from functools import wraps

from rest_framework import status
from rest_framework.response import Response

from apps.users.models import BuyerSetting, User
from apps.utils.enums import BuyerTypeEnum, UserGroup


def farmer_access_only():
    """
    Grant permission to farmer alone
    """

    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not request.user.groups.filter(name=UserGroup.FARMER).exists():
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


def business_user_access_only():
    """
    Grant permission to business users
    """

    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not BuyerSetting.objects.filter(
                user=request.user, type=BuyerTypeEnum.BUSINESS
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
