import logging
import uuid
from abc import ABC, abstractmethod

from django.utils.crypto import get_random_string
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.users.models import BuyerSettings, User
from apps.users.serializer import VendorProfile
from apps.utils.pagination import CustomPaginator

logger = logging.getLogger("base")


class Addon:
    def __init__(self):
        super().__init__()

    @staticmethod
    def verify(payload):
        if User.objects.filter(**payload).exists():
            return True
        return False

    def generate_uuid(self, model, column):
        unique = str(uuid.uuid4())
        kwargs = {column: unique}
        qs_exists = model.objects.filter(**kwargs).exists()
        if qs_exists:
            return self.generate_uuid(model, column)
        return unique

    def unique_number_generator(
        self, model, field, length=6, allowed_chars="0123456789"
    ):
        unique = get_random_string(
            length=length, allowed_chars=allowed_chars
        )
        kwargs = {field: unique}
        qs_exists = model.objects.filter(**kwargs).exists()
        if qs_exists:
            return self.unique_number_generator(model, field, length)
        return unique

    def unique_alpha_numeric_generator(
        self,
        model,
        field,
        length=6,
        allowed_chars="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        prefix=None,
    ):
        unique = get_random_string(
            length=length, allowed_chars=allowed_chars
        )
        if prefix:
            unique = f"{prefix}_{unique}"
        kwargs = {field: unique}
        qs_exists = model.objects.filter(**kwargs).exists()
        if qs_exists:
            return self.unique_alpha_numeric_generator(model, field)
        return unique

class CustomFilter(DjangoFilterBackend):
    def get_filterset_kwargs(self, request, queryset, view):
        kwargs = super().get_filterset_kwargs(request, queryset, view)

        # merge filterset kwargs provided by view class
        if hasattr(view, "get_filterset_kwargs"):
            kwargs.update(view.get_filterset_kwargs())

        return kwargs


class AbstractBaseViewSet:
    custom_filter_class = CustomFilter()
    search_backends = SearchFilter()
    order_backend = OrderingFilter()
    filter_backends = [SearchFilter, DjangoFilterBackend]
    paginator_class = CustomPaginator()

    def __init__(self):
        pass

    @staticmethod
    def get_buyer(request):
        if request.GET.get("buyer_id") is not None:
            return BuyerSettings.objects.filter(
            id=request.GET.get("buy_id")
            ).first()
        
        if request.user.id: 
            return BuyerSettings.objects.filter(
                user__id=request.user.id
            ).first()
        
        return None

    @staticmethod
    def get_vendor(request):
        if request.GET.get("vendor_id") is not None:
            return VendorProfile.objects.filter(
                id=request.GET.get("vendor_id")
            ).first()
        
        elif request.user.id: 
            return VendorProfile.objects.filter(
                user__id=request.user.id
            ).first()
        
        return None
        

    @staticmethod
    def error_message_formatter(serializer_errors):
        """Formats serializer error messages to dictionary"""
        return {
            f"{name}": f"{message[0]}"
            for name, message in serializer_errors.items()
        }

    @staticmethod
    def order_date_filtering(date_from, date_to, queryset):
        if date_from and date_to:
            try:
                queryset = queryset.filter(order_date__range=[float(date_from), float(date_to)])
            except Exception as ex:
                logger.error(f"error filtering date due to {str(ex)}")
        return queryset

    @staticmethod
    def user_obj_permission(request, obj):
        if not request.user or request.user != obj.buyer:
            return Response(
                {
                    "status": status.HTTP_403_FORBIDDEN,
                    "message": "You currently do not have access to this resource",
                },
                status=status.HTTP_403_FORBIDDEN,
            )
    
    @staticmethod
    def validate_business_name(request, data):
        settings = data.get("settings")
        business_name = settings.get("business_name") if settings else None
        if business_name is not None:
            vendor = VendorProfile.objects.filter(business_name=business_name)
            buyer = BuyerSettings.objects.filter(business_name=business_name)
        
            if (vendor.exists() and vendor.first().user != request.user) or (buyer.exists() and buyer.first().user != request.user):
                raise Exception("Business name already exists")
      
        
class BaseViewSet(ViewSet, AbstractBaseViewSet, Addon):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @staticmethod
    def get_data(request) -> dict:
        """Returns a dictionary from the request"""
        return (
            request.data
            if isinstance(request.data, dict)
            else request.data.dict()
        )

    def get_list(self, queryset):
        if isinstance(queryset, set):
            return list(queryset)
        
        if "search" in self.request.query_params:
            query_set = self.search_backends.filter_queryset(
                request=self.request, queryset=queryset, view=self
            )
        elif self.request.query_params:
            query_set = self.custom_filter_class.filter_queryset(
                request=self.request, queryset=queryset, view=self
            )
        else:
            query_set = queryset
        if "ordering" in self.request.query_params:
            query_set = self.order_backend.filter_queryset(
                request=self.request, queryset=queryset, view=self
            )
        else:
            query_set = query_set.order_by("-pk")  # was originally 'pk'
        return query_set

    def get_paginated_data(self, queryset, serializer_class):
        paginated_data = self.paginator_class.generate_response(
            queryset, serializer_class, self.request
        )
        return paginated_data


class BaseModelViewSet(ModelViewSet, AbstractBaseViewSet, Addon):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @staticmethod
    def get_data(request) -> dict:
        return (
            request.data
            if isinstance(request.data, dict)
            else request.data.dict()
        )

    def get_list(self, queryset):
        if "search" in self.request.query_params:
            query_set = self.search_backends.filter_queryset(
                request=self.request, queryset=queryset, view=self
            )
        elif self.request.query_params:
            query_set = self.custom_filter_class.filter_queryset(
                request=self.request, queryset=queryset, view=self
            )
        else:
            query_set = queryset
        if "ordering" in self.request.query_params:
            query_set = self.order_backend.filter_queryset(
                request=self.request, queryset=queryset, view=self
            )
        else:
            query_set = query_set.order_by("-pk")  # was originally 'pk'
        return query_set

    def get_paginated_data(self, queryset, serializer_class):
        paginated_data = self.paginator_class.generate_response(
            queryset, serializer_class, self.request
        )
        return paginated_data


class BaseNoAuthViewSet(ViewSet, Addon):
    """
    This class inherit from django ViewSet class
    """

    custom_filter_class = CustomFilter()
    search_backends = SearchFilter()
    order_backend = OrderingFilter()
    paginator_class = CustomPaginator()
    serializer_class = None

    @staticmethod
    def error_message_formatter(serializer_errors):
        """Formats serializer error messages to dictionary"""
        return {
            f"{name}": f"{message[0]}"
            for name, message in serializer_errors.items()
        }

    @staticmethod
    def get_data(request) -> dict:
        return (
            request.data
            if isinstance(request.data, dict)
            else request.data.dict()
        )

    @abstractmethod
    def get_queryset(self):
        pass

    @abstractmethod
    def get_object(self):
        pass

    def get_list(self, queryset):
        if "search" in self.request.query_params:
            query_set = self.search_backends.filter_queryset(
                request=self.request, queryset=queryset, view=self
            )
        elif self.request.query_params:
            query_set = self.custom_filter_class.filter_queryset(
                request=self.request, queryset=queryset, view=self
            )
        else:
            query_set = queryset
        if "ordering" in self.request.query_params:
            query_set = self.order_backend.filter_queryset(
                query_set, self.request, self
            )
        else:
            query_set = query_set.order_by("-pk")
        return query_set

    def paginator(self, queryset, serializer_class):
        paginated_data = self.paginator_class.generate_response(
            queryset, serializer_class, self.request
        )
        return paginated_data

    @swagger_auto_schema(
        operation_description="List all entries available",
        operation_summary="List all entries available ",
    )
    def list(self, request, *args, **kwargs):
        context = {"status": status.HTTP_200_OK}
        try:
            paginate = self.paginator(
                queryset=self.get_list(self.get_queryset()),
                serializer_class=self.serializer_class,
            )
            context.update(
                {
                    "status": status.HTTP_200_OK,
                    "message": "OK",
                    "data": paginate,
                }
            )
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        operation_description="Retrieve entry details",
        operation_summary="Retrieve entry details",
    )
    def retrieve(self, requests, *args, **kwargs):
        context = {"status": status.HTTP_200_OK}
        try:
            context.update(
                {"data": self.serializer_class(self.get_object()).data}
            )
        except Exception as ex:
            context.update(
                {"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)}
            )
        return Response(context, status=context["status"])

    @staticmethod
    def price_filtering(price_from, price_to, queryset):
        if price_from and price_to:
            if (price_from and price_to) or price_from > price_to:
                price_to, price_from = price_from, price_to
                queryset = queryset.filter(
                    sales_price__range=[price_from, price_to]
                )
            elif price_from and price_to is None:
                queryset = queryset.filter(sales_price__gte=price_from)
            elif price_to and price_from is None:
                queryset = queryset.filter(sales_price__lte=price_to)
        return queryset
