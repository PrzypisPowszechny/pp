from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.annotation.serializers import UserSerializer
from apps.api.responses import NotFoundResponse

User = get_user_model()


# TODO: move those views to seperate application, it should not be part of annotation


class UserSingle(APIView):

    @swagger_auto_schema(responses={200: UserSerializer})
    def get(self, request, user_id):
        try:
            other_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return NotFoundResponse()

        return Response(UserSerializer(instance={'id': other_user, 'attributes': other_user},
                                       context={'request': request}).data)


class AnnotationRelatedUserSingle(APIView):

    @swagger_auto_schema(responses={200: UserSerializer(many=True)})
    def get(self, request, annotation_id):
        try:
            other_user = User.objects.get(annotation=annotation_id, annotation__active=True)
        except User.DoesNotExist:
            return NotFoundResponse()

        return Response(UserSerializer(instance={'id': other_user, 'attributes': other_user},
                                       context={'request': request}).data)
