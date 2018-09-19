from rest_framework import serializers

from ..annotation.models import Annotation


class StatementDeserializer(serializers.Serializer):
    class Attributes(serializers.Serializer):
        source = serializers.URLField()
        text = serializers.CharField()
        date = serializers.DateTimeField()
        rating = serializers.ChoiceField(choices=[(val.lower(), label) for val, label in Annotation.DEMAGOG_CATEGORIES])
        rating_text = serializers.CharField()
        factchecker_uri = serializers.URLField()
        # Actually we do not use this field
        sclass = serializers.CharField(required=False)

    id = serializers.IntegerField()
    attributes = Attributes()


class SourcesDeserializer(serializers.Serializer):
    class Attributes(serializers.Serializer):
        sources = serializers.ListField(child=serializers.URLField())

    attributes = Attributes()
