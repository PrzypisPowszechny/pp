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
from django.conf.urls import url

from apps.analytics import views as analytics_views
from apps.site import views as site_views


app_name = 'site'

urlpatterns = [
    # Analytics
    url(r'^extension-uninstalled/$', analytics_views.extension_uninstalled_hook),
    url(r'^pings/init/$', analytics_views.init_ping),
    url(r'^iamstaff/$', analytics_views.set_iamstaff),

    # Other site pages
    url(r'^site_test/', site_views.site_test_index, name='site_test'),
    url(r'^report/$', site_views.report_form),
    url(r'^about/$', site_views.about),
    url(r'^social-login-demo/$', site_views.social_login_demo),
    url(r'^annotation_request_unsubscribe/(?P<annotation_request_id>[0-9]+)/(?P<token>[\w.:\-_=]+)/$',
        site_views.annotation_request_unsubscribe, name='annotation_request_unsubscribe'),
]
