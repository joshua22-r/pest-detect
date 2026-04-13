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
router.register(r'sessions', views.UserSessionViewSet, basename='session')
router.register(r'roles', views.RoleViewSet, basename='role')
router.register(r'permissions', views.PermissionViewSet, basename='permission')
router.register(r'user-roles', views.UserRoleViewSet, basename='user-role')

urlpatterns = [
    # Health Checks & Monitoring
    path('health/', views.health_check, name='health_check'),
    path('ready/', views.readiness_check, name='readiness_check'),
    path('live/', views.liveness_check, name='liveness_check'),
    
    # Authentication
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login, name='login'),
    path('auth/social-login/', views.social_login, name='social_login'),
    path('auth/login/complete-mfa/', views.login_complete_mfa, name='login_complete_mfa'),
    path('auth/password-reset/request/', views.request_password_reset, name='request_password_reset'),
    path('auth/password-reset/confirm/', views.confirm_password_reset, name='confirm_password_reset'),
    path('auth/change-password/', views.change_password, name='change_password'),
    path('auth/logout/', views.logout, name='logout'),
    path('auth/user/', views.get_user, name='get_user'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # MFA (Multi-Factor Authentication)
    path('auth/mfa/status/', views.mfa_status, name='mfa_status'),
    path('auth/mfa/setup/totp/', views.mfa_setup_totp, name='mfa_setup_totp'),
    path('auth/mfa/verify/totp/', views.mfa_verify_totp, name='mfa_verify_totp'),
    path('auth/mfa/setup/sms/', views.mfa_setup_sms, name='mfa_setup_sms'),
    path('auth/mfa/verify/sms/', views.mfa_verify_sms, name='mfa_verify_sms'),
    path('auth/mfa/verify/', views.mfa_verify_login, name='mfa_verify_login'),
    path('auth/mfa/disable/', views.mfa_disable, name='mfa_disable'),
    path('auth/mfa/backup-codes/', views.mfa_backup_codes, name='mfa_backup_codes'),
    
    # Detection
    path('predict/', views.predict, name='predict'),
    
    # Trial & Subscription
    path('trial/status/', views.get_trial_status, name='trial_status'),
    path('trial/increment/', views.increment_trial_attempts, name='increment_trial'),
    path('predict/check/', views.check_can_predict, name='check_can_predict'),
    path('subscriptions/', views.subscriptions, name='subscriptions'),
    path('subscriptions/create/', views.create_subscription, name='create_subscription'),
    path('subscriptions/confirm-payment/', views.confirm_payment, name='confirm_payment'),
    
    # Stripe Payments
    path('payments/create-intent/', views.create_payment_intent, name='create_payment_intent'),
    path('payments/confirm-stripe/', views.confirm_stripe_payment, name='confirm_stripe_payment'),
    path('webhooks/stripe/', views.stripe_webhook, name='stripe_webhook'),
    
    # Data Management
    path('data/export/', views.export_user_data, name='export_user_data'),
    path('data/export-history/', views.export_detection_history, name='export_detection_history'),
    path('data/delete-account/', views.delete_user_account, name='delete_user_account'),
    
    # Analytics
    path('analytics/user/', views.user_analytics, name='user_analytics'),
    path('analytics/track/', views.track_user_action, name='track_user_action'),
    
    # Admin
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/users/<int:user_id>/', views.admin_user_detail, name='admin_user_detail'),
    path('admin/bulk-users/', views.admin_bulk_user_action, name='admin_bulk_users'),
    path('admin/system-settings/', views.admin_system_settings, name='admin_system_settings'),
    path('admin/bulk-delete-detections/', views.admin_bulk_delete_detections, name='admin_bulk_delete_detections'),
    path('admin/business-metrics/', views.admin_business_metrics, name='admin_business_metrics'),
    path('admin/performance-metrics/', views.admin_performance_metrics, name='admin_performance_metrics'),
    path('admin/stats/', views.admin_stats, name='admin_stats'),
    path('admin/payments/', views.admin_payments, name='admin_payments'),
    path('admin/subscriptions/', views.admin_subscriptions, name='admin_subscriptions'),
    path('admin/allow-access/', views.admin_allow_user_access, name='admin_allow_access'),
    path('admin/export-data/', views.admin_export_data, name='admin_export_data'),
    
    # Router URLs
    path('', include(router.urls)),
]
