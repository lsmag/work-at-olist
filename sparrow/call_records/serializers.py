__all__ = ['CallRecordStartSerializer', 'CallRecordEndSerializer']

from rest_framework import serializers

from sparrow.call_records.models import CallRecord


class CallRecordSerializerMixin:
    """
    Generic class to override `self.create`. It adds a static
    CallRecord.RECORD_TYPE as a value depending on what's configured
    in the serializer's CALL_RECORD_TYPE field
    """

    def create(self, validated_data):
        return CallRecord.objects.create(type=self.CALL_RECORD_TYPE, **validated_data)


class CallRecordStartSerializer(CallRecordSerializerMixin, serializers.ModelSerializer):
    """
    This is the most complete serializer, which contains all of
    CallRecord's fields.

    It can be used for either POST requests for START call records or
    for serializing _any_ call record.
    
    When serializing, if call record is of END type, it'll omit the
    `source` and `destination` fields
    """

    CALL_RECORD_TYPE = CallRecord.START

    class Meta:
        model = CallRecord
        fields = ('id', 'call_id', 'timestamp', 'source', 'destination')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # NOTE: This is to override the model's settings. Since the
        # field has blank=True, it's considered as optional by default
        # to the serializer, which is not what we want
        for field in ['source', 'destination']:
            self.fields[field].required = True
            self.fields[field].allow_blank = False

    def to_representation(self, record):
        data = {
            'id': record.id,
            'type': record.type,
            'call_id': record.call_id,
            'timestamp': record.timestamp,
        }

        if record.is_start_record:
            data.update({
                'source': record.source,
                'destination': record.destination
            })

        return data


class CallRecordEndSerializer(CallRecordSerializerMixin, serializers.ModelSerializer):
    CALL_RECORD_TYPE = CallRecord.END

    class Meta:
        model = CallRecord
        fields = ('call_id', 'timestamp')

    def to_representation(self, record):
        return {
            'id': record.id,
            'type': record.type,
            'call_id': record.call_id,
            'timestamp': record.timestamp
        }
