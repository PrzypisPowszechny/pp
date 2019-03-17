from django.urls import path

from apps.annotation.views.annotation_requests import AnnotationRequestViewSet
from apps.annotation.views.annotation_upvotes import AnnotationUpvoteViewSet
from apps.annotation.views.annotations import AnnotationViewSet
from apps.api.routers import RouterWithoutPut
from apps.auth import views as auth_views
from .views import annotation_reports, annotation_upvotes

app_name = 'annotation'

router = RouterWithoutPut(trailing_slash=False)
router.register('annotations', AnnotationViewSet)
router.register('annotationRequests', AnnotationRequestViewSet)
router.register('annotationUpvotes', AnnotationUpvoteViewSet)

urlpatterns = router.urls + [
    path('annotationReports', annotation_reports.AnnotationReportCreateView.as_view()),

    path('annotations/<int:annotation_id>/user', auth_views.AnnotationRelatedUserDetailView.as_view(),
         name='annotation_related_user'),
    path('annotations/<int:annotation_id>/upvote', annotation_upvotes.AnnotationRelatedAnnotationUpvote.as_view(),
         name='annotation_related_upvote'),
]

