from rest_framework.routers import DefaultRouter

from apps.purchase_orders.views import PurchaseOrderViewSet

router = DefaultRouter()

router.register(r"purchase_orders", PurchaseOrderViewSet, basename="purchase-order-api")

