from django.conf.urls import include, url

app_name = 'api'

urlpatterns = [
    url(r'^', include('apps.annotation.urls')),
    url(r'^auth/', include('apps.auth.urls')),
    url(r'^docs/', include('apps.api.urls_docs'))
]
