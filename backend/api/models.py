from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class Plant(models.Model):
    """Plant species database"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    scientific_name = models.CharField(max_length=150, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Animal(models.Model):
    """Livestock species database"""
    SPECIES_CHOICES = (
        ('cattle', 'Cattle'),
        ('sheep', 'Sheep'),
        ('goat', 'Goat'),
        ('horse', 'Horse'),
        ('pig', 'Pig'),
        ('poultry', 'Poultry'),
        ('dog', 'Dog'),
        ('cat', 'Cat'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=20, choices=SPECIES_CHOICES)
    scientific_name = models.CharField(max_length=150, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_species_display()})"

    class Meta:
        ordering = ['species', 'name']


class Disease(models.Model):
    """Disease/Pest/Condition database"""
    SUBJECT_TYPE_CHOICES = (
        ('plant', 'Plant Disease'),
        ('animal', 'Livestock Disease/Pest'),
    )
    
    SEVERITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150, unique=True)
    subject_type = models.CharField(max_length=10, choices=SUBJECT_TYPE_CHOICES)
    scientific_name = models.CharField(max_length=150, blank=True)
    description = models.TextField()
    symptoms = models.TextField()
    treatment = models.TextField()
    prevention = models.TextField()
    affected_plants = models.ManyToManyField(Plant, blank=True, related_name='diseases')
    affected_animals = models.ManyToManyField(Animal, blank=True, related_name='diseases')
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_subject_type_display()})"

    class Meta:
        ordering = ['name']


class DetectionResult(models.Model):
    """User detection scan results"""
    SUBJECT_TYPE_CHOICES = (
        ('plant', 'Plant'),
        ('animal', 'Livestock'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='detections')
    image = models.ImageField(upload_to='detections/')
    subject_type = models.CharField(max_length=10, choices=SUBJECT_TYPE_CHOICES)
    disease = models.ForeignKey(Disease, on_delete=models.SET_NULL, null=True, blank=True)
    disease_name = models.CharField(max_length=150)
    confidence = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    severity = models.CharField(max_length=10)
    treatment = models.TextField()
    prevention = models.TextField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.disease_name} - {self.user.username} - {self.created_at}"

    class Meta:
        ordering = ['-created_at']


class UserProfile(models.Model):
    """Extended user profile"""
    USER_TYPE_CHOICES = (
        ('farmer', 'Farmer'),
        ('veterinarian', 'Veterinarian'),
        ('agronomist', 'Agronomist'),
        ('admin', 'Admin'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='farmer')
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True)
    total_scans = models.IntegerField(default=0)
    admin_allowed_access = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} Profile"

    class Meta:
        ordering = ['-created_at']


class SystemStatistics(models.Model):
    """System-wide statistics"""
    total_scans = models.IntegerField(default=0)
    total_users = models.IntegerField(default=0)
    plant_scans = models.IntegerField(default=0)
    animal_scans = models.IntegerField(default=0)
    diseases_detected = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "System Statistics"

    class Meta:
        verbose_name_plural = "System Statistics"


class Trial(models.Model):
    """Trial usage tracking"""
    TRIAL_STATUS_CHOICES = (
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('converted', 'Converted to Subscription'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='trial')
    attempts_used = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=5)
    status = models.CharField(max_length=20, choices=TRIAL_STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Trial - {self.user.username} ({self.attempts_used}/{self.max_attempts})"

    class Meta:
        ordering = ['-created_at']


class Subscription(models.Model):
    """User subscription plans"""
    PLAN_CHOICES = (
        ('daily', 'Daily - 3,000 UGX'),
        ('weekly', 'Weekly - 10,000 UGX'),
        ('monthly', 'Monthly - 20,000 UGX'),
    )
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('mtn', 'MTN Mobile Money'),
        ('airtel', 'Airtel Mobile Money'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    mobile_number = models.CharField(max_length=20)
    amount = models.IntegerField()  # Amount in UGX
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.plan} ({self.status})"

    class Meta:
        ordering = ['-created_at']


class Payment(models.Model):
    """Payment transaction tracking"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='payments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    amount = models.IntegerField()  # Amount in UGX
    payment_method = models.CharField(max_length=20)
    mobile_number = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment - {self.user.username} - {self.amount} UGX ({self.status})"

    class Meta:
        ordering = ['-created_at']
