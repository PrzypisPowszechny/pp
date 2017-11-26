from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^references/(?P<pk>[0-9]+)/$', views.ReferenceDetail.as_view(), name='get_view'),
    url(r'^references/$', views.ReferencePOST.as_view(), name='post_view'),
    url(r'^references/search/', views.ReferenceList.as_view(), name='search_view'),
]
