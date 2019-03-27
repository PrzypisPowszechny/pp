from django.urls import path, include

from .views import FacebookLogin, GoogleLogin, TokenRefreshView, TokenVerifyView, UserDetailView

app_name = 'api_auth'

urlpatterns = [
    path('auth/', include([
        path('facebook/', FacebookLogin.as_view(), name='facebook'),
        path('google/', GoogleLogin.as_view()),
        path('refresh/', TokenRefreshView.as_view()),
        path('verify/', TokenVerifyView.as_view()),
    ])),
    path('users/<int:user_id>', UserDetailView.as_view())
]
