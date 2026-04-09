from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import (
    Plant, Animal, Disease, DetectionResult, 
    UserProfile, SystemStatistics, Trial, Subscription, Payment
)
from .serializers import (
    UserSerializer, AdminUserSerializer, UserProfileSerializer, PlantSerializer,
    AnimalSerializer, DiseaseSerializer, DiseaseDetailSerializer,
    DetectionResultSerializer, DetectionResultCreateSerializer,
    SystemStatisticsSerializer, TrialSerializer, SubscriptionSerializer, PaymentSerializer
)
from .ml_detector import MockMLDetector
from .permissions import IsOwnerOrReadOnly, IsAdminUser


# Health Check View
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint for Render"""
    return Response({
        'status': 'healthy',
        'message': 'Pest Detect Backend is running',
    })


# Authentication Views
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """User registration endpoint"""
    try:
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        
        if not username or not email or not password:
            return Response(
                {'error': 'Username, email, and password are required'},
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
            return Response(
                {'error': 'Invalid username or password'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
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
        
        # Run ML detection
        detection_result = MockMLDetector.detect(image_file, subject_type)
        
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
def admin_user_detail(request, user_id):
    """Update or remove a user (admin only)"""
    if not request.user.is_staff:
        return Response(
            {'error': 'Admin access required'},
            status=status.HTTP_403_FORBIDDEN
        )

    user = User.objects.filter(pk=user_id).first()
    if not user:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        if user == request.user:
            return Response(
                {'error': 'You cannot delete your own account'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.delete()
        return Response({'success': True})

    if user == request.user and 'is_staff' in request.data:
        return Response(
            {'error': 'You cannot change your own admin privileges'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if 'is_active' in request.data:
        user.is_active = bool(request.data.get('is_active'))

    if 'is_staff' in request.data:
        user.is_staff = bool(request.data.get('is_staff'))

    if 'is_superuser' in request.data:
        user.is_superuser = bool(request.data.get('is_superuser'))

    if 'first_name' in request.data:
        user.first_name = request.data.get('first_name', user.first_name)

    if 'last_name' in request.data:
        user.last_name = request.data.get('last_name', user.last_name)

    if 'email' in request.data:
        user.email = request.data.get('email', user.email)

    user.save()

    profile = getattr(user, 'profile', None)
    if profile and 'user_type' in request.data:
        profile.user_type = request.data.get('user_type', profile.user_type)
        profile.save()

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
def create_subscription(request):
    """Create a new subscription"""
    plan = request.data.get('plan')
    payment_method = request.data.get('payment_method')
    mobile_number = request.data.get('mobile_number')
    
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
    
    # Calculate amount and end date based on plan
    if plan == 'daily':
        amount = 3000
        end_date = timezone.now() + timedelta(days=1)
    elif plan == 'weekly':
        amount = 10000
        end_date = timezone.now() + timedelta(weeks=1)
    else:  # monthly
        amount = 20000
        end_date = timezone.now() + timedelta(days=30)
    
    subscription = Subscription.objects.create(
        user=request.user,
        plan=plan,
        payment_method=payment_method,
        mobile_number=mobile_number,
        amount=amount,
        end_date=end_date,
        is_paid=False
    )
    
    # Create payment record
    payment = Payment.objects.create(
        subscription=subscription,
        user=request.user,
        amount=amount,
        payment_method=payment_method,
        mobile_number=mobile_number,
        status='pending'
    )
    
    serializer = SubscriptionSerializer(subscription)
    return Response({
        'subscription': serializer.data,
        'payment_id': str(payment.id),
        'message': f'Subscription created. Please complete payment of {amount} UGX via {payment_method.upper()} to {mobile_number}'
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
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


# Admin Endpoints
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_payments(request):
    """Admin: Get all payments"""
    if not request.user.is_staff:
        return Response(
            {'error': 'Admin access required'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    filter_status = request.query_params.get('status')
    
    payments = Payment.objects.all().order_by('-created_at')
    if filter_status:
        payments = payments.filter(status=filter_status)
    
    serializer = PaymentSerializer(payments, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_subscriptions(request):
    """Admin: Get all subscriptions"""
    if not request.user.is_staff:
        return Response(
            {'error': 'Admin access required'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    filter_status = request.query_params.get('status')
    filter_paid = request.query_params.get('paid')
    
    subscriptions = Subscription.objects.all().order_by('-created_at')
    if filter_status:
        subscriptions = subscriptions.filter(status=filter_status)
    if filter_paid == 'true':
        subscriptions = subscriptions.filter(is_paid=True)
    elif filter_paid == 'false':
        subscriptions = subscriptions.filter(is_paid=False)
    
    serializer = SubscriptionSerializer(subscriptions, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
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
        user = User.objects.get(id=user_id)
        profile = user.profile
        profile.admin_allowed_access = allow
        profile.save()
        
        return Response({
            'message': f'User {user.username} access {"allowed" if allow else "revoked"}',
            'user_id': user_id,
            'admin_allowed_access': allow
        })
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )
