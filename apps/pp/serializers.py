from .models import Reference
from rest_framework import serializers


class ReferenceSerialzer(serializers.ModelSerializer):
    class Meta:
        model = Reference
        fields = ('id', 'url', 'range', 'quote', 'priority', 'link', 'link_title', 'reference_request_id',
                  'useful_count', 'objection_count')
