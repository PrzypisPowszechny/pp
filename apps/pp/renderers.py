from rest_framework import renderers


class JSONAPIRenderer(renderers.JSONRenderer):
    media_type = 'application/vnd.api+json'
    format = 'vnd.api+json'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get('response', None)
        if response is not None and response.status_code == 204:
            data = None
        elif data is None:
            data = {'data': None}
        # One of those MUST be in valid response, so if it isn't we assume data var is actual val of data key
        elif 'data' not in data and 'errors' not in data and 'meta' not in data:
            data = {'data': data}

        # Pagination case: response consists of results, meta and links, just replace results key with data
        if 'results' in data:
            data['data'] = data.pop('results')

        return super().render(data, accepted_media_type, renderer_context)
