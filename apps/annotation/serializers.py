from typing import List

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_json_api.relations import SerializerMethodResourceRelatedField
from rest_framework_json_api.serializers import ModelSerializer

from apps.annotation.consts import SUGGESTED_CORRECTION
from apps.annotation.models import AnnotationReport, AnnotationRequest
from apps.api import fields
from .models import Annotation, AnnotationUpvote


class RequestUserMixin:
    def _assert_request(self):
        assert 'request' in self.context, f"No request in context of {self.__class__.__name__}"

    @property
    def request_user(self):
        self._assert_request()
        return self.context['request'].user


class AnnotationSerializer(ModelSerializer, RequestUserMixin):
    url = fields.StandardizedRepresentationURLField()
    range = fields.ObjectField(json_internal_type=True)
    upvote_count_except_user = serializers.SerializerMethodField()
    does_belong_to_user = serializers.SerializerMethodField()
    annotation_upvote = SerializerMethodResourceRelatedField(
        model=AnnotationUpvote,
        read_only=True, source='get_user_annotation_upvote',
        related_link_view_name='api:annotation:annotation_related_upvote',
        related_link_url_kwarg='annotation_id'
    )
    self_link = serializers.HyperlinkedIdentityField(view_name='api:annotation:annotation-detail',
                                                     lookup_url_kwarg='annotation_id')

    class Meta:
        model = Annotation

        fields = (
            'id', 'user', 'url', 'range', 'quote', 'quote_context',
            'pp_category', 'demagog_category', 'comment',
            'annotation_link', 'annotation_link_title',

            'publisher', 'create_date', 'upvote_count_except_user', 'does_belong_to_user',

            'annotation_request', 'user', 'annotation_upvote',

            'self_link'
        )
        read_only_fields = (
            'demagog_category', 'publisher', 'create_date',
        )

        extra_kwargs = {
            # TODO: this will be required soon
            'quote_context': {'required': False, 'allow_blank': True},
            'comment': {'required': False, 'allow_blank': True},
            'user': {
                'read_only': True,
                'related_link_view_name': 'api:annotation:annotation_related_user',
                'related_link_url_kwarg': 'annotation_id'
            }
        }

    def get_upvote_count_except_user(self, instance):
        return instance.total_upvote_count - int(bool(self.get_user_annotation_upvote(instance)))

    def get_does_belong_to_user(self, instance):
        return self.request_user.id == instance.user_id

    def get_user_annotation_upvote(self, instance):
        # This is prefetch that results in zero or one element
        upvotes = instance.user_annotation_upvotes
        return upvotes[0] if upvotes else None


class AnnotationPatchSerializer(AnnotationSerializer):
    range = fields.ObjectField(json_internal_type=True, read_only=True)

    class Meta:
        model = Annotation
        fields = AnnotationSerializer.Meta.fields
        read_only_fields = list(set(fields) - {
            'annotation_link', 'annotation_link_title', 'comment', 'pp_category'
        })
        extra_kwargs = AnnotationSerializer.Meta.extra_kwargs


class AnnotationReportSerializer(ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = AnnotationReport
        fields = ('id', 'reason', 'comment', 'annotation', 'user')
        extra_kwargs = {
            'comment': {'required': False, 'allow_blank': True}
        }

    def validate(self, data):
        if data.get('reason') is SUGGESTED_CORRECTION and not data.get('comment'):
            raise ValidationError({
                'comment': 'Comment is required for report "%s" reason' % SUGGESTED_CORRECTION}
            )
        return data


class AnnotationUpvoteSerializer(ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = AnnotationUpvote
        fields = ('id', 'annotation', 'user')


class UserSerializer(ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'date_joined')


class AnnotationRequestSerializer(ModelSerializer, RequestUserMixin):
    url = fields.StandardizedRepresentationURLField()
    requested_by_user = serializers.SerializerMethodField()
    annotations = SerializerMethodResourceRelatedField(read_only=True, model=Annotation, source='get_annotations')

    class Meta:
        model = AnnotationRequest
        fields = (
            'id', 'url', 'quote', 'comment', 'notification_email', 'create_date', 'requested_by_user',

            'annotations'
        )
        read_only_fields = ('create_date',)

    def get_requested_by_user(self, instance) -> bool:
        return self.request_user.id == instance.user_id

    def get_annotations(self, instance) -> List[Annotation]:
        return instance.annotation_set.all()
