"""
Serializers for the authentication app.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from apps.authentication.models import User, UserSession

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model — used for read and profile display."""

    full_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'mobile',
            'role', 'is_active', 'is_email_verified', 'full_name',
            'last_login_at', 'created_at',
        ]
        read_only_fields = ['id', 'email', 'role', 'is_active', 'is_email_verified', 'created_at']

    def get_full_name(self, obj):
        return obj.get_full_name()


class UserRegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True, label='Confirm Password')

    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'mobile',
            'role', 'password', 'password2',
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password2'):
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a user's profile info."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'mobile']


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password."""

    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True, write_only=True, label='Confirm New Password')

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({'new_password': 'New passwords do not match.'})
        return attrs


class UserSessionSerializer(serializers.ModelSerializer):
    """Serializer for UserSession — used for audit/display purposes."""

    class Meta:
        model = UserSession
        fields = ['id', 'ip_address', 'user_agent', 'created_at', 'expires_at', 'is_active']
        read_only_fields = fields
