import logging
import uuid

from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import Group
from rest_framework import serializers

from apps.users.models import BuyerSettings, User, VendorProfile
from apps.utils.constant import DATETIME_FORMAT
from apps.utils.enums import UserGroup
from apps.utils.random_number_generator import unique_alpha_numeric_generator, unique_number_generator

logger = logging.getLogger("authentication")


def generate_uuid(model, column):
    unique = str(uuid.uuid4())
    kwargs = {column: unique}
    qs_exists = model.objects.filter(**kwargs).exists()
    if qs_exists:
        return generate_uuid(model, column)
    return unique


class UserSerializer(serializers.ModelSerializer):
    joined_at = serializers.DateTimeField(
        format=DATETIME_FORMAT, read_only=True
    )
    group = serializers.CharField(read_only=True)
    avatar = serializers.SerializerMethodField("get_avatar")

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "group",
            "mobile",
            "email",
            "country",
            "state",
            "city",
            "address",
            "avatar",
            "joined_at",
        ]

    @staticmethod
    def get_avatar(obj):
        if obj.avatar:
            return f"{settings.BASE_BE_URL}{obj.avatar.url}"
        return None


class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "country",
            "state",
            "city",
            "address",
        ]


class UserFormSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    mobile = serializers.CharField(required=True)
    email = serializers.CharField(required=False)
    country = serializers.CharField(required=False)
    state = serializers.CharField(required=False)
    zip_code = serializers.CharField(required=False)
    address = serializers.CharField(required=False)

    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            instance.__setattr__(k, v)
        instance.save()
        return instance

    def create(self, validated_data):
        pass

    def validate(self, attrs):
        return attrs


class BuyerSettingsSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = BuyerSettings
        fields = ["id", "user", "business_name"]


class BuyerFormSerializer(serializers.Serializer):
    business_name = serializers.CharField(required=False)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        _ = BuyerSettings.objects.filter(id=instance.id).update(
            **validated_data
        )
        instance.refresh_from_db()
        return instance

    def validate(self, attrs):
        if BuyerSettings.objects.filter(
            business_name=attrs.get("business_name")
        ).exists():
            raise Exception("Business name already exists")
        return attrs


class BuyerRegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.CharField(required=True)
    mobile = serializers.CharField(required=True)
    password = serializers.CharField(required=True, min_length=8)
    business_name = serializers.CharField(required=False)
    is_accept_terms_and_condition = serializers.BooleanField(required=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        payload = {
            "user": {
                "first_name": validated_data.get("first_name"),
                "last_name": validated_data.get("last_name"),
                "email": validated_data.get("email"),
                "mobile": validated_data.get("mobile"),
                "password": validated_data.get("password"),
                "is_accept_terms_and_condition": validated_data.get(
                    "is_accept_terms_and_condition"
                ),
            },
            "setting": {
                "business_name": validated_data.get("business_name"),
            },
        }
        user = payload.get("user")
        user.update({"username": generate_uuid(User, "username")})
        instance = User.objects.create(**user)
        instance.set_password(user.get("password"))
        group, _ = Group.objects.get_or_create(name=UserGroup.BUYER)
        # create user account settings
        payload.get("setting").update({"user": instance})
        _ = BuyerSettings.objects.create(**payload.get("setting"))
        instance.groups.add(group)
        instance.save()
        # send email notification to buyer
        return instance

    def validate(self, attrs):
        if User.objects.filter(email=attrs.get("email")).exists():
            raise Exception("User with this email already exist")
        if User.objects.filter(mobile=attrs.get("mobile")).exists():
            raise Exception("User with this mobile number already exist")
        return attrs


class VendorRegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    mobile = serializers.CharField(required=True)
    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True, min_length=8)
    is_accept_terms_and_condition = serializers.BooleanField(required=True)
    address = serializers.CharField(required=False)
    state = serializers.CharField(required=False)
    country = serializers.CharField(required=False)
    city = serializers.CharField(required=False)
    zip_code = serializers.CharField(required=False)
    business_name = serializers.CharField(required=False)
   

    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            instance.__setattr__(k, v)
        instance.save()
        return instance

    def create(self, validated_data):
        payload = {
            "username": generate_uuid(User, "username"),
            "first_name": validated_data.get("first_name"),
            "last_name": validated_data.get("last_name"),
            "mobile": validated_data.get("mobile"),
            "email": validated_data.get("email"),
            "is_accept_terms_and_condition": validated_data.get(
                "is_accept_terms_and_condition"
            ),
        }
        instance = User.objects.create(**payload)
        instance.set_password(validated_data.get("password"))
        instance.save()
        group, _ = Group.objects.get_or_create(name=UserGroup.VENDOR)
        _ = VendorProfile.objects.create(
            **{
                "user": instance,
                "vendor_code": unique_alpha_numeric_generator(VendorProfile, "vendor_code", 8),
                "business_name": validated_data.get("business_name")
            }
        )
        instance.groups.add(group)
        instance.save()
        return instance


class VendorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = VendorProfile
        fields = "__all__"


class VendorMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorProfile
        fields = [
            "id",
            "vendor_code",
            "on_time_delivery_rate",
            "quality_rating_avg",
            "average_response_time",
            "fulfillment_rate"
        ]


class VendorFormSerializer(serializers.Serializer):
    user = UserSerializer(read_only=True)

    def update(self, instance, validated_data):
        user = validated_data.pop("user", None)

        if user:
            _ = User.objects.filter(id=instance.user.id).update(**user)

        for k, v in validated_data.items():
            instance.__setattr__(k, v)
        return instance

    def create(self, validated_data):
        pass
