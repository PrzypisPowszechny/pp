from django.conf.urls import url, include

from apps.pp.views import users
from .views import references, reference_reports, reference_upvotes


urlpatterns = [
    url(r'^references/', include([
        url(r'^(?P<reference_id>[0-9]+)/$', references.ReferenceSingle.as_view(),
            name='reference'),
        url(r'^$', references.ReferenceList.as_view(),
            name='reference'),
        # Related
        url(r'^(?P<reference_id>[0-9]+)/user/$', users.ReferenceRelatedUserSingle.as_view(),
            name='reference_user'),
        url(r'^(?P<reference_id>[0-9]+)/upvote/$', reference_upvotes.ReferenceRelatedUpvoteSingle.as_view(),
            name='reference_upvote'),
        url(r'^(?P<reference_id>[0-9]+)/reports/$', reference_reports.ReferenceRelatedReferenceReportList.as_view(),
            name='reference_reports'),
    ])),
    url(r'^upvotes/', include([
        url(r'^(?P<feedback_id>[0-9]+)/$', reference_upvotes.UpvoteSingle.as_view(),
            name='upvote'),
        url(r'^$', reference_upvotes.UpvoteList.as_view(),
            name='upvote'),
        # Related
        url(r'^(?P<feedback_id>[0-9]+)/reference/$', references.ReferenceUpvoteRelatedReferenceSingle.as_view(),
            name='upvote_reference'),
    ])),
    # TODO: do we make referenceReports, reference-reports or reference_reports urls? check redux-json-api view on that
    url(r'^reference_reports/', include([
        url(r'^(?P<report_id>[0-9]+)/$', reference_reports.ReferenceReportSingle.as_view(),
            name='reference_report'),
        url(r'^$', reference_reports.ReferenceReportList.as_view(),
            name='reference_report'),
        # Related
        url(r'^(?P<report_id>[0-9]+)/reference/$', references.ReferenceReportRelatedReferenceSingle.as_view(),
            name='report_reference'),
    ])),
    url(r'^users/', include([
        url(r'^(?P<user_id>[0-9]+)/$', users.UserSingle.as_view(),
            name='user'),
    ])),
]
