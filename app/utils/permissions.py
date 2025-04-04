
from rest_framework.permissions import IsAuthenticated

from app.utils.utils import get_field


class UserIsObjectOwner(IsAuthenticated):
    message = 'The user is not the owner of the object.'

    def has_permission(self, request, view):
        status = super().has_permission(request, view)

        obj = view.get_object()
        if status and hasattr(obj, 'OWNER_FIELD'):
            status = get_field(obj, getattr(obj, 'OWNER_FIELD')) == request.user.id

        return status
