from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

router = DefaultRouter()
router.register(r'plants', views.PlantViewSet)
router.register(r'animals', views.AnimalViewSet)
router.register(r'diseases', views.DiseaseViewSet, basename='disease')
router.register(r'detections', views.DetectionResultViewSet, basename='detection')
router.register(r'profiles', views.UserProfileViewSet, basename='profile')
router.register(r'statistics', views.SystemStatisticsViewSet, basename='statistics')

urlpatterns = [
    # Authentication
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login, name='login'),
    path('auth/logout/', views.logout, name='logout'),
    path('auth/user/', views.get_user, name='get_user'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Detection
    path('predict/', views.predict, name='predict'),
    
    # Admin
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/stats/', views.admin_stats, name='admin_stats'),
    
    # Router URLs
    path('', include(router.urls)),
]
