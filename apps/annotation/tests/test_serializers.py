from django.test import TestCase
from parameterized import parameterized

from apps.annotation.serializers2 import ConstField


class SerializersTest(TestCase):

    @parameterized.expand([
        # 1_1 is actual demagog id format, but are flexible and can accept other strings and ints as well
        [{'id': '1_1'}, {}],
        [{'id': 1}, {}],
        [{'id': '1'}, {}],
        [{'id': '1fa43de44'}, {}],
        [{'id': 'a'}, {}],
    ])
    def test_statement_deserializer__accept_valid(self, override_data, override_attributes):
        # data = self.get_statement_valid_data()
        # data.update(override_data)
        # data['attributes'].update(override_attributes)
        #
        # deserializer = StatementDeserializer(data=data)
        # self.assertTrue(deserializer.is_valid())
        pass
