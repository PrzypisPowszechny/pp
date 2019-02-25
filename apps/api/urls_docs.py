from django.conf.urls import url
from drf_yasg import openapi
from drf_yasg.openapi import Contact
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from apps.pp import version

yasg_schema_view = get_schema_view(
    openapi.Info(
        title="PP API",
        default_version='v{version}'.format(version=version),
        description="This is REST API for Przypis Powszechny browser-extension\n"
                    "\n"
                    "Repository of this API: https://github.com/PrzypisPowszechny/pp\n"
                    "Repository of the extension: https://github.com/PrzypisPowszechny/pp-client",
        # TODO: create our terms of service
        terms_of_service='',
        # TODO: set official contact
        contact=Contact(name='PP'),
        # TODO: what's our license??
        # license=openapi.License(name="BSD License"),
    ),
    validators=['flex', 'ssv'],
    public=True,
    permission_classes=(permissions.AllowAny,),
)

app_name = 'docs'

urlpatterns = [
    url(r'^swagger(?P<format>\.json|\.yaml)$',
        yasg_schema_view.without_ui(cache_timeout=None), name='schema_json'),
    url(r'^$',
        yasg_schema_view.with_ui('swagger', cache_timeout=None), name='schema_swagger'),
    url(r'^redoc/$',
        yasg_schema_view.with_ui('redoc', cache_timeout=None), name='schema_redoc'),
]
