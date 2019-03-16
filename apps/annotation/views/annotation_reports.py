import rest_framework_json_api.parsers
import rest_framework_json_api.renderers
from rest_framework import generics

from apps.annotation import serializers


class AnnotationReportList(generics.CreateAPIView):
    serializer_class = serializers.AnnotationReportSerializer
    renderer_classes = [rest_framework_json_api.renderers.JSONRenderer]
    parser_classes = [rest_framework_json_api.parsers.JSONParser]
