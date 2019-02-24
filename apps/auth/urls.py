from django.conf.urls import url

from apps.auth.views import FacebookLogin, GoogleLogin, TokenRefreshView, TokenVerifyView


app_name = 'api_auth'

urlpatterns = [
    url(r'^facebook/$', FacebookLogin.as_view(), name='facebook'),
    url(r'^google/$', GoogleLogin.as_view()),
    url(r'^refresh/$', TokenRefreshView.as_view()),
    url(r'^verify/$', TokenVerifyView.as_view()),
]
