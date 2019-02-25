from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status, serializers
from rest_framework.generics import CreateAPIView
from rest_framework_simplejwt import views as jwt_views

from .serializers import SocialLoginSerializer, TokenReadOnlyMixin


class SocialLoginView(CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = SocialLoginSerializer
    backend_name = None

    @method_decorator(sensitive_post_parameters(*SocialLoginSerializer.sensitive_fields))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class FacebookLogin(SocialLoginView):
    backend_name = 'facebook'


class GoogleLogin(SocialLoginView):
    backend_name = 'google-oauth2'


class TokenRefreshView(jwt_views.TokenRefreshView):

    @swagger_auto_schema(responses={status.HTTP_200_OK: TokenReadOnlyMixin})
    def post(self, *args, **kwargs):
        super().post(*args, **kwargs)


class TokenVerifyView(jwt_views.TokenVerifyView):

    @swagger_auto_schema(responses={status.HTTP_200_OK: serializers.Serializer})
    def post(self, *args, **kwargs):
        super().post(*args, **kwargs)
