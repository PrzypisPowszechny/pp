from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_json_api.relations import ResourceRelatedField

from apps.pp.models import ReferenceReport
from apps.pp.models import ReferenceRequest
from .models import Reference, UserReferenceFeedback, User
from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.fields import empty



def wrap_data(serializer_class):
    return type('Data%s' % serializer_class.__name__, (serializers.Serializer,), {'data': serializer_class()})


def new_serializer(name, **kwargs):
    return type('Nested%s' % name, (serializers.Serializer,), kwargs)()


class ReferenceAttributesQueryJerializer(serializers.ModelSerializer):
    comment = serializers.CharField(required=False)

    class Meta:
        model = Reference
        fields = ('url', 'ranges', 'quote',
                  'priority', 'comment', 'reference_link', 'reference_link_title')


class ReferenceAttributesJerializer(ReferenceAttributesQueryJerializer):
    useful_count = serializers.SerializerMethodField()
    objection_count = serializers.SerializerMethodField()
    useful = serializers.SerializerMethodField('is_useful')
    objection = serializers.SerializerMethodField('is_objection')
    does_belong_to_user = serializers.SerializerMethodField()

    class Meta:
        model = ReferenceAttributesQueryJerializer.Meta.model
        fields = ReferenceAttributesQueryJerializer.Meta.fields + (
                  'useful', 'useful_count', 'objection', 'objection_count',
                  'does_belong_to_user',
                  )
        read_only_fields = ('useful', 'useful_count', 'objection', 'objection_count',
                            'does_belong_to_user')

    def __init__(self, instance=None, data=empty, *args, **kwargs):
        if settings.DEBUG:
            # Allow mocking data in development to enable introspection of serializer
            self.user = User()
            super().__init__(instance, data, **kwargs)
            return
        if 'context' not in kwargs:
            raise ValueError('No context provided for ReferenceSerializer')
        self.user = self.request.user
        super().__init__(instance, data, **kwargs)

    def get_useful_count(self, instance):
        return UserReferenceFeedback.objects.filter(user=self.user, reference=instance, useful=True).count()

    def get_objection_count(self, instance):
        return UserReferenceFeedback.objects.filter(user=self.user, reference=instance, objection=True).count()

    def is_useful(self, instance):
        return UserReferenceFeedback.objects.filter(user=self.user, reference=instance, useful=True).exists()

    def is_objection(self, instance):
        return UserReferenceFeedback.objects.filter(user=self.user, reference=instance, objection=True).exists()

    def get_does_belong_to_user(self, instance):
        return self.user.id == instance.user_id


class RequestReferenceRelationSerializer(serializers.Serializer):
    data = new_serializer(
        'RequestReferenceData',
        type=serializers.CharField(),
        id=serializers.IntegerField()
    )


class UserRelationSerializer(serializers.Serializer):
    data = new_serializer(
        'UserData',
        type=serializers.CharField(),
        id=serializers.IntegerField()
    )


class ReferenceRelationshipsQueryJerializer(serializers.Serializer):
    reference_request = RequestReferenceRelationSerializer(required=False, allow_null=True)


class ReferenceRelationshipsJerializer(ReferenceRelationshipsQueryJerializer):
    user = UserRelationSerializer()


class ReferenceQueryJerializer(serializers.Serializer):
    id = serializers.IntegerField()
    type = serializers.CharField()
    attributes = ReferenceAttributesQueryJerializer()
    relationships = ReferenceRelationshipsQueryJerializer(required=False)


class ReferenceJerializer(ReferenceQueryJerializer):
    attributes = ReferenceAttributesJerializer()
    relationships = ReferenceRelationshipsJerializer()


class ReferenceListGETSerializer(serializers.ModelSerializer):
    useful_count = serializers.IntegerField(default=0)
    objection_count = serializers.IntegerField(default=0)
    useful = serializers.BooleanField(default=False)
    objection = serializers.BooleanField(default=False)
    does_belong_to_user = serializers.BooleanField(default=False)

    class Meta:
        model = Reference
        fields = ('url', 'ranges', 'quote',
                  'priority', 'comment', 'reference_link', 'reference_link_title',
                  'useful', 'useful_count', 'objection', 'objection_count',
                  'does_belong_to_user',
                  # relationships:
                  'user', 'reference_request'
                  )
        read_only_fields = ('useful', 'useful_count', 'objection', 'objection_count',
                            'does_belong_to_user')


class ReferenceQuerySerializer(serializers.ModelSerializer):

    class Meta:
        model = Reference
        fields = ('url', 'ranges', 'quote',
                  'priority', 'comment', 'reference_link', 'reference_link_title',
                  # relationships:
                  'reference_request',
                  )


class ReferenceSerializer(ReferenceQuerySerializer):
    reference_request = serializers.PrimaryKeyRelatedField(read_only=True, required=False, allow_null=True)

    useful_count = serializers.SerializerMethodField()
    objection_count = serializers.SerializerMethodField()
    useful = serializers.SerializerMethodField('is_useful')
    objection = serializers.SerializerMethodField('is_objection')
    does_belong_to_user = serializers.SerializerMethodField()

    class Meta:
        model = ReferenceQuerySerializer.Meta.model
        fields = ReferenceQuerySerializer.Meta.fields + (
                  'useful', 'useful_count', 'objection', 'objection_count',
                  'does_belong_to_user',
                  # relationships:
                  'user',
                  )
        read_only_fields = ('useful', 'useful_count', 'objection', 'objection_count',
                            'does_belong_to_user')

    def __init__(self, instance=None, data=empty, *args, **kwargs):
        if settings.DEBUG:
            # Allow mocking data in development to enable introspection of serializer
            self.user = User()
            super().__init__(instance, data, **kwargs)
            return

        if 'context' not in kwargs:
            raise ValueError('No context provided for ReferenceSerializer')
        self.user = self.request.user
        super().__init__(instance, data, **kwargs)

    def get_useful_count(self, instance):
        return UserReferenceFeedback.objects.filter(user=self.user, reference=instance, useful=True).count()

    def get_objection_count(self, instance):
        return UserReferenceFeedback.objects.filter(user=self.user, reference=instance, objection=True).count()

    def is_useful(self, instance):
        return UserReferenceFeedback.objects.filter(user=self.user, reference=instance, useful=True).exists()

    def is_objection(self, instance):
        return UserReferenceFeedback.objects.filter(user=self.user, reference=instance, objection=True).exists()

    def get_does_belong_to_user(self, instance):
        return self.user.id == instance.user_id


class ReferencePATCHSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reference
        fields = ('priority', 'comment', 'reference_link', 'reference_link_title')


class ReferenceReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferenceReport
        fields = ('reason', 'comment',
              # relationships:
              'user', 'reference'
              )