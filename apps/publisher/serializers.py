from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from rest_framework import serializers

from ..annotation.models import Annotation

url_validator = URLValidator()


class StatementDeserializer(serializers.Serializer):
    class Attributes(serializers.Serializer):
        sources = serializers.ListField(child=serializers.URLField(), allow_empty=False)
        text = serializers.CharField()
        timestamp_factcheck = serializers.DateTimeField()
        rating = serializers.ChoiceField(choices=[(val.lower(), label) for val, label in Annotation.DEMAGOG_CATEGORIES])
        rating_text = serializers.CharField()
        factchecker_uri = serializers.URLField()
        explanation = serializers.CharField()
        # Actually we do not use this field
        person_name = serializers.CharField(required=False, allow_null=True)

    # Accept valid integer int (not 0) or alphanumeric id (numbers, chars, underscores, without spaces)
    id = serializers.RegexField('^(?:[1-9a-zA-Z]|\d{2,}|[a-zA-Z0-9_]{2,})$', trim_whitespace=False)
    attributes = Attributes()


class SourcesDeserializer(serializers.Serializer):
    class Attributes(serializers.Serializer):
        sources = serializers.ListField(child=serializers.CharField())

    attributes = Attributes()


def split_valid_urls(urls_list):
    valid_urls, invalid_urls = [], []
    for url in urls_list:
        try:
            url_validator(url)
        except ValidationError:
            invalid_urls.append(url)
        else:
            valid_urls.append(url)
    return valid_urls, invalid_urls
