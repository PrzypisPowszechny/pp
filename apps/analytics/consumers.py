from django.conf import settings

from apps.consumers import Consumer


class GAConsumer(Consumer):

    VAR_TRACKING_ID = 'tid'
    VAR_CLIENT_ID = 'cid'
    VAR_VERSION = 'v'
    VAR_TYPE = 't'
    VAR_EVENT_CATEGORY = 'ec'
    VAR_EVENT_ACTION = 'ea'
    VAR_EVENT_LABEL = 'el'

    VAL_VERSION_1 = '1'
    VAL_TYPE_EVENT = 'event'

    api_name = 'Google Analytics'
    content_type = 'text/html'
    base_url = 'https://www.google-analytics.com'
    send_endpoint = '/collect'

    def __init__(self, cid_value, **kwargs):
        self.cid_value = cid_value
        super().__init__(**kwargs)

    def send(self, type_value, data):
        return self.post(
            endpoint_path=self.send_endpoint,
            data=dict(
                **data,
                **{
                   self.VAR_VERSION: self.VAL_VERSION_1,
                   self.VAR_CLIENT_ID: self.cid_value,
                   self.VAR_TRACKING_ID: settings.GA_TRACKING_ID,
                   self.VAR_TYPE: type_value
                }
            )
        )

    def send_event(self, category, action, label):
        return self.send(type_value=self.VAL_TYPE_EVENT, data={
            self.VAR_EVENT_CATEGORY: category,
            self.VAR_EVENT_ACTION: action,
            self.VAR_EVENT_LABEL: label
        })

    def send_event_extension_uninstalled(self):
        return self.send_event(category='Extension', action='Uninstall', label='ExtensionUninstalled')
