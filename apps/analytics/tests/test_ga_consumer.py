from urllib.parse import parse_qs

import responses
from django.test import TestCase, override_settings
from model_mommy import mommy

from ..consumers import GAConsumer


def unlist_single_values(qs_dict):
    return {k: v if len(v) > 1 else v[0] for k, v in qs_dict.items()}


class GAConsumerTest(TestCase):
    maxDiff = None

    ga_response = responses.Response(
        method='POST',
        url="{}{}".format(GAConsumer.base_url, GAConsumer.send_endpoint),
        content_type='text/html',
        match_querystring=True,
        body=''
    )

    def setUp(self):
        pass

    def get_cid(self):
        return str(mommy.random_gen.gen_integer(0))

    @responses.activate
    def test_send(self):
        type_ = mommy.random_gen.gen_string(5)
        data_var = mommy.random_gen.gen_string(5)
        data_var_val = mommy.random_gen.gen_string(5)
        data = {data_var: data_var_val}
        cid = self.get_cid()
        tid = mommy.random_gen.gen_string(10)

        responses.add(self.ga_response)

        with override_settings(GA_TRACKING_ID=tid):
            GAConsumer(cid).send(type_value=type_, data=data)
            rsps_call = responses.calls[-1]

            self.assertEqual(rsps_call.response.status_code, 200)

            request_all_params = unlist_single_values(parse_qs(rsps_call.request.body))
            self.assertDictContainsSubset({
                GAConsumer.VAR_TYPE: type_,
                GAConsumer.VAR_VERSION: GAConsumer.VAL_VERSION_1,
                GAConsumer.VAR_CLIENT_ID: cid,
                data_var: data_var_val,
                GAConsumer.VAR_TRACKING_ID: tid
            }, request_all_params)

    @responses.activate
    def test_send_event(self):
        category = mommy.random_gen.gen_string(10)
        action = mommy.random_gen.gen_string(10)
        label = mommy.random_gen.gen_string(20)

        responses.add(self.ga_response)

        GAConsumer(self.get_cid()).send_event(category=category, action=action, label=label)
        rsps_call = responses.calls[-1]

        self.assertEqual(rsps_call.response.status_code, 200)

        request_all_params = unlist_single_values(parse_qs(rsps_call.request.body))
        self.assertDictContainsSubset({
            GAConsumer.VAR_TYPE: GAConsumer.VAL_TYPE_EVENT,
            GAConsumer.VAR_EVENT_CATEGORY: category,
            GAConsumer.VAR_EVENT_ACTION: action,
            GAConsumer.VAR_EVENT_LABEL: label,
        }, request_all_params)

    @responses.activate
    def test_send_event_extension_uninstalled(self):
        responses.add(self.ga_response)

        GAConsumer(self.get_cid()).send_event_extension_uninstalled()
        rsps_call = responses.calls[-1]

        self.assertEqual(rsps_call.response.status_code, 200)

        request_all_params = unlist_single_values(parse_qs(rsps_call.request.body))
        self.assertDictContainsSubset({
            GAConsumer.VAR_EVENT_CATEGORY: 'Extension',
            GAConsumer.VAR_EVENT_ACTION: 'Uninstall',
            GAConsumer.VAR_EVENT_LABEL: 'ExtensionUninstalled',
        }, request_all_params)
