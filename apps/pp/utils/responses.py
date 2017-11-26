import json

from django.http.response import HttpResponseBase, HttpResponse
from rest_framework import status

# We answer all unsuccessful requests with 400 status (bad request) that indicates the client's fault.
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

default_error_status = status.HTTP_400_BAD_REQUEST
# We answer all user-caused requests with 400status
# Policy based on http://blog.restcase.com/rest-api-error-codes-101/


class ValidationErrorResponse(Response):
    def __init__(self, errors, *args, **kwargs):
        content = [{
                       'field': field,
                       'reasons': reasons
                    }
                   for field, reasons in errors.items()]
        super().__init__(content, *args, status=HTTP_400_BAD_REQUEST, **kwargs)


# Based on http://jsonapi.org/examples/#error-objects-basics
class ErrorResponse(Response):
    def __init__(self, error=None, title=None, *args, status=default_error_status, **kwargs):
        # Error is a detailed error message
        # Title is less specific and represents a class of errors
        content = [{
            'details': error or 'No details provided'
        }]
        if title:
            content[0]['title'] = title
        super().__init__(content, *args, status=status, **kwargs)


class PermissionDenied(ErrorResponse):
    def __init__(self, *args, status=default_error_status, **kwargs):
        super().__init__(*args, title='Permission Denied', status=status, **kwargs)
