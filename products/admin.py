"""Products admin paneli."""
from django.contrib import admin

from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "icon", "is_active", "sort_order")
    list_editable = ("sort_order", "is_active")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "stock", "badge", "is_active", "is_featured")
    list_editable = ("price", "stock", "is_active", "is_featured")
    list_filter = ("category", "is_active", "is_featured", "badge")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
