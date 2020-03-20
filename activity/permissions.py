from rest_framework import permissions


class IsReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        viewer_group = request.user.activity_user.activity_user_org_group.filter(group__name='Viewer')
        return not viewer_group.exists()
