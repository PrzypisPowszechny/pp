from django.conf.urls import url, include

from apps.pp.views import users
from .views import references, annotation_reports, annotation_upvotes


urlpatterns = [
    url(r'^references/', include([
        url(r'^(?P<reference_id>[0-9]+)/$', references.ReferenceSingle.as_view(),
            name='reference'),
        url(r'^$', references.ReferenceList.as_view(),
            name='reference'),
        # Related
        url(r'^(?P<reference_id>[0-9]+)/user/$', users.ReferenceRelatedUserSingle.as_view(),
            name='reference_user'),
        url(r'^(?P<reference_id>[0-9]+)/upvote/$', annotation_upvotes.ReferenceRelatedUpvoteSingle.as_view(),
            name='annotation_upvote'),
        url(r'^(?P<reference_id>[0-9]+)/reports/$', annotation_reports.ReferenceRelatedAnnotationReportList.as_view(),
            name='annotation_reports'),
    ])),
    url(r'^upvotes/', include([
        url(r'^(?P<feedback_id>[0-9]+)/$', annotation_upvotes.UpvoteSingle.as_view(),
            name='upvote'),
        url(r'^$', annotation_upvotes.UpvoteList.as_view(),
            name='upvote'),
        # Related
        url(r'^(?P<feedback_id>[0-9]+)/reference/$', references.AnnotationUpvoteRelatedReferenceSingle.as_view(),
            name='upvote_reference'),
    ])),
    # TODO: do we make annotationReports, reference-reports or annotation_reports urls? check redux-json-api view on that
    url(r'^annotation_reports/', include([
        url(r'^(?P<report_id>[0-9]+)/$', annotation_reports.AnnotationReportSingle.as_view(),
            name='annotation_report'),
        url(r'^$', annotation_reports.AnnotationReportList.as_view(),
            name='annotation_report'),
        # Related
        url(r'^(?P<report_id>[0-9]+)/reference/$', references.AnnotationReportRelatedReferenceSingle.as_view(),
            name='report_reference'),
    ])),
    url(r'^users/', include([
        url(r'^(?P<user_id>[0-9]+)/$', users.UserSingle.as_view(),
            name='user'),
    ])),
]
