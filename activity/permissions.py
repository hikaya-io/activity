from rest_framework import permissions

from workflow.models import ActivityUserOrganizationGroup


class IsReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return not ActivityUserOrganizationGroup.objects.filter(
            activity_user__id=int(request.user.activity_user.id),
            organization_id=request.user.activity_user.organization.id,
            group__name='Viewer'
        ).exists()

