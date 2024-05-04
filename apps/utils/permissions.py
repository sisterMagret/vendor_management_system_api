from functools import wraps

from rest_framework import status
from rest_framework.response import Response

from apps.utils.enums import UserGroup


def vendor_access_only():
    """
    Grant permission to vendors alone
    """

    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not request.user.groups.filter(
                name=UserGroup.VENDOR
            ).exists():
                return Response(
                    {
                        "status": status.HTTP_403_FORBIDDEN,
                        "message": "You currently do not have access to this resource",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
            response = func(request, *args, **kwargs)
            return response

        return wrapper

    return decorator


def buyer_access_only():
    """
    Grant permission to buyers
    """

    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not request.user.groups.filter(
                name=UserGroup.BUYER
            ).exists():
                return Response(
                    {
                        "status": status.HTTP_403_FORBIDDEN,
                        "message": "You currently do not have access to this resource",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
            response = func(request, *args, **kwargs)
            return response

        return wrapper

    return decorator


def staff_user_access_only():
    """
    Grant permission to super and staff users only
    """

    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_superuser or request.user.is_staff:
                return Response(
                    {
                        "status": status.HTTP_403_FORBIDDEN,
                        "message": "You currently do not have access to this resource",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
            response = func(request, *args, **kwargs)
            return response

        return wrapper

    return decorator
