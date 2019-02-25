from django.test import TestCase
from django.urls import reverse


class SchemaViewsTest(TestCase):
    def test_get_schema(self):
        response = self.client.get(reverse('api:docs:schema_json', args=['.json']))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('api:docs:schema_json', args=['.yaml']))
        self.assertEqual(response.status_code, 200)

    def test_get_docs__swagger_ui(self):
        response = self.client.get(reverse('api:docs:schema_swagger'))
        self.assertEqual(response.status_code, 200)

    def test_get_docs__redoc_ui(self):
        response = self.client.get(reverse('api:docs:schema_redoc'))
        self.assertEqual(response.status_code, 200)
