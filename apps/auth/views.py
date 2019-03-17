from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework import permissions, status, serializers
from rest_framework.generics import CreateAPIView
from rest_framework import renderers as plain_renderers
from rest_framework import parsers as plain_parsers
from rest_framework_simplejwt import views as jwt_views

from apps.annotation.serializers import UserSerializer
from .serializers import SocialLoginSerializer, TokenReadOnlyMixin

User = get_user_model()


class SocialLoginView(CreateAPIView):
    renderer_classes = (plain_renderers.JSONRenderer,)
    parser_classes = (plain_parsers.JSONParser,)

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
    renderer_classes = (plain_renderers.JSONRenderer,)
    parser_classes = (plain_parsers.JSONParser,)

    @swagger_auto_schema(responses={status.HTTP_200_OK: TokenReadOnlyMixin})
    def post(self, *args, **kwargs):
        return super().post(*args, **kwargs)


class TokenVerifyView(jwt_views.TokenVerifyView):
    renderer_classes = (plain_renderers.JSONRenderer,)
    parser_classes = (plain_parsers.JSONParser,)

    @swagger_auto_schema(responses={status.HTTP_200_OK: serializers.Serializer})
    def post(self, *args, **kwargs):
        return super().post(*args, **kwargs)


class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer

    lookup_url_kwarg = 'user_id'


class AnnotationRelatedUserDetailView(UserDetailView):
    lookup_url_kwarg = 'annotation_id'
    lookup_field = 'annotation'
