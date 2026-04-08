from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from .models import (
    Plant, Animal, Disease, DetectionResult, 
    UserProfile, SystemStatistics
)
from .serializers import (
    UserSerializer, UserProfileSerializer, PlantSerializer,
    AnimalSerializer, DiseaseSerializer, DiseaseDetailSerializer,
    DetectionResultSerializer, DetectionResultCreateSerializer,
    SystemStatisticsSerializer
)
from .ml_detector import MockMLDetector
from .permissions import IsOwnerOrReadOnly, IsAdminUser


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
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_users(request):
    """Get all users (admin only)"""
    if not request.user.is_staff:
        return Response(
            {'error': 'Admin access required'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
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
