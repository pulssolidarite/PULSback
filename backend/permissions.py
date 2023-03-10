from rest_framework import permissions


class IsAdminOrCustomerUser(permissions.BasePermission):
    """
    Global permission to allow only if auth user is a staff or assigned to a customer
    """

    def has_permission(self, request, view):
        return bool(request.user.is_staff or request.user.is_customer_user())


class NonAdminUserCanOnlyGet(permissions.BasePermission):
    """
    Global permission check for staff users.
    """

    def has_permission(self, request, view):
        if not request.user.is_staff:
            if request.method == "GET":
                return True
            else:
                return False
        else:
            return True


class NormalUserIsCurrentUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user and not request.user.is_staff and not request.user.is_superuser:
            if request.method == "GET":
                return obj.pk == request.user.id
            else:
                return False
        else:
            return True


class IsSuperStaff(permissions.BasePermission):
    """
    Global permission check for staff users.
    """

    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            return request.user.is_superuser
        else:
            return False


class TerminalIsAuthenticated(permissions.IsAuthenticated):
    """
    Global permission check for terminal user
    """

    def has_permission(self, request, view):
        return (
            super(permissions.IsAuthenticated).has_permission(request, view)
            and request.user.is_terminal_user()
        )
