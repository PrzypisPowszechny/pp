from rest_framework import generics

from apps.annotation import serializers


class AnnotationReportCreateView(generics.CreateAPIView):
    serializer_class = serializers.AnnotationReportSerializer
