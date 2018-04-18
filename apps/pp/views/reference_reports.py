from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from lazysignup.decorators import allow_lazy_user
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.pp.models import Reference, ReferenceReport
from apps.pp.serializers import ReferenceReportSerializer, ReferenceReportDeserializer
from apps.pp.responses import ValidationErrorResponse, NotFoundResponse
from apps.pp.utils import set_relationship


class ReferenceReportPOST(APIView):
    resource_name = 'reference_reports'

    @swagger_auto_schema(request_body=ReferenceReportDeserializer,
                         responses={200: ReferenceReportSerializer})
    @method_decorator(allow_lazy_user)
    def post(self, request, reference_id):
        try:
            reference = Reference.objects.get(active=True, id=reference_id)
        except Reference.DoesNotExist:
            return NotFoundResponse()

        serializer = ReferenceReportDeserializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return ValidationErrorResponse(serializer.errors)
        report = ReferenceReport(**serializer.validated_data['attributes'])
        report.user_id = request.user.pk
        report.reference_id = reference.pk
        report.save()

        data = {'id': report.id, 'type': self.resource_name, 'attributes': report}
        set_relationship(data, report, attr='reference_id')
        set_relationship(data, reference, attr='user_id')
        return Response(ReferenceReportSerializer(data, context={'request': request}).data)
