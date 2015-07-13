from django.contrib.auth.models import User

from ghost.test.testcases import LiveServerTestCase
from nose.plugins.attrib import attr


@attr('views')
class LandingPageTestCase(LiveServerTestCase):
    """
    Tests Django's landing page.
    """
    wait_timeout = 10

    PASSWORD = 'foo'

    def test_default_page(self):
        """
        Default page shows the right content to an anonymous user.
        """
        # Open the main uri.
        page, resources = self.open('/')
        # This should return a 200 status code.
        self.assertEqual(page.http_status, 200)
        # Check if the title is correct.
        text, resources = self.ghost.evaluate('document.querySelector(".title").innerHTML')
        self.assertEqual(text, 'Hello, twisted world.')

    def test_login_flow(self):
        """
        Logged in users see a correct welcome message.
        """
        # Shortcut login method if you don't want to test the login process
        # itself.
        user = User.objects.create_user('john', 'john@foo.bar', self.PASSWORD)
        self.set_session_cookie(user.username, self.PASSWORD)
        page, resources = self.open('/')
        text, resources = self.ghost.evaluate('document.querySelector(".welcome").innerHTML')
        self.assertTrue('Welcome, john' in text)
