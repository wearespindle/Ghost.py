from ghost.test.testcases import LiveServerTestCase
from nose.plugins.attrib import attr


@attr('views')
class LandingPageTestCase(LiveServerTestCase):
    """
    Tests Django's landing page.
    """
    wait_timeout = 10

    def test_title(self):
        """
        The title is correct.

        As a visiting user I want to be informed about the cruelness of the
        world.
        """
        # Open the main uri.
        page, resources = self.open('/')
        # This should return a 200 status code.
        self.assertEqual(page.http_status, 200)
        # Check if the title is correct.
        text, resources = self.ghost.evaluate('document.querySelector(".title").innerHTML')
        self.assertEqual(text, 'Hello, cruel world.')
