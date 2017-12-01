from django.conf.urls import url, include

from .views import references, reference_reports, reference_usefuls, reference_objections

reference_urls = [
    url(r'^(?P<reference_id>[0-9]+)/$', references.ReferenceDetail.as_view()),
    url(r'^$', references.ReferencePOST.as_view()),
    url(r'^search/', references.ReferenceList.as_view()),

    url(r'^(?P<reference_id>[0-9]+)/reference_reports/$', reference_reports.ReferenceReportPOST.as_view()),

    url(r'^(?P<reference_id>[0-9]+)/reference_usefuls/$', reference_usefuls.ReferenceUsefulChange.as_view()),
    url(r'^(?P<reference_id>[0-9]+)/reference_objections/$', reference_objections.ReferenceObjectionChange.as_view()),
]

urlpatterns = [
    url(r'^references/', include(reference_urls))
]
