from django.db import IntegrityError
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from lazysignup.decorators import allow_lazy_user
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.pp.models import AnnotationUpvote
from apps.pp.responses import ErrorResponse, NotFoundResponse, ValidationErrorResponse
from apps.pp.serializers import FeedbackSerializer, FeedbackDeserializer
from apps.pp.utils import DataPreSerializer, get_resource_name, get_relationship_id


class ReferenceRelatedReferenceFeedbackSingle(APIView):
    resource_attr = None
    serializer_class = FeedbackSerializer
    deprecated_description = 'DEPRECATED. Use absolute resource endpoint instead.'

    @swagger_auto_schema(operation_description=deprecated_description)
    @method_decorator(allow_lazy_user)
    def post(self, request, reference_id):
        try:
            AnnotationUpvote.objects.create(reference_id=reference_id, user=request.user,
                                                 **({self.resource_attr: True} if self.resource_attr else {}))
        except IntegrityError:
            return ErrorResponse('Failed to create object')
        return Response(data=None)

    @swagger_auto_schema(operation_description=deprecated_description)
    @method_decorator(allow_lazy_user)
    def delete(self, request, reference_id):
        try:
            model = AnnotationUpvote.objects.get(reference_id=reference_id, user=request.user,
                                                      **({self.resource_attr: True} if self.resource_attr else {}))
        except AnnotationUpvote.DoesNotExist:
            return NotFoundResponse()

        model.delete()
        return Response(data=None)

    @swagger_auto_schema(responses={200: FeedbackSerializer})
    @method_decorator(allow_lazy_user)
    def get(self, request, reference_id):
        try:
            feedback = AnnotationUpvote.objects.get(reference_id=reference_id, user=request.user,
                                                         **({self.resource_attr: True} if self.resource_attr else {}))
        except AnnotationUpvote.DoesNotExist:
            return NotFoundResponse('Resource not found')

        pre_serializer = DataPreSerializer(feedback, {'attributes': feedback})
        pre_serializer.set_relation(resource_name=get_resource_name(feedback, related_field='reference_id'),
                                    resource_id=feedback.reference_id)
        return Response(self.serializer_class(pre_serializer.data, context={'request': request}).data)


class FeedbackSingle(APIView):
    resource_attr = None
    serializer_class = FeedbackSerializer

    @swagger_auto_schema(responses={200: FeedbackSerializer})
    @method_decorator(allow_lazy_user)
    def get(self, request, feedback_id):
        try:
            feedback = AnnotationUpvote.objects.get(id=feedback_id, user=request.user,
                                                         **({self.resource_attr: True} if self.resource_attr else {}))
        except AnnotationUpvote.DoesNotExist:
            return NotFoundResponse('Resource not found')

        pre_serializer = DataPreSerializer(feedback, {'attributes': feedback})
        pre_serializer.set_relation(resource_name=get_resource_name(feedback, related_field='reference_id'),
                                    resource_id=feedback.reference_id)
        return Response(self.serializer_class(pre_serializer.data, context={'request': request}).data)

    @method_decorator(allow_lazy_user)
    def delete(self, request, feedback_id):
        try:
            feedback = AnnotationUpvote.objects.get(id=feedback_id, user=request.user,
                                                         **({self.resource_attr: True} if self.resource_attr else {}))
        except AnnotationUpvote.DoesNotExist:
            return NotFoundResponse()

        feedback.delete()
        return Response()


class FeedbackList(APIView):
    resource_attr = None
    serializer_class = FeedbackSerializer
    deserializer_class = FeedbackDeserializer

    @swagger_auto_schema(request_body=FeedbackDeserializer,
                         responses={200: FeedbackSerializer})
    @method_decorator(allow_lazy_user)
    def post(self, request):
        deserializer = self.deserializer_class(data=request.data)
        if not deserializer.is_valid():
            return ValidationErrorResponse(deserializer.errors)

        feedback = AnnotationUpvote(user=request.user,
                                         **({self.resource_attr: True} if self.resource_attr else {}))
        feedback.reference_id = get_relationship_id(deserializer, 'reference')

        try:
            feedback.save()
        except IntegrityError:
            return ErrorResponse('Failed to create object')

        pre_serializer = DataPreSerializer(feedback, {'attributes': feedback})
        pre_serializer.set_relation(resource_name=get_resource_name(feedback, related_field='reference_id'),
                                    resource_id=feedback.reference_id)
        return Response(self.serializer_class(pre_serializer.data, context={'request': request}).data)
