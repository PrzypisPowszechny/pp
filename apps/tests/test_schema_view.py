from django.test import TestCase
from django.urls import reverse

from apps.pp.tests.utils import create_test_user


class SchemaViewsTest(TestCase):

    def setUp(self):
        self.user, self.password = create_test_user()
        self.client.login(username=self.user, password=self.password)

    def test_get_schema(self):
        response = self.client.get(reverse('schema_json', args=['.json']))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('schema_json', args=['.yaml']))
        self.assertEqual(response.status_code, 200)

    def test_get_docs__swagger_ui(self):
        response = self.client.get(reverse('schema_swagger'))
        self.assertEqual(response.status_code, 200)

    def test_get_docs__redoc_ui(self):
        response = self.client.get(reverse('schema_redoc'))
        self.assertEqual(response.status_code, 200)
