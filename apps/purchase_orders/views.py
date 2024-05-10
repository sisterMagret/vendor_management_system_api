import logging

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
# Create your views here.
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.users.models import VendorProfile
from apps.utils.enums import POStatusEnum

from .models import PurchaseOrder
from .serializer import PurchaseOrderAcknowledgementSerializer, PurchaseOrderSerializer, PurchaseOrderFormSerializer
from apps.utils.base import BaseViewSet
from apps.utils.permissions import vendor_access_only


logger = logging.getLogger("purchase_order")

 
class PurchaseOrderViewSet(BaseViewSet):
    serializer_class = PurchaseOrderSerializer
    queryset = PurchaseOrder.objects.all()
    serializer_form_class = PurchaseOrderFormSerializer
    filter_fields = [
        "vendor__id",
        "buyer__id",
        "po_number",
        "order_date",
        "quality_rating",
        "delivery_date",
        "acknowledgment_date",
    ]
    search_fields = [
        "vendor__id",
        "buyer__id",
        "po_number",
        "order_date",
        "quality_rating",
        "delivery_date",
        "acknowledgment_date",
    ]

    def get_queryset(self):
        self.queryset = self.order_date_filtering(
            self.request.GET.get("order_date_from"), self.request.GET.get("order_date_to"), self.queryset
        )
        if VendorProfile.objects.filter(user__id=self.request.user.id).exists():
            return self.queryset.filter(vendor=self.get_vendor(self.request)).distinct().order_by("-order_date")
        return self.queryset.filter(Q(vendor=self.get_vendor(self.request)) | Q(buyer=self.request.user)).distinct().order_by("-order_date")

    def get_object(self):
        return get_object_or_404(PurchaseOrder, id=self.kwargs.get("pk"))

    @swagger_auto_schema(
        operation_summary="List all purchase orders",
        manual_parameters=[
            openapi.Parameter(
                "vendor_id",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=False,
                description="Vendor ID",
            ),
            openapi.Parameter(
                "buyer_id",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=False,
                description="Buyer ID",
            ),
            openapi.Parameter(
                "po_number",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=False,
                description="Purchase Order Number",
            ),
            openapi.Parameter(
                "quality_rating",
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=False,
                description="Quality Rating",
            ), 
             openapi.Parameter(
                "order_date",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=False,
                description="Order Date",
            ),
            openapi.Parameter(
                "delivery_date_from",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=False,
                description="Purchase Order Delivery Date From",
            ),
            openapi.Parameter(
                "delivery_date_to",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=False,
                description="Purchase Order Delivery Date To",

            ),
            openapi.Parameter(
                "acknowledgment_date_from",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=False,
                description="Purchase Order Acknowledgment Date From",
            ),
            openapi.Parameter(
                "acknowledgment_date_to",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=False,
                description="Purchase Order Acknowledgment Date To",

            )
        ],
    )
    def list(self, request, *args, **kwargs):
        context = {"status": status.HTTP_200_OK}
        try:
            logger.info(f"Fetching all purchase order for user_id")
            paginate = self.get_paginated_data(
                queryset=self.get_list(self.get_queryset()), serializer_class=self.serializer_class
            )
            context.update({"status": status.HTTP_200_OK, "data": paginate})
        except Exception as ex:
            logger.error(
                f"Error fetching all purchase order for user_id {request.user.id} due to {str(ex)}"
            )
            context.update({"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)})
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        operation_description="Retrieve purchase order details",
        operation_summary="Retrieve purchase order details",
    )
    def retrieve(self, requests, *args, **kwargs):
        context = {"status": status.HTTP_200_OK}
        try:
            context.update({"data": self.serializer_class(self.get_object()).data})
        except Exception as ex:
            context.update({"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)})
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        operation_description="Delete purchase order",
        operation_summary="Delete purchase order",
    )

    def destroy(self, request, *args, **kwargs):
        context = {"status": status.HTTP_204_NO_CONTENT}
        try:
            instance = self.get_object()
            self.user_obj_permission(request, instance)         
            instance.delete()
            context.update({"message": "Purchase order deleted successfully"})

        except Exception as ex:
            context.update({"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)})
        return Response(context, status=context["status"])

    @swagger_auto_schema(operation_summary="Create purchase order", request_body=PurchaseOrderFormSerializer)
    def create(self, request, *args, **kwargs):
        """
        This method handles creating of new purchase order
        """
        context = {"status": status.HTTP_201_CREATED}
        try:
            data = self.get_data(request)
            serializer = self.serializer_form_class(data=data)

            if serializer.is_valid():
                serializer.validated_data.update(
                    po_number=self.unique_number_generator(PurchaseOrder, "po_number", 12),
                    buyer=request.user,
                    )
                instance = serializer.create(serializer.validated_data)
               
                context.update({"data": self.serializer_class(instance).data})
            else:
                context.update(
                    {
                        "errors": self.error_message_formatter(serializer.errors),
                        "status": status.HTTP_400_BAD_REQUEST,
                    }
                )
        except Exception as ex:
            context.update({"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)})
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        operation_summary="Update purchase order", request_body=PurchaseOrderFormSerializer
    )
    def update(self, request, *args, **kwargs):
        """
        This method handle updating purchase order information
        """
        
        context = {"status": status.HTTP_200_OK}
        try:
            data = self.get_data(request)
            instance = self.get_object()
          
            self.user_obj_permission(request, instance)
            
            serializer = self.serializer_form_class(data=data, instance=instance)

            if serializer.is_valid():
                _ = serializer.update(instance, serializer.validated_data)
                context.update(
                    {
                        "data": self.serializer_class(self.get_object()).data,
                        "status": status.HTTP_200_OK,
                    }
                )
            else:
                context.update(
                    {
                        "errors": self.error_message_formatter(serializer.errors),
                        "status": status.HTTP_400_BAD_REQUEST,
                    }
                )
        except Exception as ex:
            context.update({"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)})
        return Response(context, status=context["status"])

    @swagger_auto_schema(
            operation_summary="The endpoint handles purchase order acknowledgement by vendor",
            )
    @action(detail=True, methods=["post"], url_path="acknowledge")
    @method_decorator(vendor_access_only(), name="dispatch")
    def po_acknowledgement(self, request, *args, **kwargs):
        """
        This method handles acknowledgement of new purchase order
        """
        context = {"status": status.HTTP_201_CREATED}
        try:
            instance = self.get_object()
            
            if not instance.vendor or request.user != instance.vendor.user:
                return Response(
                {
                    "status": status.HTTP_403_FORBIDDEN,
                    "message": "You currently do not have access to this resource",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

            if instance.status == POStatusEnum.COMPLETED:
                
                instance.acknowledgment_date = timezone.now()
                instance.save()
                
                context.update(
                        {
                            "data": self.serializer_class(self.get_object()).data,
                            "status": status.HTTP_200_OK,
                        }
                    )
            else:
                context.update(
                    {
                        "message": "Cannot acknowledge Purchase Order with status other than 'completed'",
                        "status": status.HTTP_400_BAD_REQUEST,
                    }
                )
        except Exception as ex:
            context.update({"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)})
        return Response(context, status=context["status"])
