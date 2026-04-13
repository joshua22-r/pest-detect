from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from .fields import EncryptedCharField
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
        ('moderator', 'Moderator'),
        ('content_moderator', 'Content Moderator'),
        ('user_moderator', 'User Moderator'),
        ('admin', 'Admin'),
        ('super_admin', 'Super Admin'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='farmer')
    phone = EncryptedCharField(max_length=50, blank=True)
    location = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True)
    total_scans = models.IntegerField(default=0)
    admin_allowed_access = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} Profile"

    @property
    def is_moderator(self):
        """Check if user has any moderator role"""
        return self.user_type in ['moderator', 'content_moderator', 'user_moderator', 'admin', 'super_admin']
    
    @property
    def is_admin(self):
        """Check if user has admin privileges"""
        return self.user_type in ['admin', 'super_admin']
    
    @property
    def is_super_admin(self):
        """Check if user has super admin privileges"""
        return self.user_type == 'super_admin'

    class Meta:
        ordering = ['-created_at']


class Role(models.Model):
    """Role-based access control roles"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Permission(models.Model):
    """Granular permissions for RBAC"""
    PERMISSION_TYPES = (
        ('view', 'View'),
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('moderate', 'Moderate'),
        ('admin', 'Admin'),
    )
    
    RESOURCE_TYPES = (
        ('user', 'User'),
        ('detection', 'Detection'),
        ('disease', 'Disease'),
        ('plant', 'Plant'),
        ('animal', 'Animal'),
        ('subscription', 'Subscription'),
        ('payment', 'Payment'),
        ('audit_log', 'Audit Log'),
        ('system', 'System'),
    )
    
    name = models.CharField(max_length=100, unique=True)
    codename = models.CharField(max_length=100, unique=True)
    permission_type = models.CharField(max_length=20, choices=PERMISSION_TYPES)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.permission_type}_{self.resource_type}"

    class Meta:
        ordering = ['resource_type', 'permission_type']


class UserRole(models.Model):
    """Many-to-many relationship between users and roles"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='user_roles')
    assigned_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_roles'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.role.name}"

    def is_expired(self):
        """Check if the role assignment has expired"""
        if self.expires_at and timezone.now() > self.expires_at:
            return True
        return False

    class Meta:
        ordering = ['-assigned_at']
        unique_together = ['user', 'role']


class RolePermission(models.Model):
    """Many-to-many relationship between roles and permissions"""
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_permissions')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name='role_permissions')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role.name} - {self.permission.name}"

    class Meta:
        unique_together = ['role', 'permission']


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


class MFASettings(models.Model):
    """Multi-factor authentication settings for users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mfa_settings')
    mfa_enabled = models.BooleanField(default=False)
    mfa_method = models.CharField(
        max_length=10,
        choices=[('totp', 'TOTP'), ('sms', 'SMS')],
        default='totp'
    )
    phone_number = EncryptedCharField(max_length=50, blank=True, null=True)
    backup_codes = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"MFA Settings for {self.user.username}"

    def generate_backup_codes(self):
        """Generate 10 backup codes"""
        import secrets
        self.backup_codes = [secrets.token_hex(4).upper() for _ in range(10)]
        self.save()

    def use_backup_code(self, code):
        """Use a backup code and remove it from the list"""
        if code in self.backup_codes:
            self.backup_codes.remove(code)
            self.save()
            return True
        return False


class AuditLog(models.Model):
    """Audit log for security events and admin actions"""
    ACTION_TYPES = (
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('failed_login', 'Failed Login Attempt'),
        ('password_change', 'Password Change'),
        ('mfa_setup', 'MFA Setup'),
        ('mfa_verify', 'MFA Verification'),
        ('admin_action', 'Admin Action'),
        ('data_export', 'Data Export'),
        ('data_delete', 'Data Deletion'),
        ('profile_update', 'Profile Update'),
        ('detection_create', 'Detection Created'),
        ('detection_delete', 'Detection Deleted'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action_type} - {self.user.username if self.user else 'Anonymous'} - {self.created_at}"

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'action_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['ip_address']),
        ]


class PasswordHistory(models.Model):
    """Password history to prevent reuse of recent passwords"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_history')
    password_hash = models.CharField(max_length=128)  # Store hashed password
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Password history for {self.user.username} - {self.created_at}"

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]

    @staticmethod
    def check_password_reuse(user, new_password):
        """Check if new password matches any recent passwords"""
        from django.contrib.auth.hashers import check_password
        from django.conf import settings

        history_count = getattr(settings, 'PASSWORD_HISTORY_COUNT', 5)
        recent_passwords = PasswordHistory.objects.filter(
            user=user
        ).order_by('-created_at')[:history_count]

        for old_password in recent_passwords:
            if check_password(new_password, old_password.password_hash):
                return True
        return False

    @staticmethod
    def add_password_to_history(user, password):
        """Add current password hash to history before changing"""
        from django.contrib.auth.hashers import make_password
        from django.conf import settings

        history_count = getattr(settings, 'PASSWORD_HISTORY_COUNT', 5)
        current_count = PasswordHistory.objects.filter(user=user).count()
        if current_count >= history_count:
            oldest_passwords = PasswordHistory.objects.filter(
                user=user
            ).order_by('-created_at')[history_count-1:]
            oldest_passwords.delete()

        if password.startswith(('pbkdf2_', 'argon2$', 'bcrypt$')):
            password_hash = password
        else:
            password_hash = make_password(password)

        PasswordHistory.objects.create(
            user=user,
            password_hash=password_hash
        )

    class Meta:
        verbose_name_plural = "Password histories"


class UserSession(models.Model):
    """Track active user sessions for device management and concurrent limits"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='active_sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    device_info = models.JSONField(default=dict, blank=True)  # Store device/browser info
    last_activity = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Session for {self.user.username} - {self.ip_address}"

    class Meta:
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['user', 'last_activity']),
            models.Index(fields=['session_key']),
        ]

    @staticmethod
    def get_active_sessions(user):
        """Get all active sessions for a user"""
        from django.conf import settings
        from django.utils import timezone
        from datetime import timedelta

        session_timeout = getattr(settings, 'SESSION_COOKIE_AGE', 3600)
        cutoff_time = timezone.now() - timedelta(seconds=session_timeout)

        return UserSession.objects.filter(
            user=user,
            last_activity__gte=cutoff_time
        ).order_by('-last_activity')

    @staticmethod
    def enforce_concurrent_limits(user, current_session_key=None):
        """Enforce maximum concurrent sessions per user"""
        from django.conf import settings

        max_sessions = getattr(settings, 'MAX_CONCURRENT_SESSIONS', 3)
        active_sessions = UserSession.get_active_sessions(user)

        if current_session_key:
            active_sessions = active_sessions.exclude(session_key=current_session_key)

        if active_sessions.count() >= max_sessions:
            # Remove oldest sessions to make room
            sessions_to_remove = active_sessions[max_sessions-1:]
            for session in sessions_to_remove:
                session.delete()
            return True  # Sessions were cleaned up
        return False

    def update_activity(self):
        """Update last activity timestamp"""
        from django.utils import timezone
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])


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
    mobile_number = EncryptedCharField(max_length=50)
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
    mobile_number = EncryptedCharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = EncryptedCharField(max_length=150, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment - {self.user.username} - {self.amount} UGX ({self.status})"

    class Meta:
        ordering = ['-created_at']
