from .models import Reference, UserReferenceFeedback
from rest_framework import serializers


class ReferenceSerialzer(serializers.ModelSerializer):
    class Meta:
        model = Reference
        fields = ('id', 'url', 'range', 'quote', 'priority', 'link', 'link_title', 'reference_request_id', 'useful',
                  'useful_count', 'objection', 'objection_count')


class ReferencePOSTSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reference
        fields = ('user', 'id', 'url', 'range', 'quote', 'priority', 'link', 'link_title')


class UserReferenceFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserReferenceFeedback
        fields = ('user', 'reference', 'useful', 'objection')


class GETAPISerializer(serializers.Serializer):
    reference = ReferenceSerialzer()
