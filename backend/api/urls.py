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
    
    # Trial & Subscription
    path('trial/status/', views.get_trial_status, name='trial_status'),
    path('trial/increment/', views.increment_trial_attempts, name='increment_trial'),
    path('predict/check/', views.check_can_predict, name='check_can_predict'),
    path('subscriptions/', views.subscriptions, name='subscriptions'),
    path('subscriptions/create/', views.create_subscription, name='create_subscription'),
    path('subscriptions/confirm-payment/', views.confirm_payment, name='confirm_payment'),
    
    # Admin
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/users/<int:user_id>/', views.admin_user_detail, name='admin_user_detail'),
    path('admin/stats/', views.admin_stats, name='admin_stats'),
    path('admin/payments/', views.admin_payments, name='admin_payments'),
    path('admin/subscriptions/', views.admin_subscriptions, name='admin_subscriptions'),
    path('admin/allow-access/', views.admin_allow_user_access, name='admin_allow_access'),
    
    # Router URLs
    path('', include(router.urls)),
]
