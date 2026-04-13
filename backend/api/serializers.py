from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Plant, Animal, Disease, DetectionResult, 
    UserProfile, SystemStatistics, Trial, Subscription, Payment,
    MFASettings, AuditLog, UserSession, Role, Permission, UserRole, RolePermission
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class AdminUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user_type']


class AdminUserSerializer(serializers.ModelSerializer):
    profile = AdminUserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_active', 'is_staff', 'is_superuser', 'profile'
        ]


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['user', 'user_type', 'phone', 'location', 'bio', 'total_scans']


class PlantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plant
        fields = ['id', 'name', 'scientific_name', 'description', 'created_at']


class AnimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Animal
        fields = ['id', 'name', 'species', 'scientific_name', 'description', 'created_at']


class DiseaseSerializer(serializers.ModelSerializer):
    affected_plants = PlantSerializer(many=True, read_only=True)
    affected_animals = AnimalSerializer(many=True, read_only=True)

    class Meta:
        model = Disease
        fields = [
            'id', 'name', 'subject_type', 'scientific_name', 
            'description', 'symptoms', 'treatment', 'prevention',
            'affected_plants', 'affected_animals', 'severity'
        ]


class DiseaseDetailSerializer(serializers.ModelSerializer):
    affected_plants = PlantSerializer(many=True, read_only=True)
    affected_animals = AnimalSerializer(many=True, read_only=True)

    class Meta:
        model = Disease
        fields = '__all__'


class DetectionResultSerializer(serializers.ModelSerializer):
    disease = DiseaseSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = DetectionResult
        fields = [
            'id', 'user', 'image', 'subject_type', 'disease', 
            'disease_name', 'confidence', 'severity', 
            'treatment', 'prevention', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class DetectionResultCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetectionResult
        fields = [
            'image', 'subject_type', 'disease_name', 
            'confidence', 'severity', 'treatment', 'prevention', 'notes'
        ]


class SystemStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemStatistics
        fields = [
            'total_scans', 'total_users', 'plant_scans', 
            'animal_scans', 'diseases_detected', 'updated_at'
        ]


class TrialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trial
        fields = ['id', 'user', 'attempts_used', 'max_attempts', 'status', 'created_at', 'updated_at']


class SubscriptionSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'user', 'username', 'user_email', 'plan', 'status', 'payment_method',
            'mobile_number', 'amount', 'start_date', 'end_date', 'is_paid', 'created_at', 'updated_at'
        ]


class PaymentSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'subscription', 'user', 'username', 'user_email', 'amount',
            'payment_method', 'mobile_number', 'status', 'transaction_id', 'created_at', 'updated_at'
        ]


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'is_active', 'created_at', 'updated_at']


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'permission_type', 'resource_type', 'description', 'is_active', 'created_at', 'updated_at']


class UserRoleSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.name', read_only=True)
    assigned_by_username = serializers.CharField(source='assigned_by.username', read_only=True)
    
    class Meta:
        model = UserRole
        fields = [
            'id', 'user', 'role', 'role_name', 'assigned_by', 'assigned_by_username',
            'assigned_at', 'expires_at', 'is_active'
        ]
        read_only_fields = ['id', 'assigned_at']


class RolePermissionSerializer(serializers.ModelSerializer):
    permission_name = serializers.CharField(source='permission.name', read_only=True)
    permission_codename = serializers.CharField(source='permission.codename', read_only=True)
    
    class Meta:
        model = RolePermission
        fields = ['id', 'role', 'permission', 'permission_name', 'permission_codename', 'created_at']
        read_only_fields = ['id', 'created_at']


class MFASettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MFASettings
        fields = ['mfa_enabled', 'mfa_method', 'phone_number', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class AuditLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'username', 'action_type', 'description', 
            'ip_address', 'user_agent', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class UserSessionSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    is_current_session = serializers.SerializerMethodField()
    
    class Meta:
        model = UserSession
        fields = [
            'id', 'username', 'session_key', 'ip_address', 'user_agent', 
            'device_info', 'last_activity', 'created_at', 'is_current_session'
        ]
        read_only_fields = ['id', 'created_at', 'last_activity']
    
    def get_is_current_session(self, obj):
        """Check if this is the current user's session"""
        request = self.context.get('request')
        if request and hasattr(request, 'session'):
            return obj.session_key == request.session.session_key
        return False
