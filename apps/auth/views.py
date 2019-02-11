from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from rest_framework.generics import CreateAPIView
from rest_framework import permissions

from apps.auth.serializers import SocialLoginSerializer


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
