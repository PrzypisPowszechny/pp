from django.conf.urls import url, include

from apps.pp.views import users
from .views import annotations, annotation_reports, annotation_upvotes

# TODO: do we make annotationReports, annotation-reports or annotation_reports urls? check redux-json-api view on that
urlpatterns = [
    url(r'^annotations', include([
        url(r'^/(?P<annotation_id>[0-9]+)$', annotations.AnnotationSingle.as_view(),
            name='annotation'),
        url(r'^$', annotations.AnnotationList.as_view(),
            name='annotation'),
        # Related
        url(r'^/(?P<annotation_id>[0-9]+)/user$', users.AnnotationRelatedUserSingle.as_view(),
            name='annotation_related_user'),
        url(r'^/(?P<annotation_id>[0-9]+)/upvote$',
            annotation_upvotes.AnnotationRelatedAnnotationUpvoteSingle.as_view(),
            name='annotation_related_upvote'),
        url(r'^/(?P<annotation_id>[0-9]+)/reports$', annotation_reports.AnnotationRelatedAnnotationReportList.as_view(),
            name='annotation_related_reports'),
    ])),
    url(r'^annotation_upvotes', include([
        url(r'^/(?P<feedback_id>[0-9]+)$', annotation_upvotes.AnnotationUpvoteSingle.as_view(),
            name='annotation_upvote'),
        url(r'^$', annotation_upvotes.AnnotationUpvoteList.as_view(),
            name='annotation_upvote'),
        # Related
        url(r'^/(?P<feedback_id>[0-9]+)/annotation$', annotations.AnnotationUpvoteRelatedAnnotationSingle.as_view(),
            name='annotation_upvote_related_annotation'),
    ])),
    url(r'^annotation_reports', include([
        url(r'^/(?P<report_id>[0-9]+)$', annotation_reports.AnnotationReportSingle.as_view(),
            name='annotation_report'),
        url(r'^$', annotation_reports.AnnotationReportList.as_view(),
            name='annotation_report'),
        # Related
        url(r'^/(?P<report_id>[0-9]+)/annotation$', annotations.AnnotationReportRelatedAnnotationSingle.as_view(),
            name='annotation_report_related_annotation'),
    ])),
    url(r'^users/', include([
        url(r'^(?P<user_id>[0-9]+)$', users.UserSingle.as_view(),
            name='user'),
    ])),
]
