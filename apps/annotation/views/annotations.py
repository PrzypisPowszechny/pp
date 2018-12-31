from django.apps import apps
from django.conf import settings
from django.core.signing import Signer
from django.db.models import Prefetch, Count
from django.urls import reverse
from django.utils.decorators import method_decorator
import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework.filters import OrderingFilter
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_json_api.pagination import LimitOffsetPagination

from apps.annotation.filters import StandardizedURLFilterBackend, ConflictingFilterValueError, ListORFilter
from apps.annotation.mailgun import send_mail, MailSendException
from apps.annotation.models import Annotation, AnnotationUpvote, AnnotationReport, AnnotationRequest
from apps.annotation.responses import PermissionDenied, ValidationErrorResponse, ErrorResponse, NotFoundResponse, \
    Forbidden
from apps.annotation.serializers import AnnotationPatchDeserializer, AnnotationListSerializer, AnnotationDeserializer, \
    AnnotationSerializer
from apps.annotation.utils import get_resource_name, DataPreSerializer
from apps.annotation.views.decorators import allow_lazy_user_smart

import logging
logger = logging.getLogger('pp.annotation')

class AnnotationBase(object):
    def get_pre_serialized_annotation(self, annotation, feedback=None, reports=()):
        pre_serializer = DataPreSerializer(annotation, {'attributes': annotation})
        pre_serializer.set_relation(get_resource_name(annotation.user),
                                    resource_id=annotation.user_id)
        pre_serializer.set_relation(get_resource_name(feedback, model=AnnotationUpvote),
                                    resource_id=feedback)
        pre_serializer.set_relation(get_resource_name(annotation, related_field='annotation_reports'),
                                    resource_id=reports)
        return pre_serializer.data


class AnnotationSingle(AnnotationBase, APIView):
    resource_name = 'annotations'

    @swagger_auto_schema(responses={200: AnnotationSerializer})
    @method_decorator(allow_lazy_user_smart)
    def get(self, request, annotation_id):
        try:
            annotation = Annotation.objects.get(active=True, id=annotation_id)
            feedback = AnnotationUpvote.objects.filter(annotation=annotation, user=request.user).first()
            reports = AnnotationReport.objects.filter(annotation_id=annotation.id, user=request.user)
        except (AnnotationUpvote.DoesNotExist, Annotation.DoesNotExist):
            return NotFoundResponse()
        return Response(AnnotationSerializer(instance=self.get_pre_serialized_annotation(annotation, feedback, reports),
                                             context={'request': request}).data)

    @swagger_auto_schema(request_body=AnnotationPatchDeserializer,
                         responses={200: AnnotationSerializer})
    @method_decorator(allow_lazy_user_smart)
    def patch(self, request, annotation_id):
        try:
            annotation = Annotation.objects.get(active=True, id=annotation_id)
        except Annotation.DoesNotExist:
            return NotFoundResponse()
        # Check permissions
        if annotation.user_id != request.user.id:
            return PermissionDenied()
        deserializer = AnnotationPatchDeserializer(data=request.data, context={'request': request}, partial=True)
        if not deserializer.is_valid():
            return ValidationErrorResponse(deserializer.errors)
        if 'relationships' in request.data:
            return Forbidden(error_details='Updating relationships not supported')

        patched_data = deserializer.validated_data.get('attributes', {})
        if not patched_data:
            return ErrorResponse()
        for k, v in patched_data.items():
            setattr(annotation, k, v)
        annotation.save()

        feedback = AnnotationUpvote.objects.filter(annotation=annotation, user=request.user).first()
        reports = AnnotationReport.objects.filter(annotation_id=annotation.id, user=request.user)

        return Response(AnnotationSerializer(instance=self.get_pre_serialized_annotation(annotation, feedback, reports),
                                             context={'request': request}).data)

    @method_decorator(allow_lazy_user_smart)
    def delete(self, request, annotation_id):
        try:
            annotation = Annotation.objects.get(id=annotation_id)
        except Annotation.DoesNotExist:
            return NotFoundResponse()

        # Check permissions
        if annotation.user_id != request.user.id:
            return PermissionDenied()

        if annotation.active:
            annotation.active = False
            annotation.save()
        return Response()


class AnnotationListFilter(django_filters.FilterSet):
    check_status = ListORFilter(field_name='check_status')

    class Meta:
        model = apps.get_model('annotation.Annotation')
        fields = ['check_status']


class AnnotationList(AnnotationBase, GenericAPIView):
    resource_name = 'annotations'
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, DjangoFilterBackend, StandardizedURLFilterBackend)
    ordering_fields = ('create_date', 'id')
    ordering = "-create_date"
    filter_class = AnnotationListFilter

    @staticmethod
    def notify_subscribers(url, annotation_requests):
        notification_emails = []
        recipient_variables = {}
        for instance in annotation_requests:
            if instance.notification_email:
                notification_emails.append((instance.notification_email, None))
                token = Signer().sign(instance.id).split(':')[1]
                unsubscribe_reverse = reverse('annotation_request_unsubscribe',
                                           kwargs={'annotation_request_id': instance.id, 'token': token}
                                           )
                unsubscribe_link = '{}{}'.format(settings.HOST, unsubscribe_reverse)
                recipient_variables[instance.notification_email] = {'unsubscribe_link': unsubscribe_link}
        if not notification_emails:
            return

        # TODO: format as HTML
        subject = 'Dodano przypis na stronie, na którą czytałeś'
        text = '''
                Hej,
                Ostatnio skorzystałeś z "poproś o przypis" na stronie {}.
                Właśnie ktoś dodał na niej przypis. Możliwe, że odpowiada na Twoje zgłoszenie!
                Sprawdź!
                {}
                By zrezygnować z subskrypcji, wejdź tutaj: %recipient.unsubscribe_link%
                        '''.format(url, url)

        try:
            send_mail(
                sender='dodano-przypis',
                receiver=notification_emails,
                subject=subject,
                text=text,
                recipient_variables=recipient_variables,
            )
        except MailSendException as e:
            logger.error('Annotation request notification (url: {}) could not be sent by e-mail: {}'.format(
                url,
                str(e),
            ))

    @swagger_auto_schema(request_body=AnnotationDeserializer,
                         responses={200: AnnotationSerializer})
    @method_decorator(allow_lazy_user_smart)
    def post(self, request):
        deserializer = AnnotationDeserializer(data=request.data)
        if not deserializer.is_valid():
            return ValidationErrorResponse(deserializer.errors)
        annotation = Annotation(**deserializer.validated_data['attributes'])
        annotation.user_id = request.user.pk
        annotation.save()
        response_data = AnnotationSerializer(instance=self.get_pre_serialized_annotation(annotation),
                                             context={'request': request}).data
        annotation_requests = AnnotationRequest.objects.filter(url_id=annotation.url_id)


        self.notify_subscribers(annotation.url, annotation_requests)
        return Response(response_data)

    def get_queryset(self):
        queryset = Annotation.objects.filter(active=True).annotate(
            total_upvote_count=Count('feedbacks__id')
        ).select_related(
            'user'
        ).prefetch_related(
            Prefetch('annotation_reports', queryset=AnnotationReport.objects.filter(user=self.request.user),
                     to_attr='user_annotation_reports')
        )
        return queryset

    def annotate_fetched_queryset(self, queryset):
        # Get ids on the current page
        annotation_ids = set(annotation.id for annotation in queryset)

        # Get annotations that belong to the user
        user_annotation_ids = Annotation.objects \
            .filter(user=self.request.user, id__in=annotation_ids).values_list('id', flat=True)

        # Manually annotate upvote & objection feedbacks for the current user
        feedbacks = AnnotationUpvote.objects.filter(user=self.request.user, annotation_id__in=annotation_ids)
        annotation_to_feedback = {feedback.annotation_id: feedback for feedback in feedbacks}
        for annotation in queryset:
            feedback = annotation_to_feedback.get(annotation.id)
            annotation.upvote_count_except_user = annotation.total_upvote_count - int(bool(feedback))
            annotation.does_belong_to_user = annotation.id in user_annotation_ids
            annotation.user_feedback = feedback
        return queryset

    def pre_serialize_queryset(self, queryset):
        return [
            self.get_pre_serialized_annotation(annotation, annotation.user_feedback, annotation.user_annotation_reports)
            for annotation in queryset]

    # Header parameters need to be provided explicitly
    @swagger_auto_schema(responses={200: AnnotationListSerializer(many=True)},
                         manual_parameters=StandardizedURLFilterBackend.get_manual_parameters())
    @method_decorator(allow_lazy_user_smart)
    def get(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
        except ConflictingFilterValueError as e:
            return ValidationErrorResponse(e.errors)

        queryset = self.paginator.paginate_queryset(queryset, request)

        queryset = self.annotate_fetched_queryset(queryset)

        data_list = self.pre_serialize_queryset(queryset)

        return self.get_paginated_response(
            AnnotationListSerializer(data_list, many=True, context={'request': request}).data
        )


class AnnotationFeedbackRelatedAnnotationSingle(AnnotationBase, APIView):
    resource_attr = None

    @swagger_auto_schema(responses={200: AnnotationSerializer})
    @method_decorator(allow_lazy_user_smart)
    def get(self, request, feedback_id):
        try:
            feedback = AnnotationUpvote.objects.get(id=feedback_id, user=request.user,
                                                    **({self.resource_attr: True} if self.resource_attr else {}))
            annotation = Annotation.objects.get(active=True, feedbacks=feedback_id, feedbacks__user=request.user)
            reports = AnnotationReport.objects.filter(annotation_id=annotation.id, user=request.user)
        except (AnnotationUpvote.DoesNotExist, Annotation.DoesNotExist):
            return NotFoundResponse()
        return Response(AnnotationSerializer(instance=self.get_pre_serialized_annotation(annotation, feedback, reports),
                                             context={'request': request}).data)


class AnnotationUpvoteRelatedAnnotationSingle(AnnotationFeedbackRelatedAnnotationSingle):
    resource_attr = None


class AnnotationReportRelatedAnnotationSingle(AnnotationBase, APIView):

    @swagger_auto_schema(responses={200: AnnotationSerializer})
    @method_decorator(allow_lazy_user_smart)
    def get(self, request, report_id):
        try:
            AnnotationReport.objects.get(id=report_id, user=request.user)
            annotation = Annotation.objects.get(annotation_reports=report_id, active=True,
                                                annotation_reports__user=request.user)
            feedback = AnnotationUpvote.objects.get(annotation_id=annotation.id, user=request.user)
            reports = AnnotationReport.objects.filter(annotation_id=annotation.id, user=request.user)
        except (AnnotationUpvote.DoesNotExist, Annotation.DoesNotExist, AnnotationReport.DoesNotExist):
            return NotFoundResponse()
        return Response(AnnotationSerializer(instance=self.get_pre_serialized_annotation(annotation, feedback, reports),
                                             context={'request': request}).data)
