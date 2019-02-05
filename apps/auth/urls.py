from django.conf.urls import url

from apps.auth.views import FacebookLogin, GoogleLogin

urlpatterns = [
    url(r'^facebook/$', FacebookLogin.as_view(), name='fb_login'),
    url(r'^google/$', GoogleLogin.as_view(), name='google_login'),
]
