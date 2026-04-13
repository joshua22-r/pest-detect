import csv
import json
from io import StringIO, BytesIO
from django.http import HttpResponse
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
from .models import DetectionResult, UserProfile, SystemStatistics
import logging

logger = logging.getLogger('api')


class DataManagementService:
    """Service for data export, import, and backup operations"""

    @staticmethod
    def export_user_data(user, format_type='json'):
        """
        Export user's personal data for GDPR compliance
        """
        try:
            # Get user's profile
            profile = user.profile

            # Get user's detection results
            detections = DetectionResult.objects.filter(user=user).values(
                'id', 'subject_type', 'disease_name', 'confidence', 'severity',
                'treatment', 'prevention', 'notes', 'created_at', 'updated_at'
            )

            # Get user's subscriptions
            subscriptions = user.subscriptions.all().values(
                'id', 'plan', 'status', 'payment_method', 'amount',
                'start_date', 'end_date', 'is_paid', 'created_at'
            )

            data = {
                'user_info': {
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'date_joined': user.date_joined,
                    'is_active': user.is_active,
                },
                'profile': {
                    'user_type': profile.user_type,
                    'phone': profile.phone,
                    'location': profile.location,
                    'bio': profile.bio,
                    'total_scans': profile.total_scans,
                    'created_at': profile.created_at,
                    'updated_at': profile.updated_at,
                },
                'detections': list(detections),
                'subscriptions': list(subscriptions),
                'export_date': timezone.now(),
            }

            if format_type == 'json':
                return json.dumps(data, indent=2, cls=DjangoJSONEncoder)
            elif format_type == 'csv':
                return DataManagementService._convert_to_csv(data)
            else:
                raise ValueError(f"Unsupported format: {format_type}")

        except Exception as e:
            logger.error(f'Failed to export user data: {str(e)}')
            raise

    @staticmethod
    def export_detection_results(format_type='csv', **filters):
        """
        Export detection results with optional filtering
        """
        try:
            queryset = DetectionResult.objects.select_related('user').order_by('-created_at')

            # Apply filters
            if 'user_id' in filters:
                queryset = queryset.filter(user_id=filters['user_id'])
            if 'subject_type' in filters:
                queryset = queryset.filter(subject_type=filters['subject_type'])
            if 'date_from' in filters:
                queryset = queryset.filter(created_at__gte=filters['date_from'])
            if 'date_to' in filters:
                queryset = queryset.filter(created_at__lte=filters['date_to'])
            if 'disease_name' in filters:
                queryset = queryset.filter(disease_name__icontains=filters['disease_name'])

            if format_type == 'csv':
                return DataManagementService._export_detections_csv(queryset)
            elif format_type == 'json':
                return DataManagementService._export_detections_json(queryset)
            else:
                raise ValueError(f"Unsupported format: {format_type}")

        except Exception as e:
            logger.error(f'Failed to export detection results: {str(e)}')
            raise

    @staticmethod
    def _export_detections_csv(queryset):
        """Export detection results as CSV"""
        output = StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            'ID', 'Username', 'Subject Type', 'Disease Name', 'Confidence',
            'Severity', 'Treatment', 'Prevention', 'Notes', 'Created At'
        ])

        # Write data
        for detection in queryset:
            writer.writerow([
                detection.id,
                detection.user.username,
                detection.subject_type,
                detection.disease_name,
                detection.confidence,
                detection.severity,
                detection.treatment,
                detection.prevention,
                detection.notes,
                detection.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            ])

        return output.getvalue()

    @staticmethod
    def _export_detections_json(queryset):
        """Export detection results as JSON"""
        data = []
        for detection in queryset:
            data.append({
                'id': str(detection.id),
                'user': detection.user.username,
                'subject_type': detection.subject_type,
                'disease_name': detection.disease_name,
                'confidence': detection.confidence,
                'severity': detection.severity,
                'treatment': detection.treatment,
                'prevention': detection.prevention,
                'notes': detection.notes,
                'created_at': detection.created_at,
                'updated_at': detection.updated_at,
            })

        return json.dumps(data, indent=2, cls=DjangoJSONEncoder)

    @staticmethod
    def _convert_to_csv(data):
        """Convert user data dict to CSV format"""
        output = StringIO()
        writer = csv.writer(output)

        # Write user info
        writer.writerow(['Section', 'Field', 'Value'])
        writer.writerow(['User Info', 'Username', data['user_info']['username']])
        writer.writerow(['User Info', 'Email', data['user_info']['email']])
        writer.writerow(['User Info', 'First Name', data['user_info']['first_name']])
        writer.writerow(['User Info', 'Last Name', data['user_info']['last_name']])

        # Write profile info
        writer.writerow(['Profile', 'User Type', data['profile']['user_type']])
        writer.writerow(['Profile', 'Phone', data['profile']['phone'] or ''])
        writer.writerow(['Profile', 'Location', data['profile']['location'] or ''])
        writer.writerow(['Profile', 'Bio', data['profile']['bio'] or ''])

        return output.getvalue()

    @staticmethod
    def create_backup():
        """
        Create a full system backup (metadata only, not files)
        """
        try:
            backup_data = {
                'backup_date': timezone.now(),
                'users_count': UserProfile.objects.count(),
                'detections_count': DetectionResult.objects.count(),
                'stats': SystemStatistics.objects.first().__dict__ if SystemStatistics.objects.exists() else None,
                'recent_detections': list(
                    DetectionResult.objects.order_by('-created_at')[:100].values(
                        'id', 'user__username', 'subject_type', 'disease_name',
                        'confidence', 'created_at'
                    )
                ),
            }

            return json.dumps(backup_data, indent=2, cls=DjangoJSONEncoder)

        except Exception as e:
            logger.error(f'Failed to create backup: {str(e)}')
            raise

    @staticmethod
    def delete_user_data(user):
        """
        Delete all user data for GDPR compliance
        """
        try:
            # Delete detection results
            DetectionResult.objects.filter(user=user).delete()

            # Delete subscriptions and payments
            for subscription in user.subscriptions.all():
                subscription.payments.all().delete()
            user.subscriptions.all().delete()

            # Delete profile
            user.profile.delete()

            # Delete user (this will cascade to related objects)
            user.delete()

            logger.warning(f'User data deleted for user ID: {user.id}')

            return True

        except Exception as e:
            logger.error(f'Failed to delete user data: {str(e)}')
            raise