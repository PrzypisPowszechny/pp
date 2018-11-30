"""pp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.http import HttpResponse
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from apps.pp import version
from apps.site import views as site_views
from apps.analytics import views as analytics_views


yasg_schema_view = get_schema_view(
    openapi.Info(
        title="PP API",
        default_version='v{version}'.format(version=version),
        description="This is REST API for Przypis Powszechny browser-extension\n"
                    "\n"
                    "Repository of this API: https://github.com/PrzypisPowszechny/pp\n"
                    "Repository of the extension: https://github.com/PrzypisPowszechny/pp-client",
        # TODO: create our terms of service
        terms_of_service=None,
        # TODO: set official contact
        contact=None,
        # TODO: what's our license??
        # license=openapi.License(name="BSD License"),
    ),
    validators=['flex', 'ssv'],
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^api/', include('apps.annotation.urls', namespace='api')),
    url(r'^api/docs/swagger(?P<format>\.json|\.yaml)$',
        yasg_schema_view.without_ui(cache_timeout=None), name='schema_json'),
    url(r'^api/docs/$',
        yasg_schema_view.with_ui('swagger', cache_timeout=None), name='schema_swagger'),
    url(r'^api/docs-redoc/$',
        yasg_schema_view.with_ui('redoc', cache_timeout=None), name='schema_redoc'),

    # Analytics
    url(r'^site/extension-uninstalled/$', analytics_views.extension_uninstalled_hook),
    url(r'^site/pings/init/$', analytics_views.init_ping),
    url(r'^site/iamstaff/$', analytics_views.set_iamstaff),

    # Other site pages
    url(r'^site_test/', site_views.site_test_index, name='site_test'),
    url(r'^site/report/$', site_views.report_form),

    # This is the challenge from cerbot (certbot.eff.org) after running "sudo certbot certonly --manual"
    url(r'^\.well-known/acme-challenge/(?P<acme>.+)$',
        lambda request, acme: HttpResponse('%s.fP2MtOMJg03pQ5U9zfjwPdFzA-12z143KjztlvCkMqc' % acme))
]
