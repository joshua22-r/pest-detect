from rest_framework import permissions
from django.utils import timezone


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner
        return obj.user == request.user


class IsAdminUser(permissions.BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)


class HasRolePermission(permissions.BasePermission):
    """
    Custom permission that checks if user has specific role-based permissions.
    """
    
    def __init__(self, required_permissions=None):
        """
        Initialize with required permissions.
        required_permissions should be a list of tuples: [(permission_type, resource_type), ...]
        """
        self.required_permissions = required_permissions or []
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Super admins have all permissions
        if hasattr(request.user, 'profile') and request.user.profile.is_super_admin:
            return True
        
        # Check role-based permissions
        user_permissions = self._get_user_permissions(request.user)
        
        for perm_type, resource_type in self.required_permissions:
            required_perm = f"{perm_type}_{resource_type}"
            if required_perm not in user_permissions:
                return False
        
        return True
    
    def _get_user_permissions(self, user):
        """Get all permissions for a user based on their roles"""
        permissions = set()
        
        # Get user roles (active and not expired)
        user_roles = user.user_roles.filter(
            is_active=True,
            expires_at__isnull=True
        ) | user.user_roles.filter(
            is_active=True,
            expires_at__gt=timezone.now()
        )
        
        # Get permissions from roles
        for user_role in user_roles:
            role_permissions = user_role.role.role_permissions.filter(
                permission__is_active=True
            ).select_related('permission')
            
            for rp in role_permissions:
                perm = rp.permission
                permissions.add(f"{perm.permission_type}_{perm.resource_type}")
        
        return permissions


class IsModerator(permissions.BasePermission):
    """
    Allows access to users with moderator roles.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return hasattr(request.user, 'profile') and request.user.profile.is_moderator


class IsContentModerator(permissions.BasePermission):
    """
    Allows access to content moderators.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        user_type = getattr(request.user.profile, 'user_type', None)
        return user_type in ['content_moderator', 'moderator', 'admin', 'super_admin']


class IsUserModerator(permissions.BasePermission):
    """
    Allows access to user moderators.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        user_type = getattr(request.user.profile, 'user_type', None)
        return user_type in ['user_moderator', 'moderator', 'admin', 'super_admin']


class CanModerateUsers(HasRolePermission):
    """
    Permission for moderating users.
    """
    
    def __init__(self):
        super().__init__([('moderate', 'user'), ('view', 'user')])


class CanModerateContent(HasRolePermission):
    """
    Permission for moderating content.
    """
    
    def __init__(self):
        super().__init__([('moderate', 'detection'), ('moderate', 'disease'), ('view', 'detection'), ('view', 'disease')])


class CanViewAuditLogs(HasRolePermission):
    """
    Permission for viewing audit logs.
    """
    
    def __init__(self):
        super().__init__([('view', 'audit_log')])


class CanManageSystem(HasRolePermission):
    """
    Permission for system administration.
    """
    
    def __init__(self):
        super().__init__([('admin', 'system')])
