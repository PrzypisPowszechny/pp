from django.db import IntegrityError
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from lazysignup.decorators import allow_lazy_user
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.pp.models import AnnotationUpvote
from apps.pp.responses import ErrorResponse, NotFoundResponse, ValidationErrorResponse
from apps.pp.serializers import AnnotationUpvoteSerializer, AnnotationUpvoteDeserializer
from apps.pp.utils import DataPreSerializer, get_resource_name, get_relationship_id


class AnnotationUpvoteSingle(APIView):
    resource_attr = None
    serializer_class = AnnotationUpvoteSerializer

    @swagger_auto_schema(responses={200: AnnotationUpvoteSerializer})
    @method_decorator(allow_lazy_user)
    def get(self, request, feedback_id):
        try:
            feedback = AnnotationUpvote.objects.get(id=feedback_id, user=request.user,
                                                    **({self.resource_attr: True} if self.resource_attr else {}))
        except AnnotationUpvote.DoesNotExist:
            return NotFoundResponse('Resource not found')

        pre_serializer = DataPreSerializer(feedback, {'attributes': feedback})
        pre_serializer.set_relation(resource_name=get_resource_name(feedback, related_field='annotation_id'),
                                    resource_id=feedback.annotation_id)
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


class AnnotationUpvoteList(APIView):
    resource_attr = None
    serializer_class = AnnotationUpvoteSerializer
    deserializer_class = AnnotationUpvoteDeserializer

    @swagger_auto_schema(request_body=AnnotationUpvoteDeserializer,
                         responses={200: AnnotationUpvoteSerializer})
    @method_decorator(allow_lazy_user)
    def post(self, request):
        deserializer = self.deserializer_class(data=request.data)
        if not deserializer.is_valid():
            return ValidationErrorResponse(deserializer.errors)

        feedback = AnnotationUpvote(user=request.user,
                                    **({self.resource_attr: True} if self.resource_attr else {}))
        feedback.annotation_id = get_relationship_id(deserializer, 'annotation')

        try:
            feedback.save()
        except IntegrityError:
            return ErrorResponse('Failed to create object')

        pre_serializer = DataPreSerializer(feedback, {'attributes': feedback})
        pre_serializer.set_relation(resource_name=get_resource_name(feedback, related_field='annotation_id'),
                                    resource_id=feedback.annotation_id)
        return Response(self.serializer_class(pre_serializer.data, context={'request': request}).data)


class AnnotationRelatedAnnotationUpvoteSingle(APIView):
    resource_attr = None
    serializer_class = AnnotationUpvoteSerializer

    @swagger_auto_schema(responses={200: AnnotationUpvoteSerializer})
    @method_decorator(allow_lazy_user)
    def get(self, request, annotation_id):
        try:
            feedback = AnnotationUpvote.objects.get(annotation_id=annotation_id, user=request.user,
                                                    **({self.resource_attr: True} if self.resource_attr else {}))
        except AnnotationUpvote.DoesNotExist:
            return NotFoundResponse('Resource not found')

        pre_serializer = DataPreSerializer(feedback, {'attributes': feedback})
        pre_serializer.set_relation(resource_name=get_resource_name(feedback, related_field='annotation_id'),
                                    resource_id=feedback.annotation_id)
        return Response(self.serializer_class(pre_serializer.data, context={'request': request}).data)
