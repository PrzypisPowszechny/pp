from django.conf.urls import url, include
from .views import references
from .views import reference_reports

reference_urls = [
    url(r'^(?P<pk>[0-9]+)/$', references.ReferenceDetail.as_view(), name='get_view'),
    url(r'^$', references.ReferencePOST.as_view(), name='post_view'),
    url(r'^search/', references.ReferenceList.as_view(), name='search_view'),

    url(r'^(?P<reference_id>[0-9]+)/reference_reports/$', reference_reports.ReferenceReportPOST.as_view(),
        name='post_view'),
]

urlpatterns = [
    url(r'^references/', include(reference_urls))
]
