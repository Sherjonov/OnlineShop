"""Savat, checkout, buyurtma viewlari."""
from __future__ import annotations

import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods, require_POST

from products.models import Product
from .models import Order, OrderItem
from . import services


# ============ JSON API Endpoints ============

@require_POST
def api_create_order(request):
    """JSON API for creating orders."""
    try:
        data = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)
    
    first_name = data.get('first_name', '').strip()
    last_name = data.get('last_name', '').strip()
    phone = data.get('phone', '').strip()
    email = data.get('email', '').strip()
    region = data.get('region', '').strip()
    district = data.get('district', '').strip()
    mahalla = data.get('mahalla', '').strip()
    house = data.get('house', '').strip()
    items = data.get('items', [])
    
    if not first_name or not phone or not region:
        return JsonResponse({'ok': False, 'error': 'Ism, telefon va viloyat kerak'}, status=400)
    
    if not items:
        return JsonResponse({'ok': False, 'error': 'Savat bo\'sh'}, status=400)
    
    # Calculate totals
    subtotal = 0
    order_items = []
    for item in items:
        try:
            product = Product.objects.get(pk=item['id'])
            qty = min(max(1, int(item.get('qty', 1))), 15)  # Limit 1-15
            line_total = product.price * qty
            subtotal += line_total
            order_items.append({
                'product': product,
                'product_name': product.name,
                'unit_price': product.price,
                'quantity': qty,
                'line_total': line_total,
            })
        except (Product.DoesNotExist, KeyError, ValueError):
            continue
    
    if not order_items:
        return JsonResponse({'ok': False, 'error': 'Mahsulotlar topilmadi'}, status=400)
    
    # Delivery fee
    tashkent = ['Toshkent shahar', 'Toshkent viloyati']
    delivery_fee = 0 if region in tashkent else 30000
    total = subtotal + delivery_fee
    
    # Create order
    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        customer_name=f"{first_name} {last_name}".strip(),
        customer_phone=phone,
        region=region,
        district=district,
        mahalla=mahalla,
        house=house,
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        total=total,
    )
    
    # Create order items
    for item_data in order_items:
        OrderItem.objects.create(order=order, **item_data)
    
    return JsonResponse({
        'ok': True,
        'order_number': order.number,
        'total': total,
    })


def api_list_orders(request):
    """JSON API for listing orders (admin sees all, users see own)."""
    if not request.user.is_authenticated:
        return JsonResponse({'ok': False, 'error': 'Kirish kerak'}, status=401)
    
    if request.user.is_admin:
        orders = Order.objects.select_related('user').prefetch_related('items').all()[:100]
    else:
        orders = Order.objects.filter(user=request.user).prefetch_related('items').all()[:50]
    
    return JsonResponse({
        'ok': True,
        'orders': [
            {
                'id': o.pk,
                'number': o.number,
                'customer_name': o.customer_name,
                'phone': o.customer_phone,
                'region': o.region,
                'district': o.district,
                'items_summary': ', '.join([f"{i.product_name} x{i.quantity}" for i in o.items.all()[:3]]),
                'subtotal': o.subtotal,
                'delivery_fee': o.delivery_fee,
                'total': o.total,
                'status': o.status,
                'status_display': o.get_status_display(),
                'created_at': o.created_at.strftime('%Y-%m-%d %H:%M'),
            }
            for o in orders
        ]
    })


# ============ Traditional Views ============

def cart_view(request):
    summary = services.cart_summary(request.session)
    return render(request, "orders/cart.html", {"summary": summary})


@require_http_methods(["POST"])
def cart_add(request):
    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")
    pid = data.get("product_id")
    qty = data.get("quantity", 1)
    if not pid:
        return JsonResponse({"ok": False, "error": "product_id majburiy"}, status=400)
    services.cart_add(request.session, int(pid), int(qty))
    summary = services.cart_summary(request.session)
    return JsonResponse({"ok": True, **summary})


@require_http_methods(["POST"])
def cart_set(request):
    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")
    pid = data.get("product_id")
    qty = data.get("quantity", 0)
    if not pid:
        return JsonResponse({"ok": False, "error": "product_id majburiy"}, status=400)
    services.cart_set(request.session, int(pid), int(qty))
    summary = services.cart_summary(request.session)
    return JsonResponse({"ok": True, **summary})


@require_http_methods(["POST"])
def cart_remove(request):
    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")
    pid = data.get("product_id")
    if not pid:
        return JsonResponse({"ok": False, "error": "product_id majburiy"}, status=400)
    services.cart_remove(request.session, int(pid))
    summary = services.cart_summary(request.session)
    return JsonResponse({"ok": True, **summary})


@require_http_methods(["POST"])
def cart_clear(request):
    services.cart_clear(request.session)
    return JsonResponse({"ok": True, "items": [], "total_items": 0, "subtotal": 0, "delivery_fee": 0, "total": 0})


def cart_summary(request):
    return JsonResponse(services.cart_summary(request.session))


def checkout_view(request):
    summary = services.cart_summary(request.session)
    if not summary["items"]:
        messages.warning(request, "Savatingiz bo'sh.")
        return redirect("core:home")
    if request.method == "POST":
        try:
            order = services.create_order(
                request.session,
                user=request.user,
                customer_name=(request.POST.get("customer_name") or "").strip(),
                customer_phone=(request.POST.get("customer_phone") or "").strip(),
                region=(request.POST.get("region") or "").strip(),
                district=(request.POST.get("district") or "").strip(),
                mahalla=(request.POST.get("mahalla") or "").strip(),
                house=(request.POST.get("house") or "").strip(),
                note=(request.POST.get("note") or "").strip(),
            )
        except ValueError as e:
            messages.error(request, str(e))
            return redirect("orders:cart")
        messages.success(request, f"Buyurtmangiz qabul qilindi! Raqam: {order.number}")
        return redirect("orders:detail", number=order.number)
    return render(request, "orders/checkout.html", {"summary": summary})


def order_detail(request, number: str):
    order = get_object_or_404(Order, number=number)
    return render(request, "orders/detail.html", {"order": order})
