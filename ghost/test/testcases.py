from cookielib import Cookie, CookieJar
import logging
import os

from django.core import signals
from django.test.client import Client
from django.test.testcases import LiveServerTestCase, TestCase

from ghost import Ghost


class LiveServerTestCase(LiveServerTestCase, TestCase):
    """
    LiveServerTestCase using Ghost.py and transaction rollbacks.

    The sqlite connection is shared between the server thread and the main
    thread. Normally this happens only for in-memory sqlite, but this seems to
    work find with storage sqlite as well. This mat be useful with the
    REUSE_DB=1 option in Nose. Other databases like MySQL cannot easily share
    the database connection and transactions between the server thread and the
    foreground thread.
    """
    display = os.environ.get('GHOST_DISPLAY', False)
    log_level = logging.CRITICAL
    wait_timeout = 10

    def _post_teardown(self):
        """
        Modifies Ghost in-between tests; remove cookies.
        """
        super(LiveServerTestCase, self)._post_teardown()
        self.ghost.delete_cookies()
        self.ghost.clear_alert_message()

    def _pre_setup(self):
        """
        Optionally flush the database before the test and show the
        webkit window if display is enabled.
        """
        super(LiveServerTestCase, self)._pre_setup()
        if self.display:
            self.ghost.show()

    @classmethod
    def setUpClass(cls):
        """
        Django's LiveServerTestCase setupClass but without sqlite :memory check
        and with additional Ghost initialization.
        """
        default_address = os.environ.get('DJANGO_LIVE_TEST_SERVER_ADDRESS', 'localhost:8090-9000')
        os.environ['DJANGO_LIVE_TEST_SERVER_ADDRESS'] = default_address
        # Prevents transaction rollback errors from the server thread. Removed
        # as from Django 1.8.
        try:
            from django.db import close_connection
            signals.request_finished.disconnect(close_connection)
        except ImportError:
            pass
        super(LiveServerTestCase, cls).setUpClass()

        # Server is up and running, start up a Ghost instance.
        if not hasattr(cls, 'ghost'):
            try:
                cls.ghost = Ghost(display=cls.display, wait_timeout=cls.wait_timeout, log_level=cls.log_level)
            except:
                # If we fail to initialize a Ghost instance, we should
                # still clean up any daemon threads the parent
                # LiveServerTestCase made.
                super(LiveServerTestCase, cls).tearDownClass()
                raise

    @classmethod
    def tearDownClass(cls):
        """
        Django's LiveServerTestCase tearDownClass, but without sqlite :memory
        check and shuts down the Ghost instance.
        """
        super(LiveServerTestCase, cls).tearDownClass()
        cls.ghost.exit()

    def fill_form(self, form_selector, params, submit=True):
        """
        Fills in a form supplying a dict for the field names.

        Args:
        form_selector (str): A unique CSS selector to the form.
        params (dict): Dict key is the input name, the value it's value.
        submit (bool): Whether to submit the form or not, default is True.
        """
        try:
            self.ghost.fill(form_selector, params)
        except TypeError:
            # Ghost failed to fill-in all the fields, try brute-force.
            for key, value in params.items():
                try:
                    result, resources = self.ghost.set_field_value('input[name="%s"]' % key, value)
                except Exception:
                    try:
                        result, resources = self.ghost.set_field_value('textarea[name="%s"]' % key, value)
                    except Exception:
                        pass

        if submit:
            self.ghost.evaluate('document.querySelector("%s").submit()' % form_selector, expect_loading=True)

    @property
    def js_errors(self):
        """
        Check your project for javascript errors. Add the following snippet to
        your base template to make this work in tests:

        <script>
            window.__webdriver_javascript_errors = [];
            window.onerror = function(errorMsg, url, lineNumber) {
              window.__webdriver_javascript_errors.push(
                errorMsg +' (found at ' + url + ', line ' + lineNumber + ')');
            };
        </script>
        """
        errors, release_resources = self.ghost.evaluate('__webdriver_javascript_errors')
        return errors

    def open(self, path):
        """
        Simple shortcut function for self.ghost.open. Circumvents DRY for
        live_server_url.

        Args:
            path (str): The uri part of the url.
        """
        return self.ghost.open(self.live_server_url + path)

    @property
    def path(self):
        return str(self.ghost.evaluate('location.pathname+location.hash')[0])

    def set_session_cookie(self, username, password):
        """
        Sets a session with Django test client and logs Ghost in by creating
        a session cookie for it.

        Args:
            username (str): The username to login with.
            password (str): The password to login with.
        """
        client = Client(enforce_csrf_checks=False)
        self.assertEqual(client.login(username=username, password=password), True)
        sessionid = client.cookies['sessionid']
        django_cookie = Cookie(
            version=0, name='sessionid', value=sessionid.value, port=None, port_specified=False, domain='localhost',
            domain_specified=True, domain_initial_dot=False, path='/', path_specified=True, secure=False,
            expires=None, discard=True, comment=None, comment_url=None, rest=None, rfc2109=False
        )

        cj = CookieJar()
        cj.set_cookie(django_cookie)
        self.ghost.load_cookies(cj)
