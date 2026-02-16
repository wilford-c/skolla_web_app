from functools import wraps

from django.core.exceptions import PermissionDenied


def role_required(*allowed_roles):
    """Restrict a view to the provided roles (superusers always pass)."""

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                raise PermissionDenied
            if user.is_superuser or user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied

        return _wrapped

    return decorator
