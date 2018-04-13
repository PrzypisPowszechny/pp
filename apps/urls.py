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
from rest_framework.documentation import include_docs_urls
from rest_framework import permissions
from rest_framework_swagger.views import get_swagger_view
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

import apps


yasg_schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   validators=['flex', 'ssv'],
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    url(r'^admin/',admin.site.urls),
    url(r'^api/',include('apps.pp.urls')),
    url(r'^api/docs/', include_docs_urls(title='My API title', public=False)),
    url(r'^api/docs-swagger/$', get_swagger_view(title='Pastebin API')),
    url(r'^api/docs-yasg/swagger(?P<format>\.json|\.yaml)$',
        yasg_schema_view.without_ui(cache_timeout=None), name='schema-json'),
    url(r'^api/docs-yasg/swagger/$',
        yasg_schema_view.with_ui('swagger', cache_timeout=None), name='schema-swagger-ui'),
    url(r'^api/docs-yasg/redoc/$',
        yasg_schema_view.with_ui('redoc', cache_timeout=None), name='schema-redoc'),
]
