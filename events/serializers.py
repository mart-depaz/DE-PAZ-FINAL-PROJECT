# for events app
# serializers.py


from rest_framework import serializers
from .models import Event
from django.utils import timezone

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'what', 'when', 'where', 'who', 'created_by', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']

    def validate_when(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Event date and time cannot be in the past.")
        return value