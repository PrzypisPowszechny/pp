from .models import Reference, UserReferenceFeedback, User
from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.fields import empty


class ReferenceListGETSerializer(serializers.ModelSerializer):
    useful_count = serializers.IntegerField(default=0, read_only=True)
    objection_count = serializers.IntegerField(default=0, read_only=True)
    useful = serializers.BooleanField(default=False, read_only=True)
    objection = serializers.BooleanField(default=False, read_only=True)
    does_belong_to_user = serializers.BooleanField(default=False, read_only=True)

    class Meta:
        model = Reference
        fields = ('url', 'ranges', 'quote', 'priority', 'link', 'link_title',
                  'useful', 'useful_count', 'objection', 'objection_count',
                  'does_belong_to_user',
                  'reference_request'
                  )
        depth = 1




class ReferenceGETSerializer(serializers.ModelSerializer):
    useful_count = serializers.SerializerMethodField(read_only=True)
    objection_count = serializers.SerializerMethodField(read_only=True)
    useful = serializers.SerializerMethodField('is_useful', read_only=True)
    objection = serializers.SerializerMethodField('is_objection', read_only=True)
    does_belong_to_user = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Reference
        fields = ('url', 'ranges', 'quote', 'priority', 'link', 'link_title',
                  'useful', 'useful_count', 'objection', 'objection_count',
                  'does_belong_to_user',
                  'reference_request'
                  )
        depth = 1

    def __init__(self, instance=None, data=empty, *args, **kwargs):
        if 'context' not in kwargs:
            raise ValueError('No context provided for ReferenceGETSerializer')

        self.user = kwargs['context']['request'].user
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


class ReferencePOSTSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reference
        fields = ('user', 'url', 'ranges', 'quote', 'priority', 'link', 'link_title')


class ReferencePATCHSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reference
        fields = ('quote', 'priority', 'link', 'link_title')
