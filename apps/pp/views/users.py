from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from lazysignup.decorators import allow_lazy_user
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.pp.responses import NotFoundResponse
from apps.pp.serializers import UserSerializer
from apps.pp.utils import DataPreSerializer

User = get_user_model()


# TODO: add test
class UserSingle(APIView):

    @swagger_auto_schema(responses={200: UserSerializer})
    @method_decorator(allow_lazy_user)
    def get(self, request, user_id):
        try:
            other_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return NotFoundResponse()

        pre_serializer = DataPreSerializer(other_user, {'attributes': other_user})
        return Response(UserSerializer(pre_serializer.data, context={'request': request}).data)


# TODO: add test
class AnnotationRelatedUserSingle(APIView):

    @swagger_auto_schema(responses={200: UserSerializer(many=True)})
    def get(self, request, annotation_id):
        try:
            other_user = User.objects.get(annotation=annotation_id, annotation__active=True)
        except User.DoesNotExist:
            return NotFoundResponse()

        pre_serializer = DataPreSerializer(other_user, {'attributes': other_user})
        return Response(UserSerializer(pre_serializer.data, context={'request': request}).data)
