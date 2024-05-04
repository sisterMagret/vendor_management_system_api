from rest_framework.routers import DefaultRouter

from apps.authentication.views import (AuthViewSet, BuyerSettingsViewSet,
                                       UserViewSet, VendorViewSet)

router = DefaultRouter()

router.register(r"users", UserViewSet, basename="user-api")
router.register(r"auth", AuthViewSet, basename="auth-api")
router.register(r"vendors", VendorViewSet, basename="vendor-profile-api")
router.register(
    r"buyers", BuyerSettingsViewSet, basename="buyer-profile-api"
)
