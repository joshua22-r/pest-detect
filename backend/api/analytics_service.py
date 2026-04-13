from django.utils import timezone
from django.db.models import Count, Sum, Avg
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
from .models import DetectionResult, User, Subscription, Payment, SystemStatistics
import logging

logger = logging.getLogger('api')


class AnalyticsService:
    """Service for tracking and analyzing user behavior and business metrics"""

    @staticmethod
    def track_user_action(user, action, metadata=None):
        """Track user actions for analytics"""
        try:
            # This would typically go to an analytics database or service
            # For now, we'll log it and could extend to store in a separate table
            logger.info(f'User Action: {user.username} - {action} - {metadata or {}}')
        except Exception as e:
            logger.error(f'Failed to track user action: {str(e)}')

    @staticmethod
    def get_user_analytics(user, period='30d'):
        """Get analytics for a specific user"""
        try:
            end_date = timezone.now()
            if period == '7d':
                start_date = end_date - timezone.timedelta(days=7)
            elif period == '30d':
                start_date = end_date - timezone.timedelta(days=30)
            elif period == '90d':
                start_date = end_date - timezone.timedelta(days=90)
            else:
                start_date = end_date - timezone.timedelta(days=30)

            detections = DetectionResult.objects.filter(
                user=user,
                created_at__gte=start_date
            )

            analytics = {
                'total_scans': detections.count(),
                'scans_by_type': detections.values('subject_type').annotate(
                    count=Count('id')
                ).order_by('-count'),
                'scans_by_disease': detections.values('disease_name').annotate(
                    count=Count('id')
                ).order_by('-count')[:10],
                'daily_activity': detections.annotate(
                    date=TruncDate('created_at')
                ).values('date').annotate(
                    count=Count('id')
                ).order_by('date'),
                'avg_confidence': detections.aggregate(avg=Avg('confidence'))['avg'],
                'period': period,
            }

            return analytics

        except Exception as e:
            logger.error(f'Failed to get user analytics: {str(e)}')
            return {}

    @staticmethod
    def get_business_metrics(period='30d'):
        """Get business metrics for dashboard"""
        try:
            end_date = timezone.now()
            if period == '7d':
                start_date = end_date - timezone.timedelta(days=7)
            elif period == '30d':
                start_date = end_date - timezone.timedelta(days=30)
            elif period == '90d':
                start_date = end_date - timezone.timedelta(days=90)
            else:
                start_date = end_date - timezone.timedelta(days=30)

            # User metrics
            new_users = User.objects.filter(date_joined__gte=start_date).count()
            active_users = User.objects.filter(
                last_login__gte=start_date
            ).count()

            # Detection metrics
            detections = DetectionResult.objects.filter(created_at__gte=start_date)
            total_scans = detections.count()
            avg_confidence = detections.aggregate(avg=Avg('confidence'))['avg'] or 0

            # Subscription metrics
            subscriptions = Subscription.objects.filter(created_at__gte=start_date)
            new_subscriptions = subscriptions.count()
            active_subscriptions = Subscription.objects.filter(
                status='active',
                is_paid=True,
                end_date__gt=timezone.now()
            ).count()

            # Revenue metrics
            payments = Payment.objects.filter(
                created_at__gte=start_date,
                status='completed'
            )
            total_revenue = payments.aggregate(sum=Sum('amount'))['sum'] or 0

            # Churn rate (simplified)
            expired_subscriptions = Subscription.objects.filter(
                end_date__gte=start_date,
                end_date__lte=end_date,
                status='expired'
            ).count()

            churn_rate = (expired_subscriptions / max(active_subscriptions, 1)) * 100

            metrics = {
                'period': period,
                'users': {
                    'new': new_users,
                    'active': active_users,
                    'total': User.objects.count(),
                },
                'scans': {
                    'total': total_scans,
                    'avg_confidence': round(avg_confidence, 2),
                    'by_type': detections.values('subject_type').annotate(
                        count=Count('id')
                    ),
                },
                'subscriptions': {
                    'new': new_subscriptions,
                    'active': active_subscriptions,
                    'churn_rate': round(churn_rate, 2),
                },
                'revenue': {
                    'total': total_revenue,
                    'currency': 'UGX',
                },
                'conversion_funnel': {
                    'registrations': new_users,
                    'trial_users': subscriptions.filter(plan='daily').count(),
                    'paid_users': active_subscriptions,
                    'conversion_rate': round((active_subscriptions / max(new_users, 1)) * 100, 2),
                }
            }

            return metrics

        except Exception as e:
            logger.error(f'Failed to get business metrics: {str(e)}')
            return {}

    @staticmethod
    def get_system_performance_metrics():
        """Get system performance metrics"""
        try:
            # Detection performance
            recent_detections = DetectionResult.objects.filter(
                created_at__gte=timezone.now() - timezone.timedelta(hours=24)
            )

            performance = {
                'detection_success_rate': 0,
                'avg_processing_time': 0,  # Would need to add processing time field
                'error_rate': 0,  # Would need error tracking
                'peak_usage_hours': [],  # Would need time-based analysis
            }

            if recent_detections.exists():
                # Calculate success rate (detections with confidence > 50%)
                successful = recent_detections.filter(confidence__gt=50).count()
                performance['detection_success_rate'] = round(
                    (successful / recent_detections.count()) * 100, 2
                )

            return performance

        except Exception as e:
            logger.error(f'Failed to get performance metrics: {str(e)}')
            return {}

    @staticmethod
    def track_conversion_funnel(user, step, metadata=None):
        """Track user journey through conversion funnel"""
        try:
            steps = {
                'registration': 'User registered',
                'first_scan': 'Completed first scan',
                'trial_started': 'Started trial',
                'subscription_created': 'Created subscription',
                'payment_completed': 'Completed payment',
                'subscription_activated': 'Subscription activated',
            }

            if step in steps:
                AnalyticsService.track_user_action(
                    user,
                    f'funnel_{step}',
                    {'description': steps[step], **(metadata or {})}
                )

        except Exception as e:
            logger.error(f'Failed to track conversion funnel: {str(e)}')