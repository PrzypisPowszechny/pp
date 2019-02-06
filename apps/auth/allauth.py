from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings


class AccountAdapter(DefaultAccountAdapter):
    def login(self, request, user):
        """
        All auth adapter that allows to switch off django session login use.
        For example when we use JWT with django_rest.
        """
        if getattr(settings, 'PP_AUTH_REST_SESSION_LOGIN', True):
            super().login(request, user)

    def get_login_redirect_url(self, request):
        if getattr(settings, 'PP_AUTH_REST_SESSION_LOGIN', True):
            return super().get_login_redirect_url(request)
