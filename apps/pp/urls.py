from django.conf.urls import url, include

from .views import references, reference_reports, reference_usefuls, reference_objections

reference_urls = [
    url(r'^(?P<reference_id>[0-9]+)/$', references.ReferenceSingle.as_view(),
        name='reference'),
    url(r'^$', references.ReferenceList.as_view(),
        name='reference'),

    url(r'^(?P<reference_id>[0-9]+)/$', references.ReferenceSingle.as_view(),
        name='reference'),
    url(r'^(?P<reference_id>[0-9]+)/useful/$', reference_usefuls.ReferenceRelatedUsefulSingle.as_view(),
        name='reference_useful'),
    url(r'^(?P<reference_id>[0-9]+)/objection/$', reference_objections.ReferenceRelatedObjectionSingle.as_view(),
        name='reference_objection'),
    url(r'^(?P<reference_id>[0-9]+)/reports/$', reference_reports.ReferenceRelatedReferenceReportList.as_view(),
        name='reference_reports'),
]

urlpatterns = [
    url(r'^references/', include(reference_urls)),
    url(r'^usefuls/', include([
        url(r'^(?P<feedback_id>[0-9]+)/$', reference_usefuls.UsefulSingle.as_view(),
            name='useful'),
        url(r'^$', reference_usefuls.UsefulList.as_view(),
            name='useful'),
    ])),
    url(r'^objections/', include([
        url(r'^(?P<feedback_id>[0-9]+)/$', reference_objections.ObjectionSingle.as_view(),
            name='objection'),
        url(r'^$', reference_objections.ObjectionList.as_view(),
            name='objection'),
    ])),
    # TODO: do we make referenceReports, reference-reports or reference_reports urls? check redux-json-api view on that
    url(r'^reference_reports/', include([
        url(r'^(?P<report_id>[0-9]+)/$', reference_reports.ReferenceReportSingle.as_view(),
            name='reference_report'),
        url(r'^$', reference_reports.ReferenceReportList.as_view(),
            name='reference_report'),
    ])),
]
