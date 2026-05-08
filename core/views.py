"""Asosiy frontend viewlar."""
import json

from django.db.models import Count, Q
from django.shortcuts import render

from products.models import Category, Product


def home(request):
    cat_slug = request.GET.get("category", "all")
    q = (request.GET.get("q") or "").strip()

    products = Product.objects.filter(is_active=True).select_related("category")
    if cat_slug and cat_slug != "all":
        products = products.filter(category__slug=cat_slug)
    if q:
        products = products.filter(Q(name__icontains=q) | Q(description__icontains=q))

    categories = Category.objects.filter(is_active=True).annotate(
        cnt=Count("products", filter=Q(products__is_active=True))
    )

    # JSON for JS
    products_list = list(products)
    products_json = json.dumps([
        {
            "id": p.pk,
            "name": p.name,
            "slug": p.slug,
            "emoji": p.emoji or "🍽️",
            "description": p.description or "",
            "price": p.price,
            "old_price": p.old_price,
            "badge": p.badge or "",
            "category": p.category.slug,
            "category_name": p.category.name,
            "weight": p.weight or "",
            "stock": p.stock,
            "image": p.image_url or "",
        }
        for p in products_list
    ], ensure_ascii=False)

    return render(request, "index.html", {
        "products": products_list,
        "products_json": products_json,
        "products_count": len(products_list),
        "categories": categories,
        "active_category": cat_slug,
        "search_query": q,
        "total_products": len(products_list),
    })


def page_not_found(request, exception=None):
    return render(request, "404.html", status=404)


def server_error(request):
    return render(request, "500.html", status=500)
