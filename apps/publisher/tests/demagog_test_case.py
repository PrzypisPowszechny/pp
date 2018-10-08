from django.test import TestCase
from django.utils import timezone


class DemagogTestCase(TestCase):
    maxDiff = None

    TEST_URL = 'http://i-test-you-all.org'
    OTHER_URL = 'http://i-dont-test-anything.org'

    SOURCE_URL = 'http://i-am-article-you-check.org'
    SOURCE_URL2 = 'http://i-am-article-you-check-n2.org'
    FACT_URL = 'http://i-check-you-all.org'

    def get_statement_valid_attrs(self):
        return {
            'source': self.SOURCE_URL,
            'text': "it's an interesting article",
            'date':  timezone.now(),
            'rating': 'true',
            'rating_text': 'true statement',
            'explanation': 'this statement is a statement that says something that is true',
            'factchecker_uri': self.FACT_URL
        }

    def get_statement_valid_data(self):
        return {
            'id': 'hash_1fa43de44',
            'attributes': self.get_statement_valid_attrs()
        }
