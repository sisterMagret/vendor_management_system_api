from django.contrib import admin

from .models import BuyerSettings, User


class UserAdmin(admin.ModelAdmin):

    search_fields = ["first_name", "last_name", "mobile", "email"]
    list_display = (
        "id",
        "mobile",
        "email",
        "first_name",
        "last_name",
        "state",
        "city",
        "zip_code",
        "is_accept_terms_and_condition",
    )
    list_per_page = 100


class BuyerSettingsAdmin(admin.ModelAdmin):
    list_display = ("id", "business_name", "user")


admin.site.register(User, UserAdmin)
admin.site.register(BuyerSettings, BuyerSettingsAdmin)
