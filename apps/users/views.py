import logging
from datetime import datetime
import pytz

from django.contrib.auth import authenticate, get_user_model, logout
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.utils.timezone import make_aware
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from apps.purchase_orders.models import PurchaseOrder
from apps.purchase_orders.serializer import PurchaseOrderSerializer
from apps.users.models import BuyerSettings, VendorProfile
from apps.users.serializer import (
    BuyerFormSerializer,
    BuyerRegistrationSerializer,
    BuyerSettingsSerializer,
    UserSerializer,
    VendorFormSerializer,
    VendorHistoricalPerformanceSerializer,
    VendorRegistrationSerializer,
    VendorSerializer,
)
from apps.utils.base import Addon, BaseViewSet
from apps.utils.enums import UserGroup
from apps.utils.permissions import buyer_access_only, vendor_access_only

logger = logging.getLogger("users")

User = get_user_model()


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class AuthViewSet(ViewSet, Addon):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    @staticmethod
    def get_user(username):
        try:
            user = User.objects.get(
                Q(email=username)
                | Q(username=username)
                | Q(primary_number=username)
            )
            return user
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_data(request) -> dict:
        return (
            request.data
            if isinstance(request.data, dict)
            else request.data.dict()
        )

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "username": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="username is customer phone number",
                ),
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="user password"
                ),
            },
        ),
        operation_description="",
        responses={},
        operation_summary="LOGIN ENDPOINT FOR ALL USERS",
    )
    @action(
        detail=False, methods=["post"], description="Login authentication"
    )
    def login(self, request, *args, **kwargs):
        context = {"status": status.HTTP_200_OK}
        try:
            data = self.get_data(request)
            for key, value in data.items():
                if key not in ["username", "password"]:
                    raise Exception(f"{key} missing from the request")
            user = authenticate(
                request,
                username=data.get("username"),
                password=data.get("password"),
            )
            if user:
                user.last_login = make_aware(
                    datetime.today(),
                    timezone=pytz.timezone("Africa/Lagos"),
                )
                user.save(update_fields=["last_login"])
                context.update(
                    {
                        "data": UserSerializer(user).data,
                        "token": get_tokens_for_user(user),
                    }
                )
            else:
                context["status"] = status.HTTP_400_BAD_REQUEST
                context["message"] = (
                    "Invalid credentials, Kindly supply valid credentials"
                )
            return Response(context, status=context["status"])
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

    @staticmethod
    def error_message_formatter(serializer_errors):
        """Formats serializer error messages to dictionary"""
        return {
            f"{name}": f"{message[0]}"
            for name, message in serializer_errors.items()
        }

    @swagger_auto_schema(
        request_body=VendorRegistrationSerializer,
        operation_description="This endpoint handles user onboarding",
        responses={},
        operation_summary="USER ONBOARD ENDPOINT",
        manual_parameters=[
            openapi.Parameter(
                name="account_type",
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                description="The type of account to be registered.",
                required=True,
                enum=UserGroup.to_list(),
            )
        ],
    )
    @action(
        detail=False,
        methods=["post"],
        description=f"on boarding authentication. account type include {UserGroup.to_list()}",
        url_path=r"register/(?P<account_type>[^/]+)",
    )
    def register(self, request, account_type):
        context = {"status": status.HTTP_200_OK}
        try:
            account_type_list = [UserGroup.VENDOR, UserGroup.BUYER]
            if account_type not in account_type_list:
                raise Exception("Kindly supply a valid account type")

            data = self.get_data(request)

            if account_type == UserGroup.VENDOR:
                return self.create_vendor_account(data)
            else:
                serializer_dict = {
                    UserGroup.BUYER: BuyerRegistrationSerializer,
                }
                return self.generic_create_user(
                    data, serializer_dict[account_type]
                )
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

    def create_vendor_account(self, data):
        context = {"status": status.HTTP_201_CREATED}
        try:
            serializer = VendorRegistrationSerializer(data=data)
            if serializer.is_valid():
                if User.objects.filter(mobile=data.get("mobile")).exists():
                    raise Exception(
                        "User with this mobile number already exist on our system"
                    )
                instance = serializer.create(
                    validated_data=serializer.validated_data
                )
                context["message"] = "Account created successfully"
            else:
                context.update(
                    {
                        "errors": self.error_message_formatter(
                            serializer.errors
                        ),
                        "status": status.HTTP_400_BAD_REQUEST,
                    }
                )
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

    def generic_create_user(self, data, serializer):
        context = {"status": status.HTTP_201_CREATED}
        try:
            serializer = serializer(data=data)
            if serializer.is_valid():
                _ = serializer.create(
                    validated_data=serializer.validated_data
                )
                context.update({"message": "Account created successfully"})
            else:
                context.update(
                    {
                        "errors": self.error_message_formatter(
                            serializer.errors
                        ),
                        "status": status.HTTP_400_BAD_REQUEST,
                    }
                )
        except Exception as ex:
            context.update(
                {"message": str(ex), "status": status.HTTP_400_BAD_REQUEST}
            )
        return Response(context, status=context["status"])


class UserViewSet(BaseViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.select_related("buyer").all()

    def get_queryset(self):
        return self.queryset
    
    def get_object(self):
        return get_object_or_404(User, pk=self.kwargs.get("pk"))

    def list(self, request, *args, **kwargs):
        context = {"status": status.HTTP_200_OK}
        try:
            logger.info(f"Fetching all users")
            paginate = self.get_paginated_data(
                queryset=self.get_list(self.get_queryset()),
                serializer_class=self.serializer_class,
            )
            context.update(
                {"status": status.HTTP_200_OK, "data": paginate}
            )
        except Exception as ex:
            logger.error(f"Error fetching all user due to {str(ex)}")
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

   
    @swagger_auto_schema(
        operation_description="",
        responses={},
        operation_summary="Deletes user account",
    )
    @action(
        detail=False,
        methods=["delete"],
        description="Deletes user account",
        url_path="delete",
    )
    def delete_account(self, request, *args, **kwargs):
        context = {"status": status.HTTP_204_NO_CONTENT}
        try:
            user = get_object_or_404(User, pk=request.user.id)
            user.delete()
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])


class VendorViewSet(BaseViewSet):
    queryset = VendorProfile.objects.select_related("user").all()
    serializer_class = VendorSerializer
    serializer_form_class = VendorFormSerializer

    def get_object(self):
        return get_object_or_404(VendorProfile, pk=self.kwargs.get("pk"))

    def get_queryset(self):
        return self.queryset

    @swagger_auto_schema(
        operation_description="",
        responses={},
        operation_summary="List all vendors account",
    )
    def list(self, request, *args, **kwargs):
        context = {"status": status.HTTP_200_OK}
        try:
            paginate = self.get_paginated_data(
                queryset=self.get_list(self.get_queryset()),
                serializer_class=self.serializer_class,
            )
            context.update(
                {"status": status.HTTP_200_OK, "data": paginate}
            )
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])
    
    @action(
        detail=False,
        methods=["get"],
        description="Get vendor customers",
        url_path="buyers",
    )
    @swagger_auto_schema(
        operation_description="",
        responses={},
        operation_summary="List all vendor customers",
    )
    def buyers_list(self, request, *args, **kwargs):
        context = {"status": status.HTTP_200_OK}
        try:
            queryset = {po.buyer for po in PurchaseOrder.objects.filter(vendor__user=request.user)}
            paginate = self.get_paginated_data(
                queryset=self.get_list(queryset),
                serializer_class=UserSerializer,
            )
            context.update(
                {"status": status.HTTP_200_OK, "data": paginate}
            )
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

    @action(
        detail=False,
        methods=["get"],
        description="Get vendor profile settings ",
        url_path="profile"
    )
    @method_decorator(vendor_access_only(), name="dispatch")
    def me(self, request, *args, **kwargs):
        context = {"status": status.HTTP_200_OK}
        try:
            vendor = self.queryset.filter(user__id=request.user.id)

            if vendor.exists():
                
                performance_metrics = vendor.first().calculate_performance_metrics
                
                performance_metrics.update(vendor=VendorSerializer(vendor.first()).data)
                context.update(
                    {
                        "data": performance_metrics
                    }
                )   
            else:
                raise Exception("profile does not exist")
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        request_body=VendorFormSerializer,
        operation_description="",
        responses={},
        operation_summary="Update vendor profile",
    )
    @action(
        detail=False,
        methods=["put"],
        description="Update vendor profile settings ",
        url_path="profile/update",
    )
    @method_decorator(vendor_access_only(), name="dispatch")
    def update_account(self, request, *args, **kwargs):
        context = {"status": status.HTTP_200_OK}
        try:
            data = self.get_data(request)
            self.validate_business_name(request, data)
            instance = self.queryset.filter(user__id=request.user.id).first()
        
            serializer = self.serializer_form_class(
                instance=instance, data=data
            )
            if serializer.is_valid():
                obj = serializer.update(
                    instance=instance,
                    validated_data=serializer.validated_data,
                )
                context.update({"data": self.serializer_class(obj).data})
            else:
                context.update(
                    {
                        "status": status.HTTP_400_BAD_REQUEST,
                        "errors": self.error_message_formatter(
                            serializer.errors
                        ),
                    }
                )
        except Exception as ex:
            context.update(
                {
                    "message": str(ex),
                    "status": status.HTTP_400_BAD_REQUEST,
                }
            )
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        operation_description="Retrieve minimal vendor profile details",
        operation_summary="Retrieve minimal vendor profile details",
    )
    def retrieve(self, requests, *args, **kwargs):
        context = {"status": status.HTTP_200_OK}
        try:
            context.update({"data": self.serializer_class(self.get_object()).data})
        except Exception as ex:
            context.update({"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)})
        return Response(context, status=context["status"])

    @action(
        detail=False,
        methods=["get"],
        description="Get vendor purchase orders",
        url_path="purchase-order",
    )
    @swagger_auto_schema(
        operation_description="",
        responses={},
        operation_summary="List all vendor purchase orders",
    )
    @method_decorator(vendor_access_only(), name="dispatch")
    def vendor_po_list(self, request, *args, **kwargs):
        context = {"status": status.HTTP_200_OK}
        try:
            queryset = PurchaseOrder.objects.filter(vendor__user=request.user)
            paginate = self.get_paginated_data(
                queryset=self.get_list(queryset),
                serializer_class=PurchaseOrderSerializer,
            )
            context.update(
                {"status": status.HTTP_200_OK, "data": paginate}
            )
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

    @action(
        detail=True,
        methods=["get"],
        description="Get vendor performance.",
        url_path="performance"
    )
    @swagger_auto_schema(
        operation_description="",
        responses={},
        operation_summary="Get vendor performance",
    )
    def performance(self, request, *args, **kwargs):
        context = {"status": status.HTTP_200_OK}
        try:
            vendor = self.get_object()
            performance_metrics = vendor.calculate_performance_metrics
            performance_metrics.update(vendor=VendorSerializer(vendor).data)
            context.update(
                {
                    "data": performance_metrics
                }
            )   
           
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])


    @action(
        detail=True,
        methods=["get"],
        description="Get vendor performance history.",
        url_path="performance/history"
    )
    @swagger_auto_schema(
        operation_description="",
        responses={},
        operation_summary="Get vendor performance history",
    )
    def performance(self, request, *args, **kwargs):
        context = {"status": status.HTTP_200_OK}
        try:
            vendor = self.get_object()
            performance_history = vendor.vendor_profile.select_related('vendor').all()


            context.update(
                {
                    "data": VendorHistoricalPerformanceSerializer(performance_history, many=True).data
                }
            )   
           
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])


class BuyerSettingsViewSet(BaseViewSet):
    queryset = BuyerSettings.objects.select_related("user").all()
    serializer_class = BuyerSettingsSerializer
    serializer_form_class = BuyerFormSerializer

    def get_object(self):
        return get_object_or_404(BuyerSettings, pk=self.kwargs.get("pk"))

    def get_queryset(self):
        return self.queryset
    
    @swagger_auto_schema(
        operation_description="",
        responses={},
        operation_summary="List all buyers account",
    )
    def list(self, request, *args, **kwargs):
        context = {"status": status.HTTP_200_OK}
        try:
            paginate = self.get_paginated_data(
                queryset=self.get_list(self.get_queryset()),
                serializer_class=self.serializer_class,
            )
            context.update(
                {"status": status.HTTP_200_OK, "data": paginate}
            )
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])
    
    @action(
        detail=False,
        methods=["get"],
        description="Get buyer vendors",
        url_path="vendors",
    )
    @swagger_auto_schema(
        operation_description="",
        responses={},
        operation_summary="List all buyer vendors",
    )
    def vendors_list(self, request, *args, **kwargs):
        context = {"status": status.HTTP_200_OK}
        try:
            queryset = {po.vendor for po in PurchaseOrder.objects.filter(buyer=request.user) if po.vendor}
            paginate = self.get_paginated_data(
                queryset=self.get_list(queryset),
                serializer_class=VendorSerializer,
            )
            context.update(
                {"status": status.HTTP_200_OK, "data": paginate}
            )
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

    @action(
        detail=False,
        methods=["get"],
        description="Get buyer profile settings",
        url_path="profile",
    )
    @method_decorator(buyer_access_only(), name="dispatch")
    def account(self, request, *args, **kwargs):
        context = {"status": status.HTTP_200_OK}
        try:
            instance, _ = self.queryset.get_or_create(user=request.user)
            context.update({"data": self.serializer_class(instance).data})
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        request_body=BuyerFormSerializer,
        operation_description="",
        responses={},
        operation_summary="Update buyer settings",
    )
    @action(
        detail=False,
        methods=["put"],
        description="Update vendor profile settings ",
        url_path="profile/update",
    )
    @method_decorator(buyer_access_only(), name="dispatch")
    def update_account(self, request, *args, **kwargs):
        context = {"status": status.HTTP_200_OK}
        try:
            data = self.get_data(request)
            self.validate_business_name(request, data)
            
            instance = self.queryset.filter(user__id=request.user.id).first()

            serializer = self.serializer_form_class(
                instance=instance, data=data
            )
            if serializer.is_valid():
                obj = serializer.update(
                    instance=instance,
                    validated_data=serializer.validated_data,
                )
                context.update({"data": self.serializer_class(obj).data})
            else:
                context.update(
                    {
                        "status": status.HTTP_400_BAD_REQUEST,
                        "errors": self.error_message_formatter(
                            serializer.errors
                        ),
                    }
                )
        except Exception as ex:
            context.update(
                {
                    "message": str(ex),
                    "status": status.HTTP_400_BAD_REQUEST,
                }
            )
        return Response(context, status=context["status"])

    @action(
        detail=False,
        methods=["get"],
        description="Get buyer purchase orders",
        url_path="purchase-order",
    )
    @swagger_auto_schema(
        operation_description="",
        responses={},
        operation_summary="List all buyer purchase orders",
    )
    def buyer_po_list(self, request, *args, **kwargs):
        context = {"status": status.HTTP_200_OK}
        try:
            queryset = PurchaseOrder.objects.filter(buyer=request.user)
            paginate = self.get_paginated_data(
                queryset=self.get_list(queryset),
                serializer_class=PurchaseOrderSerializer,
            )
            context.update(
                {"status": status.HTTP_200_OK, "data": paginate}
            )
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])


def account_logout(request):
    try:
        logout(request)
    except Exception as ex:
        pass
    return redirect("/")
