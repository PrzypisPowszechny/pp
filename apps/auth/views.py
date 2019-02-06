from allauth.account.utils import perform_login
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount import app_settings as socialaccount_settings
from rest_auth.registration import views as rest_auth_views


class LoginView(rest_auth_views.LoginView):
    def process_login(self):
        """
        Process login using allauth complete tool, that calls all signals and might trigger mails.
        It replaces default "shortcut" behaviour by django_rest_auth that evades it and calls django login directly.
        """
        perform_login(self.request, self.user, socialaccount_settings.EMAIL_VERIFICATION)


class SocialLoginView(rest_auth_views.SocialLoginView):
    def process_login(self):
        """
        SocialLoginView serializer's validation triggers perform_login,
        so we clean this hook to avoid duplicating signals etc.
        """
        pass


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
