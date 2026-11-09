from django.contrib import admin

from .models import Order, Product, RefundRequest


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "in_stock")
    list_filter = ("in_stock", "category")
    search_fields = ("name", "description", "category")
    list_editable = ("in_stock",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "product_name",
        "amount",
        "status",
        "carrier",
        "tracking_number",
        "created_at",
    )
    list_filter = ("status", "carrier", "created_at")
    search_fields = (
        "product_name",
        "tracking_number",
        "user__username",
        "user__email",
    )
    date_hierarchy = "created_at"
    autocomplete_fields = ("user", "product")
    list_select_related = ("user", "product")


@admin.register(RefundRequest)
class RefundRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "user", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = (
        "order__product_name",
        "user__username",
        "user__email",
        "reason",
    )
    date_hierarchy = "created_at"
    autocomplete_fields = ("order", "user")
    list_select_related = ("order", "user")
