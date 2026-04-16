from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from django_ratelimit.decorators import ratelimit  # Enabled for security
from .models import (
    Plant, Animal, Disease, DetectionResult, 
    UserProfile, SystemStatistics, Trial, Subscription, Payment,
    MFASettings, AuditLog, UserSession, Role, Permission, UserRole, RolePermission
)
from .serializers import (
    UserSerializer, AdminUserSerializer, UserProfileSerializer, PlantSerializer,
    AnimalSerializer, DiseaseSerializer, DiseaseDetailSerializer,
    DetectionResultSerializer, DetectionResultCreateSerializer,
    SystemStatisticsSerializer, TrialSerializer, SubscriptionSerializer, PaymentSerializer,
    MFASettingsSerializer, AuditLogSerializer, UserSessionSerializer,
    RoleSerializer, PermissionSerializer, UserRoleSerializer, RolePermissionSerializer
)
from .utils import (
    sanitize_string, validate_email_domain, validate_file_upload,
    generate_password_reset_token, verify_password_reset_token,
    encode_uid, decode_uid,
    get_google_user_info, get_facebook_user_info, build_social_username,
)
from .mobile_money_service import MobileMoneyService, MTNMobileMoneyService
from .data_service import DataManagementService
from .email_service import EmailService
from .analytics_service import AnalyticsService
from .ml_detector import MockMLDetector
from .permissions import (
    IsOwnerOrReadOnly, IsAdminUser, HasRolePermission, IsModerator,
    IsContentModerator, IsUserModerator, CanModerateUsers, CanModerateContent,
    CanViewAuditLogs, CanManageSystem
)
import logging
import re
import hashlib
import hmac
import json
from time import time

logger = logging.getLogger('api')


def ratelimit_key_user_or_ip(request):
    """Rate limit key that uses user when authenticated, otherwise IP."""
    if request.user and request.user.is_authenticated:
        return str(request.user.id)
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')


# Health Check View
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Comprehensive health check endpoint for monitoring"""
    from django.db import connection
    from django.core.cache import cache
    from django.conf import settings
    import psutil
    import os

    health_status = {
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'services': {},
        'metrics': {},
    }

    # Database check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status['services']['database'] = 'healthy'
    except Exception as e:
        health_status['services']['database'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'

    # Cache check
    try:
        cache.set('health_check', 'ok', 10)
        cache_value = cache.get('health_check')
        if cache_value == 'ok':
            health_status['services']['cache'] = 'healthy'
        else:
            health_status['services']['cache'] = 'unhealthy: cache not working'
            health_status['status'] = 'unhealthy'
    except Exception as e:
        health_status['services']['cache'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'

    # File system check
    try:
        media_root = settings.MEDIA_ROOT
        test_file = os.path.join(media_root, 'health_check.tmp')
        with open(test_file, 'w') as f:
            f.write('health_check')
        os.remove(test_file)
        health_status['services']['filesystem'] = 'healthy'
    except Exception as e:
        health_status['services']['filesystem'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'

    # System metrics
    try:
        health_status['metrics'] = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else None,
        }
    except Exception as e:
        health_status['metrics'] = {'error': str(e)}

    # Application metrics
    try:
        health_status['app_metrics'] = {
            'total_users': User.objects.count(),
            'total_scans': DetectionResult.objects.count(),
            'active_subscriptions': Subscription.objects.filter(
                status='active',
                is_paid=True,
                end_date__gt=timezone.now()
            ).count(),
            'pending_payments': Payment.objects.filter(status='pending').count(),
        }
    except Exception as e:
        health_status['app_metrics'] = {'error': str(e)}

    status_code = 200 if health_status['status'] == 'healthy' else 503
    return Response(health_status, status=status_code)


@api_view(['GET'])
@permission_classes([AllowAny])
def readiness_check(request):
    """Kubernetes readiness probe - checks if app can serve traffic"""
    try:
        # Quick database check
        User.objects.exists()
        return Response({'status': 'ready'}, status=200)
    except Exception:
        return Response({'status': 'not ready'}, status=503)


@api_view(['GET'])
@permission_classes([AllowAny])
def liveness_check(request):
    """Kubernetes liveness probe - checks if app is running"""
    return Response({'status': 'alive'}, status=200)


# Authentication Views
@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def register(request):
    """User registration endpoint"""
    try:
        username = sanitize_string(request.data.get('username'), max_length=150)
        email = sanitize_string(request.data.get('email'), max_length=254)
        password = request.data.get('password')
        first_name = sanitize_string(request.data.get('first_name', ''), max_length=150)
        last_name = sanitize_string(request.data.get('last_name', ''), max_length=150)
        
        if not username or not email or not password:
            return Response(
                {'error': 'Username, email, and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate email domain
        if not validate_email_domain(email):
            return Response(
                {'error': 'Invalid email domain'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Additional password validation
        if len(password) < 12:
            return Response(
                {'error': 'Password must be at least 12 characters long'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            validate_password(password)
        except Exception as password_error:
            return Response(
                {'error': str(password_error)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if User.objects.filter(username=username).exists():
            return Response(
                {'error': 'Username already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'Email already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Create user profile
        UserProfile.objects.create(user=user)
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='20/m', method='POST', block=True)
@ratelimit(key=ratelimit_key_user_or_ip, rate='100/h', method='POST', block=True)
def login(request):
    """User login endpoint"""
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response(
                {'error': 'Username and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = User.objects.filter(username=username).first()
        
        if not user or not user.check_password(password):
            # Log failed login attempt
            AuditLog.objects.create(
                user=user if user else None,
                action_type='failed_login',
                description=f'Failed login attempt for username: {username}',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
            )
            return Response(
                {'error': 'Invalid username or password'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Check if user has MFA enabled and is admin
        mfa_required = False
        if user.is_staff:
            try:
                mfa_settings = MFASettings.objects.get(user=user)
                mfa_required = mfa_settings.mfa_enabled
            except MFASettings.DoesNotExist:
                # For admin users, MFA should be required but we'll allow login for now
                # In production, you might want to enforce MFA setup for admins
                pass
        
        # Log successful login
        AuditLog.objects.create(
            user=user,
            action_type='login',
            description='User logged in successfully',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )
        
        if mfa_required:
            # Return MFA challenge instead of tokens
            return Response({
                'mfa_required': True,
                'mfa_method': MFASettings.objects.get(user=user).mfa_method,
                'user': UserSerializer(user).data,
            })
        else:
            # Generate tokens for non-MFA users
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='10/m', method='POST', block=True)
@ratelimit(key=ratelimit_key_user_or_ip, rate='30/h', method='POST', block=True)
def social_login(request):
    """Login or register users through Google/Facebook social authentication."""
    provider = sanitize_string(request.data.get('provider', ''), max_length=50).lower()
    access_token = request.data.get('access_token')
    id_token = request.data.get('id_token')
    credential = request.data.get('credential')

    if provider not in ['google', 'facebook']:
        return Response(
            {'error': 'Unsupported social provider'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        if access_token and access_token.startswith('mock_') and not settings.DEBUG:
            return Response(
                {'error': 'Mock tokens are only permitted in development mode'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Handle mock tokens in development mode
        if settings.DEBUG and access_token and access_token.startswith('mock_'):
            provider_id = f"{provider}_{int(access_token.split('_')[-1])}"
            email = f"test_{provider}_{int(access_token.split('_')[-1])%10000}@testdomain.local"
            name = f"Test {provider.capitalize()} User"
            user_info = {
                'email': email,
                'name': name,
                'provider_id': provider_id,
            }
        elif provider == 'google':
            if credential:
                id_token = credential
            if not id_token and not access_token:
                return Response(
                    {'error': 'Google provider requires id_token or access_token'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user_info = get_google_user_info(id_token=id_token, access_token=access_token)
        else:
            if not access_token:
                return Response(
                    {'error': 'Facebook provider requires access_token'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user_info = get_facebook_user_info(access_token)

        email = user_info.get('email')
        name = user_info.get('name')
        provider_id = user_info.get('provider_id')

        if not email:
            return Response(
                {'error': 'Unable to retrieve email from social provider'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.filter(email=email).first()
        if not user:
            username = build_social_username(email, provider)
            username_base = username
            suffix = 1
            while User.objects.filter(username=username).exists():
                username = f"{username_base}_{suffix}"
                suffix += 1

            user = User.objects.create_user(
                username=username,
                email=email,
                password=User.objects.make_random_password(),
                first_name=name.split(' ')[0] if name else '',
                last_name=' '.join(name.split(' ')[1:]) if name and len(name.split(' ')) > 1 else '',
            )
            user.set_unusable_password()
            user.save()
            UserProfile.objects.create(user=user)

        refresh = RefreshToken.for_user(user)
        AuditLog.objects.create(
            user=user,
            action_type='login',
            description=f'Social login via {provider}',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            metadata={'provider': provider, 'provider_id': provider_id}
        )

        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'provider': provider,
        })

    except Exception as e:
        import traceback
        error_msg = str(e)
        logger.error(f'Social login failed for {provider}: {error_msg}')
        logger.error(f'Traceback: {traceback.format_exc()}')
        
        # In development, include error details; in production, keep it generic
        if settings.DEBUG:
            response_data = {'error': 'Social login failed', 'details': error_msg}
        else:
            response_data = {'error': 'Social login failed'}
        
        return Response(
            response_data,
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='10/m', method='POST', block=True)
@ratelimit(key=ratelimit_key_user_or_ip, rate='30/h', method='POST', block=True)
def login_complete_mfa(request):
    username = request.data.get('username')
    token = request.data.get('token')
    method = request.data.get('method', 'totp')

    if not username or not token:
        return Response(
            {'error': 'Username and token are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(username=username)
        token_valid = False

        if method == 'totp':
            from django_otp.plugins.otp_totp.models import TOTPDevice
            devices = TOTPDevice.objects.filter(user=user, confirmed=True)
            for device in devices:
                if device.verify_token(token):
                    token_valid = True
                    break
        elif method == 'sms':
            stored_code = request.session.get('mfa_login_code')
            token_valid = (stored_code == token)
            if token_valid:
                del request.session['mfa_login_code']
        else:
            return Response(
                {'error': 'Invalid MFA method'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not token_valid:
            AuditLog.objects.create(
                user=user,
                action_type='failed_login',
                description=f'Failed MFA verification for {method}',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
            )
            return Response(
                {'error': 'Invalid MFA token'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)
        AuditLog.objects.create(
            user=user,
            action_type='login',
            description=f'Successful login with {method} MFA',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )

        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f'Failed to complete MFA login: {str(e)}')
        return Response(
            {'error': 'Failed to complete MFA login'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='5/m', method='POST', block=True)
@ratelimit(key=ratelimit_key_user_or_ip, rate='20/h', method='POST', block=True)
def request_password_reset(request):
    """Request a password reset email."""
    email = sanitize_string(request.data.get('email'), max_length=254)
    if not email:
        return Response(
            {'error': 'Email is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = User.objects.filter(email=email).first()
    if user:
        reset_token = generate_password_reset_token(user)
        uid = encode_uid(user)
        EmailService.send_password_reset_email(user, f"{uid}:{reset_token}")
        AuditLog.objects.create(
            user=user,
            action_type='password_change',
            description='Password reset requested',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )

    return Response({
        'message': 'If the email exists, a password reset link has been sent.'
    })


@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='5/m', method='POST', block=True)
@ratelimit(key=ratelimit_key_user_or_ip, rate='20/h', method='POST', block=True)
def confirm_password_reset(request):
    """Confirm password reset with token and set a new password."""
    token_payload = request.data.get('token')
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')

    if not token_payload or not new_password or not confirm_password:
        return Response(
            {'error': 'Token, new password, and confirmation are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if new_password != confirm_password:
        return Response(
            {'error': 'New password and confirmation do not match.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        uidb64, token = token_payload.split(':', 1)
    except ValueError:
        return Response(
            {'error': 'Invalid token format.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    uid = decode_uid(uidb64)
    if not uid:
        return Response(
            {'error': 'Invalid password reset token.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(pk=uid)
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    if not verify_password_reset_token(user, token):
        return Response(
            {'error': 'Invalid or expired password reset token.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        validate_password(new_password, user)
        user.set_password(new_password)
        user.save()

        AuditLog.objects.create(
            user=user,
            action_type='password_change',
            description='Password reset completed successfully',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )

        return Response({'message': 'Password has been reset successfully.'})
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Allow users to change their password with history enforcement"""
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')

    if not all([old_password, new_password, confirm_password]):
        return Response(
            {'error': 'Old password, new password, and confirmation are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if new_password != confirm_password:
        return Response(
            {'error': 'New password and confirmation do not match.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = request.user
    if not user.check_password(old_password):
        return Response(
            {'error': 'Old password is incorrect.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        validate_password(new_password, user)
        user.set_password(new_password)
        user.save()

        AuditLog.objects.create(
            user=user,
            action_type='password_change',
            description='User changed password successfully',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )

        return Response({'message': 'Password updated successfully'})
    except Exception as e:
        logger.error(f'Failed to change password: {str(e)}')
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """User logout endpoint"""
    return Response({'message': 'Logged out successfully'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user(request):
    """Get current user information"""
    user = request.user
    profile = user.profile
    
    return Response({
        'user': UserSerializer(user).data,
        'profile': UserProfileSerializer(profile).data,
    })


# Detection Views
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@ratelimit(key='user', rate='20/h', method='POST', block=True)
def predict(request):
    """Main prediction endpoint - detects plant or animal disease"""
    try:
        # Check if user can make predictions
        try:
            trial = Trial.objects.get(user=request.user)
            can_use_trial = trial.status == 'active' and trial.attempts_used < trial.max_attempts
        except Trial.DoesNotExist:
            can_use_trial = True  # New user can use trial
        
        # Check for active subscription
        active_subscription = Subscription.objects.filter(
            user=request.user,
            status='active',
            is_paid=True,
            end_date__gt=timezone.now()
        ).exists()
        
        # Check if admin has allowed user without subscription
        user_profile = request.user.profile
        admin_allowed = getattr(user_profile, 'admin_allowed_access', False)
        
        can_predict = can_use_trial or active_subscription or admin_allowed
        
        if not can_predict:
            return Response(
                {'error': 'Trial expired. Please subscribe to continue using the system.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if 'image' not in request.FILES:
            return Response(
                {'error': 'Image file is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        subject_type = request.data.get('subject_type')
        if subject_type not in ['plant', 'animal']:
            return Response(
                {'error': 'subject_type must be "plant" or "animal"'},
                status=status.HTTP_400_BAD_REQUEST
            )

        image_file = request.FILES['image']
        try:
            validate_file_upload(
                image_file,
                allowed_types=['image/jpeg', 'image/png'],
                max_size=5 * 1024 * 1024,
            )
        except Exception as e:
            return Response(
                {'error': f'Invalid image upload: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        mode = request.data.get('mode', 'real')
        if mode not in ['real', 'demo']:
            return Response(
                {'error': 'Invalid mode. Must be real or demo'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Run ML detection with selected mode
        detection_result = MockMLDetector.detect(image_file, subject_type, mode)

        # Save detection result to database
        result = DetectionResult.objects.create(
            user=request.user,
            image=image_file,
            subject_type=subject_type,
            disease=detection_result['disease'],
            disease_name=detection_result['disease_name'],
            confidence=detection_result['confidence'],
            severity=detection_result['severity'],
            treatment=detection_result['treatment'],
            prevention=detection_result['prevention'],
            notes=detection_result.get('notes', ''),
        )
        
        # Update user profile scan count
        profile = request.user.profile
        profile.total_scans += 1
        profile.save()
        
        # Update system statistics
        stats, _ = SystemStatistics.objects.get_or_create(pk=1)
        stats.total_scans += 1
        if subject_type == 'plant':
            stats.plant_scans += 1
        else:
            stats.animal_scans += 1
        stats.save()
        
        return Response(
            DetectionResultSerializer(result).data,
            status=status.HTTP_201_CREATED
        )
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class PlantViewSet(viewsets.ModelViewSet):
    """Plant species management"""
    queryset = Plant.objects.all()
    serializer_class = PlantSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAdminUser()]


class AnimalViewSet(viewsets.ModelViewSet):
    """Livestock species management"""
    queryset = Animal.objects.all()
    serializer_class = AnimalSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAdminUser()]


class DiseaseViewSet(viewsets.ModelViewSet):
    """Disease management"""
    queryset = Disease.objects.all()
    serializer_class = DiseaseDetailSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DiseaseDetailSerializer
        return DiseaseSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAdminUser()]
    
    @action(detail=False, methods=['get'])
    def plant_diseases(self, request):
        """Get all plant diseases"""
        diseases = Disease.objects.filter(subject_type='plant')
        serializer = self.get_serializer(diseases, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def animal_diseases(self, request):
        """Get all animal diseases"""
        diseases = Disease.objects.filter(subject_type='animal')
        serializer = self.get_serializer(diseases, many=True)
        return Response(serializer.data)


class DetectionResultViewSet(viewsets.ModelViewSet):
    """User detection results management"""
    serializer_class = DetectionResultSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Users only see their own results"""
        return DetectionResult.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DetectionResultCreateSerializer
        return DetectionResultSerializer
    
    def perform_create(self, serializer):
        """Save detection with current user"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_scans(self, request):
        """Get current user's all scans"""
        scans = self.get_queryset()
        serializer = self.get_serializer(scans, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def plant_scans(self, request):
        """Get current user's plant scans"""
        scans = self.get_queryset().filter(subject_type='plant')
        serializer = self.get_serializer(scans, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def animal_scans(self, request):
        """Get current user's animal scans"""
        scans = self.get_queryset().filter(subject_type='animal')
        serializer = self.get_serializer(scans, many=True)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """Delete a scan result"""
        instance = self.get_object()
        if instance.user != request.user:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)


class UserProfileViewSet(viewsets.ModelViewSet):
    """User profile management"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Users only see their own profile"""
        return UserProfile.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_profile(self, request):
        """Get current user's profile"""
        profile = request.user.profile
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """Update current user's profile"""
        profile = request.user.profile
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """User session management"""
    serializer_class = UserSessionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Users only see their own active sessions"""
        return UserSession.get_active_sessions(self.request.user)
    
    @action(detail=True, methods=['post'])
    def terminate(self, request, pk=None):
        """Terminate a specific session"""
        try:
            session = self.get_object()
            
            # Don't allow terminating current session
            if session.session_key == request.session.session_key:
                return Response(
                    {'error': 'Cannot terminate current session'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Log the action
            AuditLog.objects.create(
                user=request.user,
                action_type='admin_action',
                description=f'Terminated session from {session.ip_address}',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT'),
                metadata={'terminated_session_id': str(session.id)}
            )
            
            session.delete()
            return Response({'message': 'Session terminated successfully'})
            
        except UserSession.DoesNotExist:
            return Response(
                {'error': 'Session not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def terminate_all_other(self, request):
        """Terminate all sessions except current one"""
        current_session_key = request.session.session_key
        sessions_terminated = UserSession.objects.filter(
            user=request.user
        ).exclude(session_key=current_session_key).delete()[0]
        
        # Log the action
        AuditLog.objects.create(
            user=request.user,
            action_type='admin_action',
            description=f'Terminated {sessions_terminated} other sessions',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            metadata={'sessions_terminated': sessions_terminated}
        )
        
        return Response({
            'message': f'Terminated {sessions_terminated} sessions successfully'
        })


class RoleViewSet(viewsets.ModelViewSet):
    """Role management for RBAC"""
    queryset = Role.objects.filter(is_active=True)
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, CanManageSystem]
    
    @action(detail=True, methods=['post'])
    def assign_to_user(self, request, pk=None):
        """Assign role to a user"""
        role = self.get_object()
        user_id = request.data.get('user_id')
        expires_at = request.data.get('expires_at')
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if user already has this role
        existing_role = UserRole.objects.filter(
            user=user, 
            role=role, 
            is_active=True
        ).first()
        
        if existing_role:
            return Response(
                {'error': 'User already has this role'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_role = UserRole.objects.create(
            user=user,
            role=role,
            assigned_by=request.user,
            expires_at=expires_at
        )
        
        # Log the action
        AuditLog.objects.create(
            user=request.user,
            action_type='admin_action',
            description=f'Assigned role "{role.name}" to user {user.username}',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            metadata={'assigned_role_id': str(user_role.id), 'target_user_id': user_id}
        )
        
        serializer = UserRoleSerializer(user_role)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def remove_from_user(self, request, pk=None):
        """Remove role from a user"""
        role = self.get_object()
        user_id = request.data.get('user_id')
        
        try:
            user = User.objects.get(id=user_id)
            user_role = UserRole.objects.get(user=user, role=role, is_active=True)
        except (User.DoesNotExist, UserRole.DoesNotExist):
            return Response(
                {'error': 'User role assignment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        user_role.is_active = False
        user_role.save()
        
        # Log the action
        AuditLog.objects.create(
            user=request.user,
            action_type='admin_action',
            description=f'Removed role "{role.name}" from user {user.username}',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            metadata={'removed_role_id': str(user_role.id), 'target_user_id': user_id}
        )
        
        return Response({'message': 'Role removed successfully'})


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """Permission management for RBAC"""
    queryset = Permission.objects.filter(is_active=True)
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, CanManageSystem]


class UserRoleViewSet(viewsets.ModelViewSet):
    """User role assignments management"""
    queryset = UserRole.objects.filter(is_active=True).select_related('user', 'role', 'assigned_by')
    serializer_class = UserRoleSerializer
    permission_classes = [IsAuthenticated, CanManageSystem]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user_id = self.request.query_params.get('user_id')
        role_id = self.request.query_params.get('role_id')
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if role_id:
            queryset = queryset.filter(role_id=role_id)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a user role assignment"""
        user_role = self.get_object()
        user_role.is_active = False
        user_role.save()
        
        # Log the action
        AuditLog.objects.create(
            user=request.user,
            action_type='admin_action',
            description=f'Deactivated role assignment "{user_role.role.name}" for user {user_role.user.username}',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            metadata={'deactivated_role_id': str(user_role.id)}
        )
        
        return Response({'message': 'Role assignment deactivated'})


class SystemStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    """System-wide statistics"""
    queryset = SystemStatistics.objects.all()
    serializer_class = SystemStatisticsSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get system statistics"""
        stats, _ = SystemStatistics.objects.get_or_create(pk=1)
        serializer = self.get_serializer(stats)
        return Response(serializer.data)


# Admin views
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@ratelimit(key='ip', rate='10/h')  # Prevent abuse of user enumeration
def admin_users(request):
    """Get all users or create a new user (admin only)"""
    if not request.user.is_staff:
        return Response(
            {'error': 'Admin access required'},
            status=status.HTTP_403_FORBIDDEN
        )

    if request.method == 'GET':
        users = User.objects.all().select_related('profile')
        serializer = AdminUserSerializer(users, many=True)
        # Log admin enumeration
        AuditLog.objects.create(
            user=request.user,
            action_type='admin_action',
            description='Enumerated all users',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        return Response(serializer.data)

    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    first_name = request.data.get('first_name', '')
    last_name = request.data.get('last_name', '')
    user_type = request.data.get('user_type', 'farmer')
    is_staff = bool(request.data.get('is_staff', False))
    is_active = request.data.get('is_active', True)

    if not username or not email or not password:
        return Response(
            {'error': 'Username, email, and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    username = sanitize_string(username, max_length=150)
    email = sanitize_string(email, max_length=254)
    first_name = sanitize_string(first_name, max_length=150)
    last_name = sanitize_string(last_name, max_length=150)

    if not validate_email_domain(email):
        return Response(
            {'error': 'Invalid email domain'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if len(password) < 12:
        return Response(
            {'error': 'Password must be at least 12 characters long'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        validate_password(password)
    except Exception as password_error:
        return Response(
            {'error': str(password_error)},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'Username already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(email=email).exists():
        return Response(
            {'error': 'Email already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        is_active=is_active,
    )
    user.is_staff = is_staff
    user.save()

    UserProfile.objects.create(user=user, user_type=user_type)

    serializer = AdminUserSerializer(user)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
@ratelimit(key='ip', rate='5/h')  # Prevent abuse of user modification
def admin_user_detail(request, user_id):
    """Update or remove a user (admin only)"""
    if not request.user.is_staff:
        return Response(
            {'error': 'Admin access required'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Validate user_id is a valid integer
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        return Response(
            {'error': 'Invalid user ID format'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = User.objects.filter(pk=user_id).first()
    if not user:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        if user == request.user:
            # Log attempted self-deletion
            AuditLog.objects.create(
                user=request.user,
                action_type='admin_action',
                description='Attempted to delete own account',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT'),
                metadata={'target_user_id': str(user_id), 'action': 'delete', 'status': 'rejected'}
            )
            return Response(
                {'error': 'You cannot delete your own account'},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Audit user deletion
        AuditLog.objects.create(
            user=request.user,
            action_type='admin_action',
            description=f'Admin deleted user: {user.username} (ID: {user_id}, Email: {user.email})',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            metadata={'target_user_id': str(user_id), 'action': 'delete', 'target_email': user.email}
        )
        logger.warning(f'Admin {request.user.username} deleted user {user.username} (ID: {user_id})')
        user.delete()
        return Response({'success': True, 'message': 'User deleted'})

    if user == request.user and 'is_staff' in request.data:
        return Response(
            {'error': 'You cannot change your own admin privileges'},
            status=status.HTTP_400_BAD_REQUEST
        )

    changes = []
    if 'is_active' in request.data:
        old_value = user.is_active
        user.is_active = bool(request.data.get('is_active'))
        if old_value != user.is_active:
            changes.append(f'is_active: {old_value} -> {user.is_active}')

    if 'is_staff' in request.data:
        old_value = user.is_staff
        user.is_staff = bool(request.data.get('is_staff'))
        if old_value != user.is_staff:
            changes.append(f'is_staff: {old_value} -> {user.is_staff}')

    if 'is_superuser' in request.data:
        old_value = user.is_superuser
        user.is_superuser = bool(request.data.get('is_superuser'))
        if old_value != user.is_superuser:
            changes.append(f'is_superuser: {old_value} -> {user.is_superuser}')

    if 'first_name' in request.data:
        old_value = user.first_name
        user.first_name = request.data.get('first_name', user.first_name)
        if old_value != user.first_name:
            changes.append(f'first_name: "{old_value}" -> "{user.first_name}"')

    if 'last_name' in request.data:
        old_value = user.last_name
        user.last_name = request.data.get('last_name', user.last_name)
        if old_value != user.last_name:
            changes.append(f'last_name: "{old_value}" -> "{user.last_name}"')

    if 'email' in request.data:
        old_value = user.email
        email_value = sanitize_string(request.data.get('email', user.email), max_length=254)
        if not validate_email_domain(email_value):
            return Response(
                {'error': 'Invalid email domain'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.email = email_value
        if old_value != user.email:
            changes.append(f'email: "{old_value}" -> "{user.email}"')

    user.save()

    profile = getattr(user, 'profile', None)
    if profile and 'user_type' in request.data:
        old_value = profile.user_type
        profile.user_type = request.data.get('user_type', profile.user_type)
        if old_value != profile.user_type:
            changes.append(f'user_type: "{old_value}" -> "{profile.user_type}"')
        profile.save()

    if changes:
        logger.info(f'Admin {request.user.username} updated user {user.username} (ID: {user_id}): {", ".join(changes)}')

    serializer = AdminUserSerializer(user)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_stats(request):
    """Get admin statistics"""
    if not request.user.is_staff:
        return Response(
            {'error': 'Admin access required'},
            status=status.HTTP_403_FORBIDDEN
        )

    stats, _ = SystemStatistics.objects.get_or_create(pk=1)
    stats.total_users = User.objects.count()
    stats.diseases_detected = DetectionResult.objects.values('disease_name').distinct().count()
    stats.save()

    serializer = SystemStatisticsSerializer(stats)
    return Response(serializer.data)


# Trial and Subscription Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_trial_status(request):
    """Get user's trial status"""
    try:
        trial = Trial.objects.get(user=request.user)
    except Trial.DoesNotExist:
        # Create trial if it doesn't exist
        trial = Trial.objects.create(user=request.user)
    
    serializer = TrialSerializer(trial)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def increment_trial_attempts(request):
    """Increment trial attempts after a successful prediction"""
    try:
        trial = Trial.objects.get(user=request.user)
    except Trial.DoesNotExist:
        trial = Trial.objects.create(user=request.user)
    
    if trial.status == 'active' and trial.attempts_used < trial.max_attempts:
        trial.attempts_used += 1
        trial.save()
        
        return Response({
            'attempts_used': trial.attempts_used,
            'max_attempts': trial.max_attempts,
            'can_use_trial': trial.attempts_used < trial.max_attempts,
            'message': f'Trial attempt {trial.attempts_used}/{trial.max_attempts}'
        })
    else:
        return Response({
            'error': 'Trial expired. Please subscribe to continue using the system.',
            'can_use_trial': False
        }, status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_can_predict(request):
    """Check if user can make predictions (trial or subscription)"""
    trial = None
    try:
        trial = Trial.objects.get(user=request.user)
        can_use_trial = trial.status == 'active' and trial.attempts_used < trial.max_attempts
    except Trial.DoesNotExist:
        can_use_trial = True  # New user can use trial
    
    # Check for active subscription
    active_subscription = Subscription.objects.filter(
        user=request.user,
        status='active',
        is_paid=True,
        end_date__gt=timezone.now()
    ).exists()
    
    # Check if admin has allowed user without subscription
    user_profile = request.user.profile
    admin_allowed = getattr(user_profile, 'admin_allowed_access', False)
    
    can_predict = can_use_trial or active_subscription or admin_allowed
    
    return Response({
        'can_predict': can_predict,
        'has_trial_access': can_use_trial,
        'has_active_subscription': active_subscription,
        'admin_allowed': admin_allowed,
        'trial_status': {
            'attempts_used': trial.attempts_used if trial else 0,
            'max_attempts': trial.max_attempts if trial else 5
        } if trial else None
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@ratelimit(key='user', rate='20/h', method='POST', block=True)
def create_subscription(request):
    """Create a new subscription with mobile money payment"""
    plan = sanitize_string(request.data.get('plan', ''), max_length=20)
    payment_method = sanitize_string(request.data.get('payment_method', ''), max_length=20)
    mobile_number = sanitize_string(request.data.get('mobile_number', ''), max_length=20)

    if not plan or not payment_method or not mobile_number:
        return Response(
            {'error': 'Plan, payment method, and mobile number are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if plan not in ['daily', 'weekly', 'monthly']:
        return Response(
            {'error': 'Invalid plan. Must be daily, weekly, or monthly'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if payment_method not in ['mtn', 'airtel']:
        return Response(
            {'error': 'Invalid payment method. Must be mtn or airtel'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validate Uganda mobile number formats
    # Valid formats: 0700123456, +256700123456, 256700123456
    if not re.match(r'^(\+?256|0)?\d{9}$|^(\+?256|0)\d{7,15}$', mobile_number):
        return Response(
            {'error': 'Invalid mobile number format. Use format like 0700123456 or +256700123456'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Calculate amount based on plan
    if plan == 'daily':
        amount = 3000
    elif plan == 'weekly':
        amount = 10000
    else:  # monthly
        amount = 20000

    plan_data = {
        'plan': plan,
        'payment_method': payment_method,
        'mobile_number': mobile_number,
        'amount': amount
    }

    try:
        # Process payment via mobile money
        if payment_method == 'airtel':
            result = MobileMoneyService.process_subscription_payment(request.user, plan_data)
        else:
            return Response(
                {'error': 'Currently only Airtel payments are supported'},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription = result['subscription']
        serializer = SubscriptionSerializer(subscription)

        return Response({
            'subscription': serializer.data,
            'collection_transaction': result['collection_transaction'],
            'disbursement_transaction': result['disbursement_transaction'],
            'message': f'Payment processed successfully! {amount} UGX sent to Airtel number {MobileMoneyService.TARGET_AIRTEL_NUMBER}',
            'target_number': MobileMoneyService.TARGET_AIRTEL_NUMBER
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f'Failed to create subscription: {str(e)}')
        return Response(
            {'error': f'Payment processing failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@ratelimit(key='user', rate='20/h', method='POST', block=True)
def confirm_payment(request):
    """Confirm payment and activate subscription"""
    payment_id = request.data.get('payment_id')
    transaction_id = request.data.get('transaction_id', '')
    
    if not payment_id:
        return Response(
            {'error': 'Payment ID is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        payment = Payment.objects.get(id=payment_id, user=request.user)
    except Payment.DoesNotExist:
        return Response(
            {'error': 'Payment not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Mark payment as completed
    payment.status = 'completed'
    if transaction_id:
        payment.transaction_id = transaction_id
    payment.save()
    
    # Mark subscription as paid
    subscription = payment.subscription
    subscription.is_paid = True
    subscription.save()
    
    # Update user trial status if they convert from trial
    try:
        trial = Trial.objects.get(user=request.user)
        trial.status = 'converted'
        trial.save()
    except Trial.DoesNotExist:
        pass
    
    serializer = SubscriptionSerializer(subscription)
    return Response({
        'subscription': serializer.data,
        'message': f'Payment confirmed! Subscription activated until {subscription.end_date}'
    })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def subscriptions(request):
    """Get user's subscriptions or create new subscription"""
    if request.method == 'GET':
        subscriptions = Subscription.objects.filter(user=request.user).order_by('-created_at')
        serializer = SubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data)
    else:
        return create_subscription(request)


# Stripe Payment Views
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@ratelimit(key='user', rate='20/h', method='POST', block=True)
def create_payment_intent(request):
    """Create a Stripe payment intent for subscription"""
    plan = request.data.get('plan')

    if not plan or plan not in SUBSCRIPTION_PLANS:
        return Response(
            {'error': 'Valid plan is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        plan_info = SUBSCRIPTION_PLANS[plan]
        amount = plan_info['price']

        # Create payment intent
        payment_data = StripePaymentService.create_payment_intent(
            amount=amount,
            currency='usd',
            metadata={
                'user_id': str(request.user.id),
                'plan': plan,
                'user_email': request.user.email,
            }
        )

        return Response({
            'client_secret': payment_data['client_secret'],
            'payment_intent_id': payment_data['payment_intent_id'],
            'amount': amount,
            'currency': 'usd',
            'plan': plan,
        })

    except Exception as e:
        logger.error(f'Failed to create payment intent: {str(e)}')
        return Response(
            {'error': 'Failed to create payment intent'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='30/m')  # Prevent webhook spam
def stripe_webhook(request):
    """Handle Stripe webhook events with idempotency and security"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event_data = json.loads(payload)
        event_id = event_data.get('id')
        event_type = event_data.get('type')
    except (json.JSONDecodeError, ValueError):
        logger.error('Stripe webhook: Invalid JSON payload')
        return Response({'error': 'Invalid JSON'}, status=status.HTTP_400_BAD_REQUEST)

    if not event_id:
        return Response({'error': 'Invalid event'}, status=status.HTTP_400_BAD_REQUEST)

    # Idempotency check to prevent duplicate processing
    from django.core.cache import cache
    webhook_key = f'stripe_webhook_{event_id}'
    
    if cache.get(webhook_key):
        logger.warning(f'Stripe webhook duplicate: {event_id}')
        return Response({'status': 'success'})

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
        cache.set(webhook_key, True, 3600)
        
        logger.info(f'Stripe webhook: {event_type} (ID: {event_id})')
        AuditLog.objects.create(
            user=None,
            action_type='webhook',
            description=f'Stripe webhook processed: {event_type}',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            metadata={'event_id': event_id, 'event_type': event_type}
        )

        StripePaymentService.process_webhook_event(event)
        return Response({'status': 'success'})

    except ValueError as e:
        return Response({'error': 'Invalid payload'}, status=status.HTTP_400_BAD_REQUEST)
    except stripe.error.SignatureVerificationError as e:
        logger.warning(f'Stripe webhook signature failed from {request.META.get("REMOTE_ADDR")}')
        AuditLog.objects.create(
            user=None,
            action_type='webhook',
            description='STRIPE WEBHOOK SIGNATURE VERIFICATION FAILED - POTENTIAL ATTACK',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            metadata={'event_id': event_id if event_id else 'unknown'}
        )
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        logger.error(f'Stripe webhook error: {str(e)}')
        return Response({'error': 'Processing failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_stripe_payment(request):
    """Confirm Stripe payment and create subscription"""
    payment_intent_id = request.data.get('payment_intent_id')
    plan = request.data.get('plan')

    if not payment_intent_id or not plan:
        return Response(
            {'error': 'Payment intent ID and plan are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Confirm the payment
        payment_result = StripePaymentService.confirm_payment_intent(payment_intent_id)

        if payment_result['status'] == 'succeeded':
            # Create subscription
            subscription = StripePaymentService.create_subscription(
                user=request.user,
                plan_data={
                    'plan': plan,
                    'amount': payment_result['amount'],
                    'payment_method': 'stripe',
                    'transaction_id': payment_intent_id,
                }
            )

            serializer = SubscriptionSerializer(subscription)
            return Response({
                'subscription': serializer.data,
                'message': f'Payment successful! Subscription activated until {subscription.end_date}'
            })
        else:
            return Response(
                {'error': 'Payment not completed'},
                status=status.HTTP_400_BAD_REQUEST
            )

    except Exception as e:
        logger.error(f'Failed to confirm Stripe payment: {str(e)}')
        return Response(
            {'error': 'Failed to confirm payment'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


        return Response(
            {'error': 'Failed to confirm payment'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Data Management Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_user_data(request):
    """Export user's personal data"""
    format_type = request.query_params.get('format', 'json')

    if format_type not in ['json', 'csv']:
        return Response(
            {'error': 'Format must be json or csv'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        data = DataManagementService.export_user_data(request.user, format_type)

        if format_type == 'json':
            response = HttpResponse(data, content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="user_data_{request.user.username}.json"'
        else:
            response = HttpResponse(data, content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="user_data_{request.user.username}.csv"'

        return response

    except Exception as e:
        logger.error(f'Failed to export user data: {str(e)}')
        return Response(
            {'error': 'Failed to export data'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_user_account(request):
    """Delete user account and all associated data (GDPR compliance)"""
    confirmation = request.data.get('confirmation')

    if confirmation != f"DELETE-{request.user.username}":
        return Response(
            {'error': 'Invalid confirmation. Please provide exact confirmation text.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        DataManagementService.delete_user_data(request.user)

        # Note: This will fail because the user is deleted, but that's expected
        return Response({
            'message': 'Account and all associated data have been permanently deleted.'
        })

    except Exception as e:
        logger.error(f'Failed to delete user account: {str(e)}')
        return Response(
            {'error': 'Failed to delete account'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_detection_history(request):
    """Export user's detection history"""
    format_type = request.query_params.get('format', 'csv')
    subject_type = request.query_params.get('subject_type')
    date_from = request.query_params.get('date_from')
    date_to = request.query_params.get('date_to')

    if format_type not in ['json', 'csv']:
        return Response(
            {'error': 'Format must be json or csv'},
            status=status.HTTP_400_BAD_REQUEST
        )

    filters = {'user_id': request.user.id}
    if subject_type:
        filters['subject_type'] = subject_type
    if date_from:
        filters['date_from'] = date_from
    if date_to:
        filters['date_to'] = date_to

    try:
        data = DataManagementService.export_detection_results(format_type, **filters)

        if format_type == 'json':
            response = HttpResponse(data, content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="detection_history_{request.user.username}.json"'
        else:
            response = HttpResponse(data, content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="detection_history_{request.user.username}.csv"'

        return response

    except Exception as e:
        logger.error(f'Failed to export detection history: {str(e)}')
        return Response(
            {'error': 'Failed to export detection history'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Admin Data Management Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@ratelimit(key='ip', rate='5/h')  # Prevent abuse of data export
def admin_export_data(request):
    """Admin: Export system data with audit logging"""
    if not request.user.is_staff:
        return Response(
            {'error': 'Admin access required'},
            status=status.HTTP_403_FORBIDDEN
        )

    data_type = request.query_params.get('type', 'detections')
    format_type = request.query_params.get('format', 'csv')

    if data_type not in ['detections', 'backup']:
        return Response(
            {'error': 'Type must be detections or backup'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if format_type not in ['json', 'csv']:
        return Response(
            {'error': 'Format must be json or csv'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Log export action
        AuditLog.objects.create(
            user=request.user,
            action_type='admin_action',
            description=f'Exported system data: type={data_type}, format={format_type}',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            metadata={'export_type': data_type, 'export_format': format_type}
        )
        
        if data_type == 'detections':
            data = DataManagementService.export_detection_results(format_type)
        else:  # backup
            data = DataManagementService.create_backup()
            format_type = 'json'

        if format_type == 'json':
            response = HttpResponse(data, content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="system_{data_type}_{timezone.now().date()}.json"'
        else:
            response = HttpResponse(data, content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="system_{data_type}_{timezone.now().date()}.csv"'

        return response

    except Exception as e:
        logger.error(f'Failed to export admin data: {str(e)}')
        AuditLog.objects.create(
            user=request.user,
            action_type='admin_action',
            description=f'Data export failed: {data_type}',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            metadata={'error': str(e), 'export_type': data_type}
        )
        return Response(
            {'error': 'Failed to export data'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


        return Response(
            {'error': 'Failed to export data'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


        return Response(
            {'error': 'Failed to export data'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Analytics & Metrics Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_analytics(request):
    """Get analytics for the current user"""
    period = request.query_params.get('period', '30d')

    if period not in ['7d', '30d', '90d']:
        return Response(
            {'error': 'Period must be 7d, 30d, or 90d'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        analytics = AnalyticsService.get_user_analytics(request.user, period)
        return Response(analytics)

    except Exception as e:
        logger.error(f'Failed to get user analytics: {str(e)}')
        return Response(
            {'error': 'Failed to retrieve analytics'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def track_user_action(request):
    """Track user action for analytics"""
    action = request.data.get('action')
    metadata = request.data.get('metadata', {})

    if not action:
        return Response(
            {'error': 'Action is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        AnalyticsService.track_user_action(request.user, action, metadata)
        return Response({'status': 'tracked'})

    except Exception as e:
        logger.error(f'Failed to track user action: {str(e)}')
        return Response(
            {'error': 'Failed to track action'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Admin Analytics Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@ratelimit(key='ip', rate='10/h')  # Rate limit metrics queries
def admin_business_metrics(request):
    """Admin: Get business metrics dashboard"""
    if not request.user.is_staff:
        return Response(
            {'error': 'Admin access required'},
            status=status.HTTP_403_FORBIDDEN
        )

    period = request.query_params.get('period', '30d')

    # Validate period input against whitelist
    if period not in ['7d', '30d', '90d']:
        return Response(
            {'error': 'Period must be 7d, 30d, or 90d'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        metrics = AnalyticsService.get_business_metrics(period)
        # Log metrics access
        AuditLog.objects.create(
            user=request.user,
            action_type='admin_action',
            description=f'Accessed business metrics for period: {period}',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            metadata={'period': period}
        )
        return Response(metrics)

    except Exception as e:
        logger.error(f'Failed to get business metrics: {str(e)}')
        return Response(
            {'error': 'Failed to retrieve metrics'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@ratelimit(key='ip', rate='10/h')  # Rate limit performance metrics queries
def admin_performance_metrics(request):
    """Admin: Get system performance metrics"""
    if not request.user.is_staff:
        return Response(
            {'error': 'Admin access required'},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        metrics = AnalyticsService.get_system_performance_metrics()
        # Log metrics access
        AuditLog.objects.create(
            user=request.user,
            action_type='admin_action',
            description='Accessed system performance metrics',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        return Response(metrics)

    except Exception as e:
        logger.error(f'Failed to get performance metrics: {str(e)}')
        return Response(
            {'error': 'Failed to retrieve performance metrics'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Advanced Admin Features
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@ratelimit(key='ip', rate='3/h')  # Strict rate limit on bulk operations
def admin_bulk_user_action(request):
    """Admin: Perform bulk actions on users"""
    if not request.user.is_staff:
        return Response(
            {'error': 'Admin access required'},
            status=status.HTTP_403_FORBIDDEN
        )

    action = request.data.get('action')
    user_ids = request.data.get('user_ids', [])

    if not action or not user_ids:
        return Response(
            {'error': 'Action and user_ids are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validate action
    if action not in ['activate', 'deactivate', 'delete', 'grant_access', 'revoke_access']:
        return Response(
            {'error': 'Invalid action'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Enforce bulk operation limits to prevent mass destruction
    MAX_BULK_OPERATIONS = 100
    if len(user_ids) > MAX_BULK_OPERATIONS:
        AuditLog.objects.create(
            user=request.user,
            action_type='admin_action',
            description=f'Attempted bulk {action} on {len(user_ids)} users (exceeded limit)',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            metadata={'action': action, 'requested_count': len(user_ids), 'status': 'rejected'}
        )
        return Response(
            {'error': f'Maximum {MAX_BULK_OPERATIONS} users per bulk operation'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validate user_ids are valid integers
    try:
        user_ids = [int(uid) for uid in user_ids]
    except (ValueError, TypeError):
        return Response(
            {'error': 'Invalid user IDs format'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        users = User.objects.filter(id__in=user_ids)
        updated_count = 0
        failed_ids = []

        for user in users:
            if action == 'activate':
                user.is_active = True
                user.save()
                logger.info(f'Admin {request.user.username} activated user {user.username}')
            elif action == 'deactivate':
                user.is_active = False
                user.save()
                logger.info(f'Admin {request.user.username} deactivated user {user.username}')
            elif action == 'delete':
                if user != request.user:  # Can't delete self
                    user.delete()
                    logger.warning(f'Admin {request.user.username} deleted user {user.username}')
                else:
                    failed_ids.append(user.id)
                    continue
            elif action == 'grant_access':
                profile = user.profile
                profile.admin_allowed_access = True
                profile.save()
                logger.info(f'Admin {request.user.username} granted access to user {user.username}')
            elif action == 'revoke_access':
                profile = user.profile
                profile.admin_allowed_access = False
                profile.save()
                logger.info(f'Admin {request.user.username} revoked access from user {user.username}')

            updated_count += 1

        # Log bulk operation
        AuditLog.objects.create(
            user=request.user,
            action_type='admin_action',
            description=f'Performed bulk action "{action}" on {updated_count} users',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            metadata={'action': action, 'count': updated_count, 'failed_ids': failed_ids}
        )

        return Response({
            'message': f'Action "{action}" applied to {updated_count} users',
            'updated_count': updated_count,
            'failed_count': len(failed_ids)
        })

    except Exception as e:
        logger.error(f'Failed to perform bulk user action: {str(e)}')
        AuditLog.objects.create(
            user=request.user,
            action_type='admin_action',
            description=f'Bulk action "{action}" failed: {str(e)}',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            metadata={'action': action, 'error': str(e)}
        )
        return Response(
            {'error': 'Failed to perform bulk action'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@ratelimit(key='ip', rate='2/h')  # Strict rate limit on settings changes
def admin_system_settings(request):
    """Admin: Update system settings with comprehensive validation"""
    if not request.user.is_staff:
        return Response(
            {'error': 'Admin access required'},
            status=status.HTTP_403_FORBIDDEN
        )

    settings_data = request.data.get('settings', {})
    
    if not settings_data:
        return Response(
            {'error': 'Settings data is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate and sanitize settings keys - whitelist approach
    ALLOWED_SETTINGS = ['trial_max_attempts', 'notification_enabled', 'maintenance_mode']
    invalid_keys = [k for k in settings_data.keys() if k not in ALLOWED_SETTINGS]
    
    if invalid_keys:
        return Response(
            {'error': f'Invalid settings keys: {invalid_keys}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Log the settings change attempt
    AuditLog.objects.create(
        user=request.user,
        action_type='admin_action',
        description=f'Admin updated system settings: {list(settings_data.keys())}',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT'),
        metadata={'settings_modified': list(settings_data.keys()), 'values_count': len(settings_data)}
    )

    logger.warning(f'Admin {request.user.username} updated system settings')

    return Response({
        'message': 'System settings updated',
        'settings_applied': list(settings_data.keys())
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@ratelimit(key='ip', rate='3/h')  # Strict rate limit on bulk deletion
def admin_bulk_delete_detections(request):
    """Admin: Bulk delete detection results"""
    if not request.user.is_staff:
        return Response(
            {'error': 'Admin access required'},
            status=status.HTTP_403_FORBIDDEN
        )

    detection_ids = request.data.get('detection_ids', [])
    reason = request.data.get('reason', 'Bulk deletion by admin')

    if not detection_ids:
        return Response(
            {'error': 'detection_ids are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Enforce bulk deletion limits
    MAX_BULK_DELETIONS = 500
    if len(detection_ids) > MAX_BULK_DELETIONS:
        AuditLog.objects.create(
            user=request.user,
            action_type='admin_action',
            description=f'Attempted to bulk delete {len(detection_ids)} detections (exceeded limit)',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            metadata={'action': 'bulk_delete', 'requested_count': len(detection_ids), 'status': 'rejected'}
        )
        return Response(
            {'error': f'Maximum {MAX_BULK_DELETIONS} detections per deletion operation'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validate detection_ids are valid UUIDs or integers
    try:
        detection_ids = [str(did) for did in detection_ids if did]
    except (ValueError, TypeError):
        return Response(
            {'error': 'Invalid detection IDs format'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        detections = DetectionResult.objects.filter(id__in=detection_ids)
        deleted_count = detections.count()

        # Log deletion details
        for detection in detections:
            logger.warning(f'Admin {request.user.username} deleted detection {detection.id} for user {detection.user.username}. Reason: {reason}')

        # Comprehensive audit log
        AuditLog.objects.create(
            user=request.user,
            action_type='admin_action',
            description=f'Admin deleted {deleted_count} detection results. Reason: {sanitize_string(reason, max_length=200)}',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            metadata={'action': 'bulk_delete', 'count': deleted_count, 'reason': reason}
        )

        detections.delete()

        # Update system statistics
        stats, _ = SystemStatistics.objects.get_or_create(pk=1)
        stats.total_scans = max(0, stats.total_scans - deleted_count)
        stats.save()

        return Response({
            'message': f'Deleted {deleted_count} detection results',
            'deleted_count': deleted_count
        })

    except Exception as e:
        logger.error(f'Failed to bulk delete detections: {str(e)}')
        return Response(
            {'error': 'Failed to delete detections'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Admin Endpoints
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@ratelimit(key='ip', rate='15/h')  # Rate limit admin payment enumeration
def admin_payments(request):
    """Admin: Get all payments"""
    if not request.user.is_staff:
        return Response(
            {'error': 'Admin access required'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    filter_status = request.query_params.get('status')
    
    # Validate status filter if provided
    if filter_status and filter_status not in ['pending', 'completed', 'failed']:
        return Response(
            {'error': 'Invalid status filter. Must be: pending, completed, or failed'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    payments = Payment.objects.all().order_by('-created_at')
    if filter_status:
        payments = payments.filter(status=filter_status)
    
    # Log access to payment records
    AuditLog.objects.create(
        user=request.user,
        action_type='admin_action',
        description=f'Viewed payment records (filter: {filter_status or "none"})',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT'),
        metadata={'filter': filter_status, 'count': payments.count()}
    )
    
    serializer = PaymentSerializer(payments, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@ratelimit(key='ip', rate='15/h')  # Rate limit admin subscription enumeration
def admin_subscriptions(request):
    """Admin: Get all subscriptions"""
    if not request.user.is_staff:
        return Response(
            {'error': 'Admin access required'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    filter_status = request.query_params.get('status')
    filter_paid = request.query_params.get('paid')
    
    # Validate status filter
    if filter_status and filter_status not in ['active', 'expired', 'cancelled']:
        return Response(
            {'error': 'Invalid status filter. Must be: active, expired, or cancelled'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate paid filter
    if filter_paid and filter_paid not in ['true', 'false']:
        return Response(
            {'error': 'Invalid paid filter. Must be: true or false'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    subscriptions = Subscription.objects.all().order_by('-created_at')
    if filter_status:
        subscriptions = subscriptions.filter(status=filter_status)
    if filter_paid == 'true':
        subscriptions = subscriptions.filter(is_paid=True)
    elif filter_paid == 'false':
        subscriptions = subscriptions.filter(is_paid=False)
    
    # Log access to subscription records
    AuditLog.objects.create(
        user=request.user,
        action_type='admin_action',
        description=f'Viewed subscription records (status: {filter_status or "any"}, paid: {filter_paid or "any"})',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT'),
        metadata={'filter_status': filter_status, 'filter_paid': filter_paid, 'count': subscriptions.count()}
    )
    
    serializer = SubscriptionSerializer(subscriptions, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@ratelimit(key='ip', rate='10/h')
def admin_allow_user_access(request):
    """Admin: Allow a user to use system without subscription"""
    if not request.user.is_staff:
        return Response(
            {'error': 'Admin access required'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    user_id = request.data.get('user_id')
    allow = request.data.get('allow', True)
    
    if not user_id:
        return Response(
            {'error': 'User ID is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        return Response(
            {'error': 'Invalid user ID format'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not isinstance(allow, bool):
        return Response(
            {'error': 'Allow must be boolean'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(id=user_id)
        profile = user.profile
        old_access = profile.admin_allowed_access
        profile.admin_allowed_access = allow
        profile.save()
        
        AuditLog.objects.create(
            user=request.user,
            action_type='admin_action',
            description=f'Admin access {"granted" if allow else "revoked"} for {user.username}',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            metadata={'target_user_id': str(user_id), 'action': 'access_grant', 'old_value': old_access, 'new_value': allow}
        )
        
        return Response({
            'message': f'User {user.username} access {"allowed" if allow else "revoked"}',
            'user_id': user_id,
            'admin_allowed_access': allow
        })
    except User.DoesNotExist:
        AuditLog.objects.create(
            user=request.user,
            action_type='admin_action',
            description=f'Attempted to modify non-existent user ID {user_id}',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            metadata={'target_user_id': str(user_id), 'status': 'not_found'}
        )
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )


    username = request.data.get('username')
    token = request.data.get('token')
    method = request.data.get('method', 'totp')

    if not username or not token:
        return Response(
            {'error': 'Username and token are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(username=username)

        # Verify MFA token
        if method == 'totp':
            from django_otp.plugins.otp_totp.models import TOTPDevice
            devices = TOTPDevice.objects.filter(user=user, confirmed=True)

            token_valid = False
            for device in devices:
                if device.verify_token(token):
                    token_valid = True
                    break
        elif method == 'sms':
            # For SMS, check session-stored code
            stored_code = request.session.get('mfa_login_code')
            token_valid = (token == stored_code)
            if token_valid:
                del request.session['mfa_login_code']
        else:
            return Response(
                {'error': 'Invalid MFA method'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not token_valid:
            # Log failed MFA attempt
            AuditLog.objects.create(
                user=user,
                action_type='failed_login',
                description=f'Failed MFA verification for {method}',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
            )
            return Response(
                {'error': 'Invalid MFA token'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Generate tokens
        refresh = RefreshToken.for_user(user)

        # Log successful MFA login
        AuditLog.objects.create(
            user=user,
            action_type='login',
            description=f'Successful login with {method} MFA',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )

        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Multi-Factor Authentication (MFA) Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mfa_status(request):
    """Get MFA status for current user"""
    try:
        mfa_settings, created = MFASettings.objects.get_or_create(user=request.user)
        return Response({
            'mfa_enabled': mfa_settings.mfa_enabled,
            'mfa_method': mfa_settings.mfa_method,
            'has_phone': bool(mfa_settings.phone_number),
        })
    except Exception as e:
        logger.error(f'Failed to get MFA status: {str(e)}')
        return Response(
            {'error': 'Failed to retrieve MFA status'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mfa_setup_totp(request):
    """Setup TOTP MFA for current user"""
    try:
        from django_otp.plugins.otp_totp.models import TOTPDevice
        import qrcode
        import io
        import base64

        # Check if user already has MFA enabled
        mfa_settings, created = MFASettings.objects.get_or_create(user=request.user)
        if mfa_settings.mfa_enabled:
            return Response(
                {'error': 'MFA is already enabled'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create TOTP device
        device = TOTPDevice.objects.create(
            user=request.user,
            name=f"{request.user.username}'s TOTP Device",
            confirmed=False
        )

        # Generate QR code
        provisioning_uri = device.config_url
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

        return Response({
            'device_id': device.id,
            'provisioning_uri': provisioning_uri,
            'qr_code': f"data:image/png;base64,{qr_code_base64}",
            'secret': device.bin_key.hex(),
        })

    except Exception as e:
        logger.error(f'Failed to setup TOTP: {str(e)}')
        return Response(
            {'error': 'Failed to setup TOTP'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mfa_verify_totp(request):
    """Verify and enable TOTP MFA"""
    device_id = request.data.get('device_id')
    token = request.data.get('token')

    if not device_id or not token:
        return Response(
            {'error': 'Device ID and token are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        from django_otp.plugins.otp_totp.models import TOTPDevice

        device = TOTPDevice.objects.get(id=device_id, user=request.user)

        if device.verify_token(token):
            device.confirmed = True
            device.save()

            # Update MFA settings
            mfa_settings, created = MFASettings.objects.get_or_create(user=request.user)
            mfa_settings.mfa_enabled = True
            mfa_settings.mfa_method = 'totp'
            mfa_settings.save()

            # Log MFA setup
            AuditLog.objects.create(
                user=request.user,
                action_type='mfa_setup',
                description='TOTP MFA enabled',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
            )

            return Response({
                'message': 'TOTP MFA enabled successfully',
                'mfa_enabled': True,
                'mfa_method': 'totp',
            })
        else:
            return Response(
                {'error': 'Invalid token'},
                status=status.HTTP_400_BAD_REQUEST
            )

    except TOTPDevice.DoesNotExist:
        return Response(
            {'error': 'Device not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f'Failed to verify TOTP: {str(e)}')
        return Response(
            {'error': 'Failed to verify TOTP'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mfa_setup_sms(request):
    """Setup SMS MFA for current user"""
    phone_number = request.data.get('phone_number')

    if not phone_number:
        return Response(
            {'error': 'Phone number is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Validate phone number format (basic validation)
        import re
        if not re.match(r'^\+?1?\d{9,15}$', phone_number):
            return Response(
                {'error': 'Invalid phone number format'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user already has MFA enabled
        mfa_settings, created = MFASettings.objects.get_or_create(user=request.user)
        if mfa_settings.mfa_enabled:
            return Response(
                {'error': 'MFA is already enabled'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate verification code
        import secrets
        verification_code = secrets.token_hex(3).upper()  # 6-character code

        # Store code temporarily (in production, use Redis or similar)
        request.session['sms_verification_code'] = verification_code
        request.session['sms_phone_number'] = phone_number
        request.session.set_expiry(300)  # 5 minutes

        # Send SMS (mock implementation - replace with actual SMS service)
        logger.info(f'SMS verification code for {phone_number}: {verification_code}')

        return Response({
            'message': 'Verification code sent to your phone',
            'phone_number': phone_number,
        })

    except Exception as e:
        logger.error(f'Failed to setup SMS MFA: {str(e)}')
        return Response(
            {'error': 'Failed to setup SMS MFA'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mfa_verify_sms(request):
    """Verify SMS code and enable SMS MFA"""
    code = request.data.get('code')

    if not code:
        return Response(
            {'error': 'Verification code is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        stored_code = request.session.get('sms_verification_code')
        phone_number = request.session.get('sms_phone_number')

        if not stored_code or not phone_number:
            return Response(
                {'error': 'No verification code found. Please restart setup.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if code.upper() == stored_code:
            # Clear session data
            del request.session['sms_verification_code']
            del request.session['sms_phone_number']

            # Update MFA settings
            mfa_settings, created = MFASettings.objects.get_or_create(user=request.user)
            mfa_settings.mfa_enabled = True
            mfa_settings.mfa_method = 'sms'
            mfa_settings.phone_number = phone_number
            mfa_settings.save()

            # Log MFA setup
            AuditLog.objects.create(
                user=request.user,
                action_type='mfa_setup',
                description='SMS MFA enabled',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
            )

            return Response({
                'message': 'SMS MFA enabled successfully',
                'mfa_enabled': True,
                'mfa_method': 'sms',
                'phone_number': phone_number,
            })
        else:
            return Response(
                {'error': 'Invalid verification code'},
                status=status.HTTP_400_BAD_REQUEST
            )

    except Exception as e:
        logger.error(f'Failed to verify SMS code: {str(e)}')
        return Response(
            {'error': 'Failed to verify SMS code'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mfa_verify_login(request):
    """Verify MFA token during login"""
    token = request.data.get('token')
    method = request.data.get('method', 'totp')

    if not token:
        return Response(
            {'error': 'Token is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        mfa_settings = MFASettings.objects.get(user=request.user, mfa_enabled=True)

        if method == 'totp':
            from django_otp.plugins.otp_totp.models import TOTPDevice
            devices = TOTPDevice.objects.filter(user=request.user, confirmed=True)

            for device in devices:
                if device.verify_token(token):
                    # Log successful MFA verification
                    AuditLog.objects.create(
                        user=request.user,
                        action_type='mfa_verify',
                        description='TOTP verification successful',
                        ip_address=get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    )
                    return Response({'verified': True})

            return Response(
                {'error': 'Invalid TOTP token'},
                status=status.HTTP_400_BAD_REQUEST
            )

        elif method == 'sms':
            # For SMS, we'd typically send a new code and verify it
            # This is a simplified implementation
            stored_code = request.session.get('mfa_verification_code')
            if token == stored_code:
                # Clear the code
                del request.session['mfa_verification_code']

                # Log successful MFA verification
                AuditLog.objects.create(
                    user=request.user,
                    action_type='mfa_verify',
                    description='SMS verification successful',
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                )
                return Response({'verified': True})
            else:
                return Response(
                    {'error': 'Invalid SMS code'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        else:
            return Response(
                {'error': 'Invalid MFA method'},
                status=status.HTTP_400_BAD_REQUEST
            )

    except MFASettings.DoesNotExist:
        return Response(
            {'error': 'MFA not enabled'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f'Failed to verify MFA: {str(e)}')
        return Response(
            {'error': 'Failed to verify MFA'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mfa_disable(request):
    """Disable MFA for current user"""
    confirmation = request.data.get('confirmation')

    if confirmation != 'DISABLE_MFA':
        return Response(
            {'error': 'Invalid confirmation'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        mfa_settings = MFASettings.objects.get(user=request.user)
        mfa_settings.mfa_enabled = False
        mfa_settings.save()

        # Delete TOTP devices
        from django_otp.plugins.otp_totp.models import TOTPDevice
        TOTPDevice.objects.filter(user=request.user).delete()

        # Log MFA disable
        AuditLog.objects.create(
            user=request.user,
            action_type='mfa_setup',
            description='MFA disabled',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )

        return Response({
            'message': 'MFA disabled successfully',
            'mfa_enabled': False,
        })

    except MFASettings.DoesNotExist:
        return Response(
            {'error': 'MFA not configured'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f'Failed to disable MFA: {str(e)}')
        return Response(
            {'error': 'Failed to disable MFA'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mfa_backup_codes(request):
    """Generate new backup codes"""
    try:
        mfa_settings = MFASettings.objects.get(user=request.user, mfa_enabled=True)
        mfa_settings.generate_backup_codes()

        # Log backup code generation
        AuditLog.objects.create(
            user=request.user,
            action_type='mfa_setup',
            description='Backup codes generated',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )

        return Response({
            'message': 'Backup codes generated',
            'backup_codes': mfa_settings.backup_codes,
        })

    except MFASettings.DoesNotExist:
        return Response(
            {'error': 'MFA not enabled'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f'Failed to generate backup codes: {str(e)}')
        return Response(
            {'error': 'Failed to generate backup codes'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Helper function to get client IP
def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
