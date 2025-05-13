from rest_framework import serializers
from .models import User, Notification

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name', 'birthdate', 'age', 'gender', 'address', 'contact_no', 'is_pwd', 'is_4ps_member', 'is_senior_citizen', 'role', 'created_at']
        read_only_fields = ['id', 'created_at']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'timestamp', 'is_read', 'event']
        read_only_fields = ['id', 'timestamp']