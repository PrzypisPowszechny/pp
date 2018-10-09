from collections import namedtuple

from django.test import SimpleTestCase
from parameterized import parameterized

from apps.annotation.utils import standardize_url, standardize_url_id

JSONAPIMeta = namedtuple('JSONAPIMeta', ('resource_name',))


class StandardizeURLTest(SimpleTestCase):

    @parameterized.expand([
        # Accepts empty, returns empty
        ("",
         ""),
        # No change
        ("https://docs.python.org/",
         "https://docs.python.org/"),
        # No change
        ("http://docs.python.org/",
         "http://docs.python.org/"),
        # Add slash
        ("https://docs.python.org",
         "https://docs.python.org/"),
        # Strip fragment (anchor)
        ("https://docs.python.org/2/library/urlparse.html?a=1&b=2#urlparse-result-object",
         "https://docs.python.org/2/library/urlparse.html?a=1&b=2"),
        # Strip question mark
        ("https://docs.python.org/2/library/urlparse.html?",
         "https://docs.python.org/2/library/urlparse.html"),
        # Strip irrelevant querystring
        ("https://docs.python.org/2/library/urlparse.html?utm_campaign=buy-it&a=1",
         "https://docs.python.org/2/library/urlparse.html?a=1"),
    ])
    def test_standardize_url(self, input_url, expected_url):
        self.assertEqual(standardize_url(input_url), expected_url)


    @parameterized.expand([
        # Accepts empty, returns empty
        ("",
         ""),
        # No change
        ("docs.python.org/",
         "docs.python.org/"),
        # Remove protocol
        ("http://docs.python.org/",
         "docs.python.org/"),
        # Add slash
        ("https://docs.python.org",
         "docs.python.org/"),
        # Strip fragment (anchor)
        ("https://docs.python.org/2/library/urlparse.html?a=1&b=2#urlparse-result-object",
         "docs.python.org/2/library/urlparse.html?a=1&b=2"),
        # Strip question mark
        ("https://docs.python.org/2/library/urlparse.html?",
         "docs.python.org/2/library/urlparse.html"),
        # Strip irrelevant querystring
        ("https://docs.python.org/2/library/urlparse.html?utm_campaign=buy-it&a=1",
         "docs.python.org/2/library/urlparse.html?a=1"),
    ])
    def test_standardize_url_id(self, input_url, expected_url):
        self.assertEqual(standardize_url_id(input_url), expected_url)
