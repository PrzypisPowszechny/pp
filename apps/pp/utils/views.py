import json

from functools import wraps
from django.http.response import HttpResponseBase, HttpResponse

# We answer all unsuccessful requests with 400 status (bad request) that indicates the client's fault.
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN
from simplejson import OrderedDict

default_error_status = HTTP_400_BAD_REQUEST
# We answer all user-caused requests with 400status
# Policy based on http://blog.restcase.com/rest-api-error-codes-101/


class JsonApiResponse(Response):
    pass


class DataResponse(JsonApiResponse):
    def __init__(self, *args, **kwargs):
        if args:
            data = args[0]
            args = args[1:]
        else:
            data = kwargs.pop('data')
        super().__init__({'data': data}, *args, **kwargs)


# Based on http://jsonapi.org/examples/#error-objects-basics
class ErrorResponse(JsonApiResponse):
    def __init__(self, error=None, title=None, *args, status=default_error_status, **kwargs):
        errors_content = kwargs.get('data', [])
        if not isinstance(errors_content, (list, tuple)):
            raise ValueError('%s expects data to be None or list of errors' % ErrorResponse.__name__)
        # Error is a detailed error message
        # Title is less specific and represents a class of errors
        error_content = [OrderedDict()]
        # Set title first as it is in that order when printing
        if title:
            error_content[0]['title'] = title
        error_content[0]['details'] = error or 'No details provided'
        super().__init__({'errors': tuple(errors_content) + tuple(error_content)}, *args, status=status, **kwargs)


class ValidationErrorResponse(ErrorResponse):
    def __init__(self, errors, *args, status=HTTP_400_BAD_REQUEST, **kwargs):
        errors_content = [{
            'source': {
                'field': field
            },
            'details': reason
        } for field, reason in errors.items()]
        super().__init__(errors_content, *args, status=status, **kwargs)


class NotFoundResponse(ErrorResponse):
    def __init__(self, *args, status=HTTP_404_NOT_FOUND, **kwargs):
        super().__init__(*args, title='Resource not found', status=status, **kwargs)


class PermissionDenied(ErrorResponse):
    def __init__(self, *args, status=HTTP_403_FORBIDDEN, **kwargs):
        super().__init__(*args, title='Permission Denied', status=status, **kwargs)


def data_wrapped_view(func):
    def wrapped(request, *args, **kwargs):
        # Reshape data without setting request.data itself witch is immutable
        data = request.data.pop('data', {})
        for k, v in data.items():
            request.data[k] = v
        response = func(request, *args, **kwargs)
        if isinstance(response, JsonApiResponse):
            return response
        if isinstance(response, (None.__class__, dict, list, tuple)):
            return DataResponse(response)
        if not hasattr(response, 'data') or not isinstance(response.data, (dict, None.__class__)):
            raise ValueError('%s requires view to return dict, list, tuple, None or response with data attribute, '
                             'got: %s' % (data_wrapped_view.__name__, response.__class__.__name__))
        response.data = {'data': response.data}
        return response
    return wraps(func)(wrapped)


def get_data_fk_value(object, fk):
    """
    A helper function that compensates a JSON-API django module quirk.
    It extract foreign key fields from request body for POST & PATCH mathods
    ...

    The relationship body is
    "relationships": {
        "related_object": {
            "id": "2"
        }
    }
    JSON-API parser parses the request body so that we receive
    ...
    "related_object": {
        "id": "2"
    }

    Before we can safely pass request body to a django_rest.serializer we need to correct it with:
    data["related_object"] = get_data_fk_value(data, "related_object")

    :param object: the data part of a JSON-API data object
    :param fk: The relationship attribute
    :return: this relationship's id value
    """
    relationship_field = object.get(fk, {})
    if isinstance(relationship_field, dict):
        return relationship_field.get('id')
    else:
        return None
