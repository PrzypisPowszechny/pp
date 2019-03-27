from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from djangorestframework_camel_case.parser import CamelCaseJSONParser
from djangorestframework_camel_case.render import CamelCaseJSONRenderer
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework import permissions, status, serializers
from rest_framework.generics import CreateAPIView
from rest_framework_simplejwt import views as jwt_views

from apps.annotation.serializers import UserSerializer
from .serializers import SocialLoginSerializer, TokenReadOnlyMixin

User = get_user_model()


@method_decorator(sensitive_post_parameters(*SocialLoginSerializer.sensitive_fields), name='dispatch')
class SocialLoginView(CreateAPIView):
    renderer_classes = (CamelCaseJSONRenderer,)
    parser_classes = (CamelCaseJSONParser,)

    permission_classes = [permissions.AllowAny]
    serializer_class = SocialLoginSerializer
    backend_name = None


class FacebookLogin(SocialLoginView):
    backend_name = 'facebook'


class GoogleLogin(SocialLoginView):
    backend_name = 'google-oauth2'


@method_decorator(swagger_auto_schema(responses={status.HTTP_201_CREATED: TokenReadOnlyMixin}), name='post')
class TokenRefreshView(jwt_views.TokenRefreshView):
    renderer_classes = (CamelCaseJSONRenderer,)
    parser_classes = (CamelCaseJSONParser,)


class TokenVerifyView(jwt_views.TokenVerifyView):
    renderer_classes = (CamelCaseJSONRenderer,)
    parser_classes = (CamelCaseJSONParser,)


class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer

    lookup_url_kwarg = 'user_id'


class AnnotationRelatedUserDetailView(UserDetailView):
    lookup_url_kwarg = 'annotation_id'
    lookup_field = 'annotation'
