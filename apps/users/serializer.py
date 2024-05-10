import logging

from django.contrib.auth.models import Group
from rest_framework import serializers

from apps.users.models import BuyerSettings, User, VendorProfile
from apps.utils.constant import DATETIME_FORMAT
from apps.utils.enums import UserGroup
from apps.utils.random_number_generator import unique_alpha_numeric_generator, generate_uuid

logger = logging.getLogger("users")


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    """

    joined_at = serializers.DateTimeField(format=DATETIME_FORMAT, read_only=True)
    group = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "username", "first_name", "last_name", "group", "mobile",
            "email", "country", "state", "city", "address", "joined_at",
            "zip_code"
        ]


class UserMiniSerializer(serializers.ModelSerializer):
    """
    Minimal User serializer for reduced data representation.
    """

    class Meta:
        model = User
        fields = ["first_name", "last_name", "country", "state", "city", "address"]


class UserFormSerializer(serializers.Serializer):
    """
    Serializer for User form data.
    """

    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    mobile = serializers.CharField(required=True)
    email = serializers.CharField(required=False)
    country = serializers.CharField(required=False)
    city = serializers.CharField(required=False)
    state = serializers.CharField(required=False)
    zip_code = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    username = serializers.CharField(required=False)

    def update(self, instance, validated_data):
        """
        Update method for UserFormSerializer.
        """
        for k, v in validated_data.items():
            instance.__setattr__(k, v)
        instance.save()
        return instance

    def create(self, validated_data):
        """
        Create method for UserFormSerializer.
        """
        pass

    def validate(self, attrs):
        """
        Validate method for UserFormSerializer.
        """
        return attrs


class BuyerSettingsSerializer(serializers.ModelSerializer):
    """
    Serializer for BuyerSettings model.
    """

    user = UserSerializer(read_only=True)

    class Meta:
        model = BuyerSettings
        fields = ["id", "user", "business_name"]


class BuyerMiniSerializer(serializers.Serializer):
    """
    Minimal Buyer serializer for reduced data representation.
    """

    business_name = serializers.CharField(required=False)


class BuyerFormSerializer(serializers.Serializer):
    """
    Serializer for Buyer form data.
    """

    settings = BuyerMiniSerializer(required=False)
    user = UserFormSerializer(required=False)

    def create(self, validated_data):
        """
        Create method for BuyerFormSerializer.
        """
        pass

    def update(self, instance, validated_data):
        """
        Update method for BuyerFormSerializer.
        """
        if validated_data.get("settings"):
            _ = BuyerSettings.objects.filter(id=instance.id).update(**validated_data.get("settings"))
        instance.refresh_from_db()
        if validated_data.get("user"):
            for k, v in validated_data.get("user").items():
                setattr(instance.user, k, v)
            instance.user.save()
        return instance


class BuyerRegistrationSerializer(serializers.Serializer):
    """
    Serializer for Buyer registration.
    """

    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.CharField(required=True)
    mobile = serializers.CharField(required=True)
    password = serializers.CharField(required=True, min_length=8)
    business_name = serializers.CharField(required=False)
    is_accept_terms_and_condition = serializers.BooleanField(required=True)

    def update(self, instance, validated_data):
        """
        Update method for BuyerRegistrationSerializer.
        """
        pass

    def create(self, validated_data):
        """
        Create method for BuyerRegistrationSerializer.
        """
        payload = {
            "user": {
                "first_name": validated_data.get("first_name"),
                "last_name": validated_data.get("last_name"),
                "email": validated_data.get("email"),
                "mobile": validated_data.get("mobile"),
                "password": validated_data.get("password"),
                "is_accept_terms_and_condition": validated_data.get("is_accept_terms_and_condition"),
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
        payload.get("setting").update({"user": instance})
        _ = BuyerSettings.objects.create(**payload.get("setting"))
        instance.groups.add(group)
        instance.save()
        return instance

    def validate(self, attrs):
        """
        Validate method for BuyerRegistrationSerializer.
        """
        if User.objects.filter(email=attrs.get("email")).exists():
            raise serializers.ValidationError("User with this email already exists")

        if User.objects.filter(mobile=attrs.get("mobile")).exists():
            raise serializers.ValidationError("User with this mobile number already exists")

        if VendorProfile.objects.filter(business_name=attrs.get("business_name")).exists() \
                or BuyerSettings.objects.filter(business_name=attrs.get("business_name")).exists():
            raise serializers.ValidationError("Business name already exists")

        return attrs


class VendorRegistrationSerializer(serializers.Serializer):
    """
    Serializer for Vendor registration.
    """

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
        """
        Update method for VendorRegistrationSerializer.
        """
        for k, v in validated_data.items():
            instance.__setattr__(k, v)
        instance.save()
        return instance

    def create(self, validated_data):
        """
        Create method for VendorRegistrationSerializer.
        """
        payload = {
            "username": generate_uuid(User, "username"),
            "first_name": validated_data.get("first_name"),
            "last_name": validated_data.get("last_name"),
            "mobile": validated_data.get("mobile"),
            "email": validated_data.get("email"),
            "is_accept_terms_and_condition": validated_data.get("is_accept_terms_and_condition"),
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

    def validate(self, attrs):
        """
        Validate method for VendorRegistrationSerializer.
        """
        if User.objects.filter(email=attrs.get("email")).exists():
            raise serializers.ValidationError("User with this email already exists")

        if User.objects.filter(mobile=attrs.get("mobile")).exists():
            raise serializers.ValidationError("User with this mobile number already exists")

        if VendorProfile.objects.filter(business_name=attrs.get("business_name")).exists() \
                or BuyerSettings.objects.filter(business_name=attrs.get("business_name")).exists():
            raise serializers.ValidationError("Business name already exists")

        return attrs


class VendorSerializer(serializers.ModelSerializer):
    """
    Serializer for VendorProfile model.
    """

    user = UserSerializer(read_only=True)

    class Meta:
        model = VendorProfile
        fields = "__all__"


class VendorMiniViewSerializer(serializers.ModelSerializer):
    """
    Minimal serializer for VendorProfile for reduced data representation.
    """

    user = UserMiniSerializer(read_only=True)

    class Meta:
        model = VendorProfile
        fields = ["business_name"]


class VendorMiniUpdateSerializer(serializers.Serializer):
    """
    Serializer for minimal updates to VendorProfile.
    """

    business_name = serializers.CharField(required=False)


class VendorFormSerializer(serializers.Serializer):
    """
    Serializer for Vendor form data.
    """

    user = UserFormSerializer(required=False)
    settings = VendorMiniUpdateSerializer(required=False)

    def update(self, instance, validated_data):
        """
        Update method for VendorFormSerializer.
        """
        if validated_data.get("settings"):
            _ = VendorProfile.objects.filter(id=instance.id).update(**validated_data.get("settings"))
        instance.refresh_from_db()
        if validated_data.get("user"):
            for k, v in validated_data.get("user").items():
                setattr(instance.user, k, v)
            instance.user.save()
        return instance

    def create(self, validated_data):
        """
        Create method for VendorFormSerializer.
        """
        pass


class VendorHistoricalPerformanceSerializer(serializers.ModelSerializer):
    """
    Serializer for historical performance of vendors.
    """

    vendor = VendorSerializer(read_only=True)
    on_time_delivery_rate = serializers.FloatField(required=False)
    quality_rating_avg = serializers.FloatField(required=False)
    avg_response_time = serializers.FloatField(required=False)
    fulfillment_rate = serializers.FloatField(required=False)

    class Meta:
        model = VendorProfile
        fields = [
            "vendor", "on_time_delivery_rate", "quality_rating_avg", 
            "avg_response_time", "fulfillment_rate",
        ]
