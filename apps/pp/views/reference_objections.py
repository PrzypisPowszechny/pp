from django.db import IntegrityError
from django.utils.decorators import method_decorator
from lazysignup.decorators import allow_lazy_user
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.pp.models import UserReferenceFeedback
from apps.pp.utils.views import ErrorResponse


class ReferenceObjectionChange(APIView):
    resource_name = 'reference_objections'

    @method_decorator(allow_lazy_user)
    def post(self, request, reference_id):
        try:
            UserReferenceFeedback.objects.create(reference_id=reference_id, user=request.user, objection=True)
        except IntegrityError:
            return ErrorResponse('Resource not found')
        return Response()

    @method_decorator(allow_lazy_user)
    def delete(self, request, reference_id):
        try:
            model = UserReferenceFeedback.objects.get(reference_id=reference_id, user=request.user, objection=True)
        except UserReferenceFeedback.DoesNotExist:
            return ErrorResponse('Resource not found')

        model.delete()
        return Response()
