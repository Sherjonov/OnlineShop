"""Mahsulot modellari (sodda)."""
from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField("Nomi", max_length=64)
    slug = models.SlugField("Slug", unique=True, max_length=80)
    icon = models.CharField("Emoji", max_length=8, blank=True, default="")
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"
        ordering = ["sort_order", "name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name) or "kat"
        super().save(*args, **kwargs)


class Product(models.Model):
    BADGES = [
        ("", "Yo'q"),
        ("hot", "Hot"),
        ("new", "Yangi"),
        ("sale", "Chegirma"),
    ]

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    name = models.CharField("Nomi", max_length=120)
    slug = models.SlugField(unique=True, max_length=140, blank=True)
    emoji = models.CharField("Emoji", max_length=8, blank=True, default="")
    description = models.TextField("Tavsif", blank=True, default="")
    price = models.PositiveIntegerField("Narx (so'm)", default=0)
    old_price = models.PositiveIntegerField(null=True, blank=True)
    badge = models.CharField(max_length=8, choices=BADGES, blank=True, default="")
    image_url = models.URLField(blank=True, max_length=500, default="")
    weight = models.CharField(max_length=32, blank=True, default="")
    stock = models.PositiveIntegerField("Qoldiq", default=15)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"
        ordering = ["sort_order", "-created_at"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or "mahsulot"
            slug = base
            i = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def to_dict(self) -> dict:
        return {
            "id": self.pk,
            "name": self.name,
            "slug": self.slug,
            "emoji": self.emoji or "",
            "description": self.description,
            "price": self.price,
            "old_price": self.old_price,
            "badge": self.badge,
            "category": self.category.slug,
            "category_name": self.category.name,
            "weight": self.weight,
            "stock": self.stock,
            "image": self.image_url,
        }


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="favorited_by",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Yoqtirilgan mahsulot"
        verbose_name_plural = "Yoqtirilgan mahsulotlar"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "product"], name="uniq_user_product_favorite"),
        ]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.product_id}"
