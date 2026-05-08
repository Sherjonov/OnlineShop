"""Admin-only mahsulot CRUD JSON endpointlari."""
from __future__ import annotations

import json

from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods

from accounts.models import AdminNotification

from .models import Category, Favorite, Product


def _is_admin(u):
    return u.is_authenticated and (u.is_staff or u.is_superuser)


admin_required = user_passes_test(_is_admin)


@login_required
@admin_required
@require_http_methods(["POST"])
def create_product(request):
    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)

    name = (data.get("name") or "").strip()
    if not name:
        return JsonResponse({"ok": False, "error": "Nom kerak"}, status=400)

    cat_slug = data.get("category") or "fastfood"
    category, _ = Category.objects.get_or_create(
        slug=cat_slug, defaults={"name": cat_slug.title(), "icon": ""}
    )

    product = Product.objects.create(
        name=name,
        category=category,
        emoji=(data.get("emoji") or "")[:8],
        description=(data.get("description") or "")[:1000],
        price=max(0, int(data.get("price") or 0)),
        old_price=int(data["old_price"]) if data.get("old_price") else None,
        badge=data.get("badge") or "",
        weight=(data.get("weight") or "")[:32],
        stock=max(1, min(15, int(data.get("stock") or 15))),
        image_url=(data.get("image_url") or "")[:500],
        is_featured=bool(data.get("is_featured")),
    )
    AdminNotification.objects.create(
        title=f"Yangi mahsulot qo'shildi: {product.name}",
        body=f"{product.category.name} kategoriyasida — {product.price:,} so'm",
    )
    return JsonResponse({"ok": True, "product": product.to_dict()})


@login_required
@admin_required
@require_http_methods(["POST"])
def update_product(request, product_id: int):
    product = get_object_or_404(Product, pk=product_id)
    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)

    for field in ("name", "emoji", "description", "weight", "image_url", "badge"):
        if field in data:
            setattr(product, field, (data.get(field) or "")[:500])
    if "price" in data:
        product.price = max(0, int(data["price"] or 0))
    if "old_price" in data:
        product.old_price = int(data["old_price"]) if data["old_price"] else None
    if "stock" in data:
        product.stock = max(1, min(15, int(data["stock"] or 15)))
    if "is_active" in data:
        product.is_active = bool(data["is_active"])
    if "is_featured" in data:
        product.is_featured = bool(data["is_featured"])
    if "category" in data:
        cat_slug = data["category"]
        category, _ = Category.objects.get_or_create(
            slug=cat_slug, defaults={"name": cat_slug.title()}
        )
        product.category = category
    product.save()
    return JsonResponse({"ok": True, "product": product.to_dict()})


@login_required
@admin_required
@require_http_methods(["POST", "DELETE"])
def delete_product(request, product_id: int):
    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    return JsonResponse({"ok": True})


@login_required
@require_http_methods(["POST"])
def toggle_favorite(request, product_id: int):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)
    if not created:
        favorite.delete()
    return JsonResponse({"ok": True, "liked": created, "product_id": product_id})


@login_required
def list_favorites(request):
    liked_ids = set(
        Favorite.objects.filter(user=request.user).values_list("product_id", flat=True)
    )
    products = Product.objects.filter(pk__in=liked_ids, is_active=True).select_related("category")
    return JsonResponse({
        "ok": True,
        "products": [p.to_dict() for p in products],
        "liked_ids": list(liked_ids),
    })
