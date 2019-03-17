from django.conf.urls import url, include
from django.urls import path

from apps.annotation.views import users, annotation_requests
from apps.annotation.views.routers import RouterWithoutPut
from .views import annotations, annotation_reports, annotation_upvotes

app_name = 'annotation'

router = RouterWithoutPut(trailing_slash=False)
router.register('annotationUpvotes', annotation_upvotes.AnnotationUpvote)
router.register('annotations', annotations.AnnotationViewSet)


urlpatterns = [
    url(r'^annotations', include([
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
] + router.urls
