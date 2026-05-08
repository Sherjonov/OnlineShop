from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_name", "unit_price", "quantity", "line_total")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("number", "customer_name", "customer_phone", "region", "district", "total", "status", "created_at")
    list_filter = ("status", "region", "district")
    search_fields = ("number", "customer_name", "customer_phone")
    readonly_fields = ("number", "subtotal", "delivery_fee", "total", "created_at", "updated_at")
    inlines = [OrderItemInline]
    date_hierarchy = "created_at"
