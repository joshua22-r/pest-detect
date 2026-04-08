from django.contrib import admin
from .models import Plant, Animal, Disease, DetectionResult, UserProfile, SystemStatistics


@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = ['name', 'scientific_name', 'created_at']
    search_fields = ['name', 'scientific_name']
    ordering = ['name']


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ['name', 'species', 'scientific_name', 'created_at']
    search_fields = ['name', 'scientific_name', 'species']
    list_filter = ['species']
    ordering = ['species', 'name']


@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject_type', 'severity', 'created_at']
    search_fields = ['name', 'scientific_name']
    list_filter = ['subject_type', 'severity']
    filter_horizontal = ['affected_plants', 'affected_animals']
    ordering = ['name']


@admin.register(DetectionResult)
class DetectionResultAdmin(admin.ModelAdmin):
    list_display = ['disease_name', 'user', 'subject_type', 'confidence', 'severity', 'created_at']
    search_fields = ['disease_name', 'user__username']
    list_filter = ['subject_type', 'severity', 'created_at']
    readonly_fields = ['user', 'created_at', 'updated_at', 'image']
    ordering = ['-created_at']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_type', 'total_scans', 'created_at']
    search_fields = ['user__username', 'user_type']
    list_filter = ['user_type', 'created_at']
    readonly_fields = ['user', 'created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(SystemStatistics)
class SystemStatisticsAdmin(admin.ModelAdmin):
    list_display = ['total_scans', 'total_users', 'plant_scans', 'animal_scans', 'diseases_detected', 'updated_at']
    readonly_fields = ['updated_at']
