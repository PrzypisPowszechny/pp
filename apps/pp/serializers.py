from .models import Reference, UserReferenceFeedback, User
from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.fields import empty


class ReferenceListGETSerializer(serializers.ModelSerializer):
    useful_count = serializers.IntegerField(default=0, read_only=True)
    objection_count = serializers.IntegerField(default=0, read_only=True)
    useful = serializers.BooleanField(default=False, read_only=True)
    objection = serializers.BooleanField(default=False, read_only=True)

    class Meta:
        model = Reference
        fields = ('id', 'url', 'ranges', 'quote', 'priority', 'link', 'link_title',
                  'useful', 'useful_count',
                  'objection', 'objection_count'
                  )


class ReferenceGETSerializer(serializers.ModelSerializer):
    useful_count = serializers.SerializerMethodField()
    objection_count = serializers.SerializerMethodField()
    useful = serializers.SerializerMethodField('is_useful')
    objection = serializers.SerializerMethodField('is_objection')

    class Meta:
        model = Reference
        fields = ('id', 'url', 'ranges', 'quote', 'priority', 'link', 'link_title',
                  'useful', 'useful_count',
                  'objection', 'objection_count'
                  )

    def __init__(self, instance=None, data=empty, *args, **kwargs):
        if 'context' not in kwargs:
            raise ValueError('No context provided for ReferenceGETSerializer')

        self.user = kwargs['context']['request'].user
        super().__init__(instance, data, *args, **kwargs)

    def get_useful_count(self, instance):
        return UserReferenceFeedback.objects.filter(user=self.user, reference=instance, useful=True).count()

    def get_objection_count(self, instance):
        return UserReferenceFeedback.objects.filter(user=self.user, reference=instance, objection=True).count()

    def is_useful(self, instance):
        return UserReferenceFeedback.objects.filter(user=self.user, reference=instance, useful=True).exists()

    def is_objection(self, instance):
        return UserReferenceFeedback.objects.filter(user=self.user, reference=instance, objection=True).exists()


class ReferencePOSTSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reference
        fields = ('user', 'url', 'ranges', 'quote', 'priority', 'link', 'link_title')


class ReferencePATCHSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reference
        fields = ('quote', 'priority', 'link', 'link_title')
