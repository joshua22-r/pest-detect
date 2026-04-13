from django.core.management.base import BaseCommand
from django.db import transaction
from api.models import Role, Permission, RolePermission


class Command(BaseCommand):
    help = 'Set up default roles and permissions for RBAC'

    def handle(self, *args, **options):
        self.stdout.write('Setting up RBAC roles and permissions...')

        with transaction.atomic():
            # Create permissions
            permissions_data = [
                # User permissions
                {'name': 'View Users', 'codename': 'view_user', 'permission_type': 'view', 'resource_type': 'user'},
                {'name': 'Create Users', 'codename': 'create_user', 'permission_type': 'create', 'resource_type': 'user'},
                {'name': 'Update Users', 'codename': 'update_user', 'permission_type': 'update', 'resource_type': 'user'},
                {'name': 'Delete Users', 'codename': 'delete_user', 'permission_type': 'delete', 'resource_type': 'user'},
                {'name': 'Moderate Users', 'codename': 'moderate_user', 'permission_type': 'moderate', 'resource_type': 'user'},

                # Detection permissions
                {'name': 'View Detections', 'codename': 'view_detection', 'permission_type': 'view', 'resource_type': 'detection'},
                {'name': 'Create Detections', 'codename': 'create_detection', 'permission_type': 'create', 'resource_type': 'detection'},
                {'name': 'Update Detections', 'codename': 'update_detection', 'permission_type': 'update', 'resource_type': 'detection'},
                {'name': 'Delete Detections', 'codename': 'delete_detection', 'permission_type': 'delete', 'resource_type': 'detection'},
                {'name': 'Moderate Detections', 'codename': 'moderate_detection', 'permission_type': 'moderate', 'resource_type': 'detection'},

                # Disease permissions
                {'name': 'View Diseases', 'codename': 'view_disease', 'permission_type': 'view', 'resource_type': 'disease'},
                {'name': 'Create Diseases', 'codename': 'create_disease', 'permission_type': 'create', 'resource_type': 'disease'},
                {'name': 'Update Diseases', 'codename': 'update_disease', 'permission_type': 'update', 'resource_type': 'disease'},
                {'name': 'Delete Diseases', 'codename': 'delete_disease', 'permission_type': 'delete', 'resource_type': 'disease'},
                {'name': 'Moderate Diseases', 'codename': 'moderate_disease', 'permission_type': 'moderate', 'resource_type': 'disease'},

                # Plant permissions
                {'name': 'View Plants', 'codename': 'view_plant', 'permission_type': 'view', 'resource_type': 'plant'},
                {'name': 'Create Plants', 'codename': 'create_plant', 'permission_type': 'create', 'resource_type': 'plant'},
                {'name': 'Update Plants', 'codename': 'update_plant', 'permission_type': 'update', 'resource_type': 'plant'},
                {'name': 'Delete Plants', 'codename': 'delete_plant', 'permission_type': 'delete', 'resource_type': 'plant'},

                # Animal permissions
                {'name': 'View Animals', 'codename': 'view_animal', 'permission_type': 'view', 'resource_type': 'animal'},
                {'name': 'Create Animals', 'codename': 'create_animal', 'permission_type': 'create', 'resource_type': 'animal'},
                {'name': 'Update Animals', 'codename': 'update_animal', 'permission_type': 'update', 'resource_type': 'animal'},
                {'name': 'Delete Animals', 'codename': 'delete_animal', 'permission_type': 'delete', 'resource_type': 'animal'},

                # Subscription permissions
                {'name': 'View Subscriptions', 'codename': 'view_subscription', 'permission_type': 'view', 'resource_type': 'subscription'},
                {'name': 'Create Subscriptions', 'codename': 'create_subscription', 'permission_type': 'create', 'resource_type': 'subscription'},
                {'name': 'Update Subscriptions', 'codename': 'update_subscription', 'permission_type': 'update', 'resource_type': 'subscription'},
                {'name': 'Delete Subscriptions', 'codename': 'delete_subscription', 'permission_type': 'delete', 'resource_type': 'subscription'},

                # Payment permissions
                {'name': 'View Payments', 'codename': 'view_payment', 'permission_type': 'view', 'resource_type': 'payment'},
                {'name': 'Create Payments', 'codename': 'create_payment', 'permission_type': 'create', 'resource_type': 'payment'},
                {'name': 'Update Payments', 'codename': 'update_payment', 'permission_type': 'update', 'resource_type': 'payment'},
                {'name': 'Delete Payments', 'codename': 'delete_payment', 'permission_type': 'delete', 'resource_type': 'payment'},

                # Audit log permissions
                {'name': 'View Audit Logs', 'codename': 'view_audit_log', 'permission_type': 'view', 'resource_type': 'audit_log'},

                # System permissions
                {'name': 'System Administration', 'codename': 'admin_system', 'permission_type': 'admin', 'resource_type': 'system'},
            ]

            permissions = {}
            for perm_data in permissions_data:
                perm, created = Permission.objects.get_or_create(
                    codename=perm_data['codename'],
                    defaults=perm_data
                )
                permissions[perm_data['codename']] = perm
                if created:
                    self.stdout.write(f'Created permission: {perm.name}')

            # Create roles
            roles_data = [
                {
                    'name': 'Content Moderator',
                    'description': 'Can moderate content like detections and diseases',
                    'permissions': [
                        'view_detection', 'update_detection', 'delete_detection', 'moderate_detection',
                        'view_disease', 'update_disease', 'moderate_disease',
                        'view_user', 'moderate_user',
                        'view_audit_log'
                    ]
                },
                {
                    'name': 'User Moderator',
                    'description': 'Can moderate user accounts and profiles',
                    'permissions': [
                        'view_user', 'update_user', 'moderate_user',
                        'view_detection', 'view_disease',
                        'view_audit_log'
                    ]
                },
                {
                    'name': 'Data Manager',
                    'description': 'Can manage plant and animal data',
                    'permissions': [
                        'view_plant', 'create_plant', 'update_plant', 'delete_plant',
                        'view_animal', 'create_animal', 'update_animal', 'delete_animal',
                        'view_disease', 'create_disease', 'update_disease'
                    ]
                },
                {
                    'name': 'Subscription Manager',
                    'description': 'Can manage subscriptions and payments',
                    'permissions': [
                        'view_subscription', 'create_subscription', 'update_subscription',
                        'view_payment', 'create_payment', 'update_payment',
                        'view_user'
                    ]
                },
                {
                    'name': 'System Administrator',
                    'description': 'Full system access and administration',
                    'permissions': [
                        'view_user', 'create_user', 'update_user', 'delete_user', 'moderate_user',
                        'view_detection', 'create_detection', 'update_detection', 'delete_detection', 'moderate_detection',
                        'view_disease', 'create_disease', 'update_disease', 'delete_disease', 'moderate_disease',
                        'view_plant', 'create_plant', 'update_plant', 'delete_plant',
                        'view_animal', 'create_animal', 'update_animal', 'delete_animal',
                        'view_subscription', 'create_subscription', 'update_subscription', 'delete_subscription',
                        'view_payment', 'create_payment', 'update_payment', 'delete_payment',
                        'view_audit_log',
                        'admin_system'
                    ]
                }
            ]

            for role_data in roles_data:
                role, created = Role.objects.get_or_create(
                    name=role_data['name'],
                    defaults={
                        'description': role_data['description']
                    }
                )
                
                if created:
                    self.stdout.write(f'Created role: {role.name}')
                
                # Assign permissions to role
                for perm_codename in role_data['permissions']:
                    if perm_codename in permissions:
                        RolePermission.objects.get_or_create(
                            role=role,
                            permission=permissions[perm_codename]
                        )

        self.stdout.write(self.style.SUCCESS('RBAC setup completed successfully!'))