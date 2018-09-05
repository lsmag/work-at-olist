from django.db import IntegrityError
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response

from sparrow.call_records.models import CallRecord
from sparrow.call_records.serializers import CallRecordStartSerializer, CallRecordEndSerializer


class CallRecordsView(generics.ListCreateAPIView):
    queryset = CallRecord.objects.all()

    def get_serializer_class(self):
        """
        Returns either CallRecordStartSerializer or CallRecordEndSerializer
        based on the method or request body
        """
        if self.request.method == 'GET' or self.request.data.get('type') == CallRecord.START:
            return CallRecordStartSerializer
        elif self.request.data.get('type') == 'end':
            return CallRecordEndSerializer

    def post(self, request, *args, **kwargs):
        if not CallRecord.is_record_type(request.data.get('type')):
            return Response({
                'type': ['Only "start" or "end" are allowed']
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            return super().post(request, *args, **kwargs)
        except IntegrityError:
            return Response({
                'detail': 'Call record already exists'
            }, status=status.HTTP_409_CONFLICT)
