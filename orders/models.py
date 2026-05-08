"""Buyurtma modellari (sodda)."""
from __future__ import annotations

import secrets
import string

from django.conf import settings
from django.db import models

from products.models import Product


def _gen_number() -> str:
    return "QM-" + "".join(secrets.choice(string.digits) for _ in range(8))


class Order(models.Model):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    DELIVERING = "delivering"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    STATUSES = [
        (PENDING, "Kutilmoqda"),
        (CONFIRMED, "Tasdiqlangan"),
        (DELIVERING, "Yetkazilmoqda"),
        (DELIVERED, "Yetkazildi"),
        (CANCELLED, "Bekor qilindi"),
    ]

    number = models.CharField(max_length=16, unique=True, default=_gen_number, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="orders",
    )
    customer_name = models.CharField("Ism", max_length=120)
    customer_phone = models.CharField("Telefon", max_length=32)

    region = models.CharField("Viloyat", max_length=64)
    district = models.CharField("Tuman/Shahar", max_length=64)
    mahalla = models.CharField("Mahalla", max_length=120)
    house = models.CharField("Uy raqami", max_length=32)
    note = models.CharField("Izoh", max_length=255, blank=True, default="")

    subtotal = models.PositiveIntegerField(default=0)
    delivery_fee = models.PositiveIntegerField(default=0)
    total = models.PositiveIntegerField(default=0)

    status = models.CharField(max_length=16, choices=STATUSES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar tarixi"

    def __str__(self) -> str:
        return f"{self.number} — {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name="order_items")
    product_name = models.CharField(max_length=120)
    unit_price = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField(default=1)
    line_total = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Buyurtma elementi"
        verbose_name_plural = "Buyurtma elementlari"

    def __str__(self) -> str:
        return f"{self.product_name} × {self.quantity}"

    def save(self, *args, **kwargs):
        self.line_total = self.unit_price * self.quantity
        super().save(*args, **kwargs)
