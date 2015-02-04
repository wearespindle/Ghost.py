from cookielib import Cookie, CookieJar
import logging
import os

from django.core import signals
from django.core.exceptions import ImproperlyConfigured
from django.db import connection, connections, close_connection
from django.test.client import Client
from django.test.testcases import LiveServerTestCase, LiveServerThread, TestCase
from django.utils.unittest import skipIf

from ghost import Ghost


@skipIf(connection.vendor != 'sqlite', 'Requires SQLite')
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
        # Prevents transaction rollback errors from the server thread.
        signals.request_finished.disconnect(close_connection)

        connections_override = {}
        for conn in connections.all():
            # If using in-memory sqlite databases, pass the connections to
            # the server thread.
            if conn.settings_dict['ENGINE'] == 'django.db.backends.sqlite3':
                # Explicitly enable thread-shareability for this connection
                conn.allow_thread_sharing = True
                connections_override[conn.alias] = conn

        # Launch the live server's thread. Use ports 9000-9200 as default range.
        specified_address = os.environ.get('DJANGO_LIVE_TEST_SERVER_ADDRESS', 'localhost:9000-9200')

        # The specified ports may be of the form '8000-8010,8080,9200-9300'
        # i.e. a comma-separated list of ports or ranges of ports, so we break
        # it down into a detailed list of all possible ports.
        possible_ports = []
        try:
            host, port_ranges = specified_address.split(':')
            for port_range in port_ranges.split(','):
                # A port range can be of either form: '8000' or '8000-8010'.
                extremes = map(int, port_range.split('-'))
                assert len(extremes) in [1, 2]
                if len(extremes) == 1:
                    # Port range of the form '8000'
                    possible_ports.append(extremes[0])
                else:
                    # Port range of the form '8000-8010'
                    for port in range(extremes[0], extremes[1] + 1):
                        possible_ports.append(port)
        except Exception:
            raise ImproperlyConfigured('Invalid address ("%s") for live server.' % specified_address)
        cls.server_thread = LiveServerThread(
            host, possible_ports, connections_override)
        cls.server_thread.daemon = True
        cls.server_thread.start()

        # Wait for the live server to be ready
        cls.server_thread.is_ready.wait()
        if cls.server_thread.error:
            raise cls.server_thread.error

        # Server is up and running, start up a Ghost instance.
        if not hasattr(cls, 'ghost'):
            cls.ghost = Ghost(display=cls.display, wait_timeout=cls.wait_timeout, log_level=cls.log_level)

    @classmethod
    def tearDownClass(cls):
        """
        Django's LiveServerTestCase tearDownClass, but without sqlite :memory
        check and shuts down the Ghost instance.
        """
        # There may not be a 'server_thread' attribute if setUpClass() for some
        # reasons has raised an exception.
        if hasattr(cls, 'server_thread'):
            # Terminate the live server's thread.
            cls.server_thread.join()

        for conn in connections.all():
            if conn.settings_dict['ENGINE'] == 'django.db.backends.sqlite3':
                conn.allow_thread_sharing = False

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
