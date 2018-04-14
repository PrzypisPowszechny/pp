from django.utils.decorators import method_decorator
from lazysignup.decorators import allow_lazy_user
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_json_api.parsers import JSONParser

from apps.pp.serializers import ReferenceReportSerializer
from apps.pp.utils.views import ValidationErrorResponse, data_wrapped_view


class ReferenceReportPOST(APIView):
    resource_name = 'reference_reports'

    @method_decorator(allow_lazy_user)
    @method_decorator(data_wrapped_view)
    def post(self, request, reference_id):
        data = JSONParser().parse(request, parser_context={'request': request, 'view': ReferenceReportPOST})
        # KG: we need to help JSONParser with relationships: extract {'id': X} pairs to X
        data['reference'] = reference_id
        # Set the user as the authenticated user
        data['user'] = request.user.pk

        serializer = ReferenceReportSerializer(data=data, context={'request': request})
        if not serializer.is_valid():
            return ValidationErrorResponse(serializer.errors)
        reference = serializer.save()
        reference_json = ReferenceReportSerializer(reference, context={'request': request})
        return Response(reference_json.data)
