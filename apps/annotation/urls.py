from django.conf.urls import url, include
from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.annotation.views import users, annotation_requests
from .views import annotations, annotation_reports, annotation_upvotes

app_name = 'annotation'

upvotes_router = DefaultRouter(trailing_slash=False)
upvotes_router.register('annotationUpvotes', annotation_upvotes.AnnotationUpvote)


urlpatterns = [
    url(r'^annotations', include([
        url(r'^/(?P<annotation_id>[0-9]+)$', annotations.AnnotationSingle.as_view(),
            name='annotation'),
        url(r'^$', annotations.AnnotationList.as_view(),
            name='annotation'),
        # Related
        url(r'^/(?P<annotation_id>[0-9]+)/user$', users.AnnotationRelatedUserSingle.as_view(),
            name='annotation_related_user'),
        path('/<int:annotation_id>/upvote', annotation_upvotes.AnnotationRelatedAnnotationUpvote.as_view(),
             name='annotation_related_upvote'),
    ])),
    url(r'^annotationReports', include([
        url(r'^$', annotation_reports.AnnotationReportList.as_view(),
            name='annotation_report'),
    ])),
    url(r'^annotationRequests', include([
        url(r'^$', annotation_requests.AnnotationRequestList.as_view(),
            name='annotation_requests'),
        url(r'^/(?P<annotation_request_id>[0-9]+)$', annotation_requests.AnnotationRequestSingle.as_view(),
            name='annotation_requests'),
    ])),
    url(r'^users/', include([
        url(r'^(?P<user_id>[0-9]+)$', users.UserSingle.as_view(),
            name='user'),
    ])),
] + upvotes_router.urls

