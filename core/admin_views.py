"""In-page admin paneli viewlari."""
from __future__ import annotations

from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from accounts.models import LoginActivity
from orders.models import Order
from products.models import Category, Product

User = get_user_model()


def _is_admin(u):
    return u.is_authenticated and (u.is_staff or u.is_superuser)


admin_required = user_passes_test(_is_admin, login_url="/accounts/login/")


@login_required
@admin_required
def dashboard(request):
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    stats = {
        "orders_today": Order.objects.filter(created_at__date=today).count(),
        "orders_week": Order.objects.filter(created_at__date__gte=week_ago).count(),
        "orders_total": Order.objects.count(),
        "users_total": User.objects.count(),
        "products_total": Product.objects.filter(is_active=True).count(),
        "revenue_total": Order.objects.aggregate(s=Sum("total"))["s"] or 0,
        "pending": Order.objects.filter(status=Order.PENDING).count(),
    }
    recent_orders = Order.objects.select_related("user").prefetch_related("items")[:10]
    recent_logins = LoginActivity.objects.all()[:10]
    return render(request, "admin_panel/dashboard.html", {
        "stats": stats,
        "recent_orders": recent_orders,
        "recent_logins": recent_logins,
    })


# ---------- Mahsulotlar ---------------------------------------------------
@login_required
@admin_required
def products_list(request):
    q = (request.GET.get("q") or "").strip()
    products = Product.objects.select_related("category").order_by("-created_at")
    if q:
        products = products.filter(name__icontains=q)
    return render(request, "admin_panel/products.html", {
        "products": products,
        "categories": Category.objects.all(),
        "search_query": q,
    })


@login_required
@admin_required
def product_form(request, product_id: int | None = None):
    product = get_object_or_404(Product, pk=product_id) if product_id else None
    categories = Category.objects.all()
    if request.method == "POST":
        cat_slug = request.POST.get("category") or "umumiy"
        category, _ = Category.objects.get_or_create(
            slug=cat_slug, defaults={"name": cat_slug.title()}
        )
        data = {
            "name": (request.POST.get("name") or "").strip(),
            "category": category,
            "emoji": (request.POST.get("emoji") or "")[:8],
            "description": (request.POST.get("description") or "")[:1000],
            "price": max(0, int(request.POST.get("price") or 0)),
            "old_price": int(request.POST.get("old_price")) if request.POST.get("old_price") else None,
            "badge": request.POST.get("badge") or "",
            "weight": (request.POST.get("weight") or "")[:32],
            "stock": max(1, min(15, int(request.POST.get("stock") or 15))),
            "image_url": (request.POST.get("image_url") or "")[:500],
            "is_active": bool(request.POST.get("is_active")),
            "is_featured": bool(request.POST.get("is_featured")),
        }
        if not data["name"]:
            messages.error(request, "Mahsulot nomi kerak.")
        else:
            if product:
                for k, v in data.items():
                    setattr(product, k, v)
                product.save()
                messages.success(request, "Mahsulot yangilandi.")
            else:
                product = Product.objects.create(**data)
                from accounts.models import AdminNotification
                AdminNotification.objects.create(
                    title=f"Yangi mahsulot qo'shildi: {product.name}",
                    body=f"{category.name} — {product.price:,} so'm",
                )
                messages.success(request, "Mahsulot qo'shildi.")
            return redirect("admin_panel:products")
    return render(request, "admin_panel/product_form.html", {
        "product": product, "categories": categories,
    })


@login_required
@admin_required
@require_http_methods(["POST"])
def product_toggle(request, product_id: int):
    product = get_object_or_404(Product, pk=product_id)
    product.is_active = not product.is_active
    product.save(update_fields=["is_active"])
    return JsonResponse({"ok": True, "is_active": product.is_active})


@login_required
@admin_required
@require_http_methods(["POST"])
def product_delete(request, product_id: int):
    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    messages.success(request, "Mahsulot o'chirildi.")
    return redirect("admin_panel:products")


# ---------- Buyurtmalar tarixi -------------------------------------------
@login_required
@admin_required
def orders_history(request):
    status = request.GET.get("status") or ""
    orders = Order.objects.select_related("user").prefetch_related("items").order_by("-created_at")
    if status:
        orders = orders.filter(status=status)
    # Buyurtma raqami: oxirdan boshlab, eng yangisi 1-bo'lib chiqadi.
    orders_list = list(orders)
    enriched = []
    for idx, o in enumerate(orders_list, start=1):
        enriched.append({"order": o, "rank": idx})
    return render(request, "admin_panel/orders.html", {
        "orders": enriched,
        "active_status": status,
        "statuses": Order.STATUSES,
    })


@login_required
@admin_required
@require_http_methods(["POST"])
def order_status(request, number: str):
    order = get_object_or_404(Order, number=number)
    new = request.POST.get("status")
    if new and new in dict(Order.STATUSES):
        order.status = new
        order.save(update_fields=["status", "updated_at"])
    return redirect("admin_panel:orders")


# ---------- Kirish/Chiqish jadvali ---------------------------------------
@login_required
@admin_required
def login_activity(request):
    activities = LoginActivity.objects.select_related("user").all()[:500]
    return render(request, "admin_panel/login_activity.html", {"activities": activities})


# ---------- Foydalanuvchilar ---------------------------------------------
@login_required
@admin_required
def users_list(request):
    q = (request.GET.get("q") or "").strip()
    users = User.objects.all().order_by("-created_at")
    if q:
        users = users.filter(username__icontains=q) | users.filter(email__icontains=q)
    return render(request, "admin_panel/users.html", {"users": users, "search_query": q})


@login_required
@admin_required
@require_http_methods(["POST"])
def user_toggle(request, user_id: int):
    u = get_object_or_404(User, pk=user_id)
    if u.pk == request.user.pk:
        return JsonResponse({"ok": False, "error": "O'zingizni o'chira olmaysiz"}, status=400)
    u.is_active = not u.is_active
    u.save(update_fields=["is_active"])
    return JsonResponse({"ok": True, "is_active": u.is_active})
