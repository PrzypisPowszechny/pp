from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^search&url=(?P<url>.+)', views.search_view, name='search_view'),
    url(r'^(?P<pk>[0-9]+)/$', views.get_view, name='get_view')
]
