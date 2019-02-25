from django.http import SimpleCookie
from django.test import TestCase
from mock import patch, MagicMock
from model_mommy import mommy

from apps.analytics import ga_cookies

CID_COOKIE_PREFIX = 'GA1.2-3'


class AnalyticsViewsTEST(TestCase):
    extension_installed_url = "/site/extension-uninstalled/"
    init_ping_url = "/site/pings/init/"

    maxDiff = None

    def setUp(self):
        pass

    def test_extension_uninstalled_hook(self):
        cid = "{}.{}".format(mommy.random_gen.gen_integer(0), mommy.random_gen.gen_integer(0))
        cid_cookie_val = "{}.{}".format(CID_COOKIE_PREFIX, cid)
        self.client.cookies = SimpleCookie({ga_cookies.CID_COOKIE: cid_cookie_val})

        mocked_consumer_instance = MagicMock()
        with patch('apps.analytics.views.GAConsumer', return_value=mocked_consumer_instance) as MockGAConsumer:
            response = self.client.get(self.extension_installed_url)
            self.assertEqual(response.status_code, 200)
            MockGAConsumer.assert_called_once_with(cid)
            mocked_consumer_instance.send_event_extension_uninstalled.assert_called_once_with()

    def test_init_ping(self):
        cid = mommy.random_gen.gen_string(20)
        gid = mommy.random_gen.gen_string(20)

        response = self.client.post(self.init_ping_url, data={ga_cookies.CID_PARAM: cid, ga_cookies.GID_PARAM: gid})
        self.assertEqual(response.status_code, 200)

        cid_cookie = response.client.cookies.get(ga_cookies.CID_COOKIE)
        gid_cookie = response.client.cookies.get(ga_cookies.GID_COOKIE)
        self.assertIsNotNone(cid_cookie)
        self.assertIsNotNone(gid_cookie)
        self.assertEqual(cid_cookie.value, cid)
        self.assertEqual(gid_cookie.value, gid)
