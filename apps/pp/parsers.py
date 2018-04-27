from rest_framework import parsers

from .renderers import JSONAPIRenderer


class JSONAPIParser(parsers.JSONParser):
    media_type = 'application/vnd.api+json'
    renderer_class = JSONAPIRenderer

    def parse(self, *args, **kwargs):
        """
        Parses the incoming bytestream as JSON and returns the resulting data
        """
        return super().parse(*args, **kwargs).get('data')
