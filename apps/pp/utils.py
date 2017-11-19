import json

from django.http.response import HttpResponseBase, HttpResponse


class SuccessHttpResponse(HttpResponse):
    def __init__(self, result, *args, **kwargs):
        super().__init__(*args, **kwargs)
        response = {
            'success': True,
            'result': result
        }
        data = json.dumps(response)
        self.content_type = 'application/json'
        kwargs.setdefault('content_type', 'application/json')
        super().__init__(content=data, **kwargs)


class ErrorHttpResponse(HttpResponse):
    def __init__(self, errors, *args, **kwargs):
        response = {
            'success': False,
            'errors': errors
        }
        data = json.dumps(response)
        self.content_type = 'application/json'
        kwargs.setdefault('content_type', 'application/json')
        super().__init__(content=data, **kwargs)
