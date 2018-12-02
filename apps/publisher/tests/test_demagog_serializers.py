from parameterized import parameterized

from apps.publisher.serializers import StatementDeserializer, SourcesDeserializer
from apps.publisher.tests.demagog_test_case import DemagogTestCase


class SerializersTest(DemagogTestCase):

    @parameterized.expand([
        # 1_1 is actual demagog id format, but are flexible and can accept other strings and ints as well
        [{'id': '1_1'}, {}],
        [{'id': 1}, {}],
        [{'id': '1'}, {}],
        [{'id': '1fa43de44'}, {}],
        [{'id': 'a'}, {}],
    ])
    def test_statement_deserializer__accept_valid(self, override_data, override_attributes):
        data = self.get_statement_valid_data()
        data.update(override_data)
        data['attributes'].update(override_attributes)

        deserializer = StatementDeserializer(data=data)
        self.assertTrue(deserializer.is_valid())

    @parameterized.expand([
        [{'id': None}, {}],
        [{'id': 0}, {}],
        [{'id': '0'}, {}],
        [{'id': ''}, {}],
        [{'id': ' '}, {}],
        [{'id': '1 '}, {}],
        [{'id': '1 1'}, {}],
        [{}, {'sources': ''}],
        [{}, {'sources': 'not-valid-url'}],
        [{}, {'sources': 'http://example.com/it-is-single-url-not-list'}],
        [{}, {'text': ''}],
        [{}, {'rating': ''}],
        [{}, {'rating': 'not-in-choices'}],
        [{}, {'rating_text': ''}],
        [{}, {'explanation': ''}],
        [{}, {'factchecker_uri': ''}],
        [{}, {'factchecker_uri': 'not-valid-url'}],
        [{}, {'timestamp_factcheck': ''}],
        [{}, {'timestamp_factcheck': 'not-valid-date'}],
    ])
    def test_statement_deserializer__invalid_field_value(self, override_data, override_attributes):
        data = self.get_statement_valid_data()
        data.update(override_data)
        data['attributes'].update(override_attributes)

        deserializer = StatementDeserializer(data=data)
        self.assertFalse(deserializer.is_valid())

    @parameterized.expand([
        [True, {'attributes': {'sources': []}}],
        [True, {'attributes': {'sources': [DemagogTestCase.FACT_URL, DemagogTestCase.SOURCE_URL]}}],
        [True, {'attributes': {'sources': ['not-an-url-is-still-valid-char']}}],
        [False, {'attributes': {'sources': None}}],
        [False, {'attributes': None}],
        [False, None],
    ])
    def test_sources_deserializer(self, is_valid, data):
        deserializer = SourcesDeserializer(data=data)
        self.assertEqual(deserializer.is_valid(), is_valid)
