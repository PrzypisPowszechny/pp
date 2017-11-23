import json

from django.http.response import HttpResponseBase, HttpResponse
from rest_framework import status

# We answer all unsuccessful requests with 400 status (bad request) that indicates the client's fault.
default_error_status = status.HTTP_400_BAD_REQUEST
# We answer all successful requests with 200 status
default_success_status = status.HTTP_200_OK
# Policy based on http://blog.restcase.com/rest-api-error-codes-101/


class SuccessHttpResponse(HttpResponse):
    def __init__(self, result, *args, status=default_success_status, **kwargs):
        super().__init__(*args, **kwargs)
        response = {
            'success': True,
            'data': result
        }
        data = json.dumps(response)
        self.content_type = 'application/json'
        kwargs.setdefault('content_type', 'application/json')
        super().__init__(content=data, **kwargs)

class ErrorHttpResponse(HttpResponse):
    def __init__(self, errors, *args, status=default_error_status, **kwargs):
        response = {
            'success': False,
            'errors': errors or []
        }
        data = json.dumps(response)
        self.content_type = 'application/json'
        kwargs.setdefault('content_type', 'application/json')
        super().__init__(content=data, **kwargs)
