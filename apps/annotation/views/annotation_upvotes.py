from django.db import IntegrityError
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from lazysignup.decorators import allow_lazy_user
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.annotation import serializers2
from apps.annotation.models import AnnotationUpvote
from apps.annotation.responses import ErrorResponse, NotFoundResponse, ValidationErrorResponse
from apps.annotation.views.decorators import allow_lazy_user_smart


class AnnotationUpvoteSingle(APIView):
    resource_attr = None
    serializer_class = serializers2.AnnotationUpvoteSerializer

    @swagger_auto_schema(responses={200: serializers2.AnnotationUpvoteSerializer})
    @method_decorator(allow_lazy_user)
    def get(self, request, feedback_id):
        try:
            feedback = AnnotationUpvote.objects.get(id=feedback_id, user=request.user,
                                                    **({self.resource_attr: True} if self.resource_attr else {}))
        except AnnotationUpvote.DoesNotExist:
            return NotFoundResponse('Resource not found')

        return Response(self.serializer_class(
            instance={
                'id': feedback,
                'relationships': {
                    'annotation': feedback.annotation_id
                }
            },
            context={'request': request, 'root_resource_obj': feedback}).data)

    @method_decorator(allow_lazy_user_smart)
    def delete(self, request, feedback_id):
        try:
            feedback = AnnotationUpvote.objects.get(id=feedback_id, user=request.user,
                                                    **({self.resource_attr: True} if self.resource_attr else {}))
        except AnnotationUpvote.DoesNotExist:
            return NotFoundResponse()

        feedback.delete()
        return Response()


class AnnotationUpvoteList(APIView):
    resource_attr = None
    serializer_class = serializers2.AnnotationUpvoteSerializer
    deserializer_class = serializers2.AnnotationUpvoteDeserializer

    @swagger_auto_schema(request_body=serializers2.AnnotationUpvoteDeserializer,
                         responses={200: serializers2.AnnotationUpvoteSerializer})
    @method_decorator(allow_lazy_user_smart)
    def post(self, request):
        deserializer = self.deserializer_class(data=request.data)
        if not deserializer.is_valid():
            return ValidationErrorResponse(deserializer.errors)

        feedback = AnnotationUpvote(user=request.user,
                                    **({self.resource_attr: True} if self.resource_attr else {}))
        feedback.annotation_id = deserializer.validated_data['relationships']['annotation']

        try:
            feedback.save()
        except IntegrityError:
            return ErrorResponse('Failed to create object')

        return Response(self.serializer_class(
            instance={
                'id': feedback,
                'relationships': {
                    'annotation': feedback.annotation_id
                }
            },
            context={'request': request, 'root_resource_obj': feedback}).data
        )


class AnnotationRelatedAnnotationUpvoteSingle(APIView):
    serializer_class = serializers2.AnnotationUpvoteSerializer

    @swagger_auto_schema(responses={200: serializers2.AnnotationUpvoteSerializer})
    @method_decorator(allow_lazy_user)
    def get(self, request, annotation_id):
        try:
            feedback = AnnotationUpvote.objects.get(annotation_id=annotation_id, user=request.user)
        except AnnotationUpvote.DoesNotExist:
            return NotFoundResponse('Resource not found')

        return Response(self.serializer_class(
            instance={
                'id': feedback,
                'relationships': {
                    'annotation': feedback.annotation_id
                }
            },
            context={'request': request, 'root_resource_obj': feedback}).data
        )
