from django.contrib import admin
from .models import PurchaseOrder
# Register your models here.


class PurchaseOrderAdmin(admin.ModelAdmin):
    search_fields = (
        "po_number",
        "order_date",
        "delivery_date",
        "status",
        "quality_rating",
        "issued_date",
        "acknowledgment_date",
        "updated_at"
    )
    list_display = (
        "po_number",
        "order_date",
        "delivery_date",
        "status",
        "quantity",
        "quality_rating",
        "issued_date",
        "acknowledgment_date",
        "updated_at"
    )

admin.register(PurchaseOrder, PurchaseOrderAdmin)