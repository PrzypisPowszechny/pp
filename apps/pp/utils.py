import json

from django.http.response import HttpResponseBase, HttpResponse
from rest_framework import status

# We answer all unsuccessful requests with 400 status (bad request) that indicates the client's fault.
from rest_framework.response import Response

default_error_status = status.HTTP_400_BAD_REQUEST
# We answer all successful requests with 200 status
default_success_status = status.HTTP_200_OK
# Policy based on http://blog.restcase.com/rest-api-error-codes-101/


def SuccessHttpResponse(result, *args, status=default_success_status, **kwargs):
    content = {
        'success': True,
        'data': result
    }
    # self.content_type = 'application/json'
    kwargs.setdefault('content_type', 'application/json')
    return Response(content, status=status)


def ErrorHttpResponse(errors=None, *args, status=default_error_status, **kwargs):
    content = {
        'success': False,
        'errors': errors or []
    }
    # self.content_type = 'application/json'
    kwargs.setdefault('content_type', 'application/json')
    return Response(content, status=status)


def PermissionDenied(*args, **kwargs):
    errors = [('permission', 'permission denied')]
    return Response(errors, status=status)
    #
    # super().__init__(*args, errors **kwargs)
