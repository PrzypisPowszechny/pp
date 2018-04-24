from django.db import IntegrityError
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from lazysignup.decorators import allow_lazy_user
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.pp.models import UserReferenceFeedback
from apps.pp.responses import ErrorResponse, NotFoundResponse, ValidationErrorResponse
from apps.pp.serializers import UsefulSerializer, UsefulDeserializer
from apps.pp.utils import DataPreSerializer, get_resource_name, get_relationship_id


class ReferenceUsefulChange(APIView):

    resource_name = UserReferenceFeedback.JSONAPIMeta.useful_resource_name
    deprecated_description = '<bold>DEPRECATED. Use absolute "%s" resource endpoint instead.' % resource_name

    @swagger_auto_schema(operation_description=deprecated_description)
    @method_decorator(allow_lazy_user)
    def post(self, request, reference_id):
        try:
            UserReferenceFeedback.objects.create(reference_id=reference_id, user=request.user, useful=True)
        except IntegrityError:
            return ErrorResponse('Failed to create object')
        return Response(data=None)

    @swagger_auto_schema(operation_description=deprecated_description)
    @method_decorator(allow_lazy_user)
    def delete(self, request, reference_id):
        try:
            model = UserReferenceFeedback.objects.get(reference_id=reference_id, user=request.user, useful=True)
        except UserReferenceFeedback.DoesNotExist:
            return NotFoundResponse()

        model.delete()
        return Response(data=None)

    @swagger_auto_schema(responses={200: UsefulSerializer})
    @method_decorator(allow_lazy_user)
    def get(self, request, reference_id):
        try:
            useful = UserReferenceFeedback.objects.get(reference_id=reference_id, user=request.user, useful=True)
        except UserReferenceFeedback.DoesNotExist:
            return NotFoundResponse('Resource not found')

        pre_serializer = DataPreSerializer(useful, {'attributes': useful})
        pre_serializer.set_relation(resource_name=get_resource_name(useful, related_field='reference_id'),
                                    resource_id=useful.reference_id)
        return Response(UsefulSerializer(pre_serializer.data, context={'request': request}).data)


class Useful(APIView):
    resource_name = 'usefuls'

    @swagger_auto_schema(responses={200: UsefulSerializer})
    @method_decorator(allow_lazy_user)
    def get(self, request, useful_id):
        try:
            useful = UserReferenceFeedback.objects.get(id=useful_id, user=request.user, useful=True)
        except UserReferenceFeedback.DoesNotExist:
            return NotFoundResponse('Resource not found')

        pre_serializer = DataPreSerializer(useful, {'attributes': useful})
        pre_serializer.set_relation(resource_name=get_resource_name(useful, related_field='reference_id'),
                                    resource_id=useful.reference_id)
        return Response(UsefulSerializer(pre_serializer.data, context={'request': request}).data)

    @method_decorator(allow_lazy_user)
    def delete(self, request, useful_id):
        try:
            useful = UserReferenceFeedback.objects.get(id=useful_id, user=request.user, useful=True)
        except UserReferenceFeedback.DoesNotExist:
            return NotFoundResponse()

        useful.delete()
        return Response()


class UsefulList(APIView):
    resource_name = 'usefuls'

    @swagger_auto_schema(request_body=UsefulDeserializer,
                         responses={200: UsefulSerializer})
    @method_decorator(allow_lazy_user)
    def post(self, request):
        deserializer = UsefulDeserializer(data=request.data)
        if not deserializer.is_valid():
            return ValidationErrorResponse(deserializer.errors)

        feedback = UserReferenceFeedback(useful=True, user=request.user)
        feedback.reference_id = get_relationship_id(deserializer, 'reference')

        try:
            feedback.save()
        except IntegrityError as e:
            return ErrorResponse('Failed to create object')

        pre_serializer = DataPreSerializer(feedback, {'attributes': feedback})
        pre_serializer.set_relation(resource_name=get_resource_name(feedback, related_field='reference_id'),
                                    resource_id=feedback.reference_id)
        return Response(UsefulSerializer(pre_serializer.data, context={'request': request}).data)
