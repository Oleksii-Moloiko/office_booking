from rest_framework.permissions import BasePermission

class IsOwnerOrAdmin(BasePermission):
    """
    Користувач бачить і змінює лише свої бронюванн.
    Адмін бачить все.
    """

    def has_object_permission(self, request, view, obj):
        # Адмін має доступ до всього
        if request.user.is_staff:
            return True

        # Користувач може бачити і змінювати лише свої бронювання
        return obj.user == request.user