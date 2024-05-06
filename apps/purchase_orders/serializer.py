from datetime import datetime
import logging

from django.apps import apps
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from apps.users.models import VendorProfile
from apps.users.serializer import UserSerializer, VendorSerializer
from .models import Item, PurchaseOrder
from apps.utils.constant import DATETIME_FORMAT
from apps.utils.enums import POStatusEnum


logger = logging.getLogger("purchase_order")


class ItemSerializer(serializers.Serializer):
    """Purchase order item serializer"""
    name = serializers.CharField(max_length=255)
    quantity = serializers.IntegerField(default=1, min_value=1)

    def create(self, validated_data):
        pass
   

class PurchaseOrderSerializer(serializers.ModelSerializer):
    vendor = VendorSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    order_date = serializers.DateTimeField(
        format=DATETIME_FORMAT, read_only=True
    )
    delivery_date = serializers.DateTimeField(
        format=DATETIME_FORMAT, required=True
    )
    acknowledgment_date = serializers.DateTimeField(
        format=DATETIME_FORMAT, read_only=True
    )
    issue_date = serializers.DateTimeField(
        format=DATETIME_FORMAT, read_only=True
    )
    items = ItemSerializer(many=True, read_only=True)
    quantity = serializers.IntegerField(default=1)

    class Meta:
        model = PurchaseOrder
        fields = "__all__"


class PurchaseOrderFormSerializer(serializers.Serializer):
    vendor_id = serializers.CharField(required=False)
    delivery_date = serializers.DateTimeField(
        format=DATETIME_FORMAT, required=False
    )
    quality_rating = serializers.FloatField(default=0.0)
    items = ItemSerializer(many=True, required=False)
    status = serializers.ChoiceField(choices=POStatusEnum.choices(), default=POStatusEnum.PENDING)

    def create(self, validated_data):
        items = validated_data.pop('items', [])
       
        instance = PurchaseOrder.objects.create(**validated_data)
        item_instances = []
        if len(items) > 0:
            instance
            for item in items:
                obj, _ = Item.objects.get_or_create(**item)
                item_instances.append(obj)
            instance.items.set(item_instances)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        items = validated_data.pop("items", None)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        if items is not None:
            instance.items.clear()
            for item in items:
                po, _ = Item.objects.get_or_create(**item)
                instance.items.add(po)
        instance.save()
        return instance

    def validate(self, attrs):
        
        if attrs.get("vendor_id"):
            vendor_id = attrs.pop("vendor_id")
            vendor = get_object_or_404(VendorProfile, pk=vendor_id)
            attrs.update(
                {
                    "issue_date": datetime.now(),
                    "vendor": vendor
                }
            )
        if attrs.get("items") is not None:
            unique_items = {d['name']: d for d in attrs.get("items")}.values() 
            quantity = 0
            for item in  unique_items: 
            
                if not item.get("quantity"):
                    raise serializers.ValidationError(f"Quantity is required for {item.get('name')}")
            
                if int(item["quantity"]) < 1:
                    raise serializers.ValidationError("Quantity must be greater than 0")
            
                quantity += int(item["quantity"])
            attrs.update(quantity=quantity)
     
        return attrs
    
    def validate_quality_rating(self, value):
        if value < 0.0 or value > 5.0:
            raise serializers.ValidationError("Quality rating must be between 0.0 and 5.0")
        return value


class PurchaseOrderAcknowledgementSerializer(serializers.Serializer):
    acknowledgment_date = serializers.DateTimeField(
        format=DATETIME_FORMAT, required=True
    )

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        _ = PurchaseOrder.objects.filter(id=instance.id).update(**validated_data)
        # use django signal to send trigger the recalculation of average_response_time.
        return instance