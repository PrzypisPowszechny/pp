from django.conf.urls import url, include

from .views import references, reference_reports, reference_usefuls, reference_objections

reference_urls = [
    url(r'^(?P<reference_id>[0-9]+)/$', references.ReferenceDetail.as_view(),
        name='reference'),
    url(r'^$', references.ReferenceList.as_view(),
        name='reference'),

    url(r'^(?P<reference_id>[0-9]+)/$', references.ReferenceDetail.as_view(),
        name='reference'),
    url(r'^(?P<reference_id>[0-9]+)/reports/$', reference_reports.ReferenceReportPOST.as_view(),
        name='reference_reports'),
    url(r'^(?P<reference_id>[0-9]+)/useful/$', reference_usefuls.ReferenceUsefulChange.as_view(),
        name='reference_useful'),
    url(r'^(?P<reference_id>[0-9]+)/objection/$', reference_objections.ReferenceObjectionChange.as_view(),
        name='reference_objection'),
]

urlpatterns = [
    url(r'^references/', include(reference_urls)),
    url(r'^usefuls/', include([
        url(r'^(?P<useful_id>[0-9]+)/$', reference_usefuls.Useful.as_view(),
            name='useful'),
        url(r'^$', reference_usefuls.UsefulList.as_view(),
            name='useful'),
    ])),
]
