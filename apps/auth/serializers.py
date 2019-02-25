from django.utils.six import text_type
from requests import HTTPError
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from social_core import exceptions
from social_django.utils import load_backend, load_strategy


class TokenReadOnlyMixin(serializers.Serializer):
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)


class SocialLoginSerializer(TokenReadOnlyMixin, serializers.Serializer):
    access_token = serializers.CharField(write_only=True)
    refresh_token = serializers.CharField(write_only=True, required=False)
    expires_in = serializers.CharField(write_only=True, required=False)
    token_type = serializers.CharField(write_only=True, required=False)
    user_id = serializers.CharField(read_only=True)

    sensitive_fields = ['access_token', 'refresh_token']

    @classmethod
    def get_token(cls, user):
        refresh = RefreshToken.for_user(user)
        return {
            'access': text_type(refresh.access_token),
            'refresh': text_type(refresh),
            'user_id': user.username
        }

    def create(self, validated_data):
        return self.get_token(validated_data['user'])

    def validate(self, attrs):
        attrs = super().validate(attrs)
        request = self.context['request']

        strategy = load_strategy(request)
        backend_name = self.context['view'].backend_name
        backend = load_backend(
            strategy, backend_name, redirect_uri=None
        )

        try:
            user = backend.do_auth(attrs['access_token'], response=attrs)
        except exceptions.AuthException as e:
            raise serializers.ValidationError(str(e))
        except HTTPError:
            raise serializers.ValidationError('Request to authentication provider failed due to incorrect data')

        return {'user': user}
