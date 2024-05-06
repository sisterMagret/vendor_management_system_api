from django.contrib import admin

from .models import BuyerSettings, User, VendorProfile


class UserAdmin(admin.ModelAdmin):

    search_fields = ["first_name", "last_name", "mobile", "email", "group", "city"]
    list_display = (
        "id",
        "mobile",
        "email",
        "first_name",
        "last_name",
        "group",
        "state",
        "city",
        "zip_code",
        "is_accept_terms_and_condition",
    )
    list_per_page = 100


class BuyerSettingsAdmin(admin.ModelAdmin):
    search_fields = ("id", "business_name")
    list_display = ("id", "business_name", "user")


class VendorProfileAdmin(admin.ModelAdmin):
    search_fields = ("id", "business_name") 
    list_display = (
        "id", 
        "user", 
        "vendor_code",
        "on_time_delivery_rate",
        "quality_rating_avg",
        "average_response_time",
        "fulfillment_rate",
         "business_name"
        )

admin.site.register(User, UserAdmin)
admin.site.register(BuyerSettings, BuyerSettingsAdmin)
admin.site.register(VendorProfile, VendorProfileAdmin)
