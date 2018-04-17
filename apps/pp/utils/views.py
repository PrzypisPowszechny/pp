from functools import wraps

from rest_framework  import parsers
from rest_framework import renderers
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN
from simplejson import OrderedDict

# We answer all user-caused requests with 400status
# Policy based on http://blog.restcase.com/rest-api-error-codes-101/
default_error_status = HTTP_400_BAD_REQUEST


class JsonApiResponse(Response):
    """
    Inherit from that class when creating new JSON API compliant `Response` type
    """
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
    def __init__(self, error_details=None, error_title=None,
                 *args, status=default_error_status, **kwargs):
        """
        :param error_details: detailed error message
        :param error_title: less specific and represents a class of errors
        """
        errors_content = kwargs.pop('data', [])
        if not isinstance(errors_content, (list, tuple)):
            raise ValueError('%s expects data to be None or list of errors' % ErrorResponse.__name__)
        if error_title or error_details:
            error_content = OrderedDict()
            # Set title first to appear on the top when printing
            if error_title:
                error_content['title'] = error_title
            error_content['details'] = error_details or 'No details provided'
            errors_content = tuple(errors_content) + (error_content,)
        super().__init__({'errors': errors_content}, *args, status=status, **kwargs)


class ValidationErrorResponse(ErrorResponse):
    def __init__(self, errors, *args, status=HTTP_400_BAD_REQUEST, **kwargs):
        """
        Flatten errors and format to source-reason dicts.

        From structure below:
            {'attributes': {
                'url': ["This field is required"]
            },
             'relationships': {
                'user': {
                    'data': {
                        'id': ["A valid integer is required.",
                               "This field is required",]
                    }
                }
            }}
        to such structure like that:
            [{'source': {
                'pointer': 'attributes/url'
            },
                'reason': ["This field is required"]
            }, {
                'source': {
                    'pointer': 'relationships/user/data/id'
                },
                'reason': ["A valid integer is required.",
                           "This field is required"]
            }]
        """
        nested_errors = [(('', field), reason) for field, reason in errors.items()]
        errors_content = []
        while nested_errors:
            field_path, reason = nested_errors.pop(0)
            if isinstance(reason, dict):
                for subfield, subreason in reason.items():
                    nested_errors.append((field_path + (subfield,), subreason))
            else:
                errors_content.append({
                    'source': {
                        'pointer': '/'.join(field_path)
                    },
                    'details': reason
                })
        super().__init__(*args, data=errors_content, status=status, **kwargs)


class NotFoundResponse(ErrorResponse):
    def __init__(self, *args, status=HTTP_404_NOT_FOUND, **kwargs):
        super().__init__(*args, error_title='Resource not found', status=status, **kwargs)


class PermissionDenied(ErrorResponse):
    def __init__(self, *args, status=HTTP_403_FORBIDDEN, **kwargs):
        super().__init__(*args, error_title='Permission Denied', status=status, **kwargs)


class JSONRenderer(renderers.JSONRenderer):
    media_type = 'application/vnd.api+json'
    format = 'vnd.api+json'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get('response', None)
        if response is not None and response.status_code == 204:
            data = None
        elif data is None or ('data' not in data and 'errors' not in 'data'):
            data = {'data': data}
        return super().render(data, accepted_media_type, renderer_context)


class JSONParser(parsers.JSONParser):
    media_type = 'application/vnd.api+json'
    renderer_class = JSONRenderer

    def parse(self, *args, **kwargs):
        """
        Parses the incoming bytestream as JSON and returns the resulting data
        """
        return super().parse(*args, **kwargs).get('data')
