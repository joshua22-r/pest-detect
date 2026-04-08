from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Plant, Animal, Disease, DetectionResult, 
    UserProfile, SystemStatistics
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


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
