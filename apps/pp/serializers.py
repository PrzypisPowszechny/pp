from .models import Reference, UserReferenceFeedback, User
from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.fields import empty


class ReferenceGETSerializer(serializers.ModelSerializer):
    useful = serializers.SerializerMethodField('is_useful')
    objection = serializers.SerializerMethodField('is_objected')
    useful_var = False
    objection_var = False

    def is_useful(self, instance):
        return self.useful_var

    def is_objected(self, instance):
        return self.objection_var

    def __init__(self, instance=None, data=empty, *args, **kwargs):
        if instance != None:
            if isinstance(instance, Reference):
                instance.count_useful_and_objection()
                if 'context' in kwargs and instance != None:
                    try:
                        user = kwargs['context']['request'].user
                        print(user)
                        urf = UserReferenceFeedback.objects.get(user=user)#, reference=instance)
                        #
                        # urf = UserReferenceFeedback.objects.get(
                        #     user=User.objects.get(id=kwargs['context']['request'].user.id), reference=instance)
                        self.useful_var = urf.useful
                        self.objection_var = urf.objection
                    except ObjectDoesNotExist:
                        self.useful = False
                        self.objection = False
                else:
                    self.useful = False
                    self.objection = False
        super().__init__(instance, data, *args, **kwargs)

    class Meta:
        model = Reference
        fields = ('id', 'url', 'range', 'quote', 'priority', 'link', 'link_title', 'useful',
                  'useful_count', 'objection', 'objection_count')


class ReferencePOSTSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reference
        fields = ('user', 'url', 'range', 'quote', 'priority', 'link', 'link_title')


class ReferencePATCHSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reference
        fields = ('quote', 'priority', 'link', 'link_title')
