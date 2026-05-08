"""Sessiya orqali savat (1..15 chegara) va buyurtma yaratish."""
from __future__ import annotations

from django.conf import settings
from django.db import transaction

from products.models import Product

from .models import Order, OrderItem


CART_KEY = "cart"
MIN_QTY = 1
MAX_QTY = 15


def _get_cart(session) -> dict:
    cart = session.get(CART_KEY)
    if not isinstance(cart, dict):
        cart = {}
        session[CART_KEY] = cart
    return cart


def _save(session, cart):
    session[CART_KEY] = cart
    session.modified = True


def cart_add(session, product_id: int, quantity: int = 1) -> dict:
    cart = _get_cart(session)
    pid = str(product_id)
    current = int(cart.get(pid, 0))
    new_qty = current + max(1, int(quantity))
    new_qty = max(MIN_QTY, min(MAX_QTY, new_qty))
    cart[pid] = new_qty
    _save(session, cart)
    return cart


def cart_set(session, product_id: int, quantity: int) -> dict:
    cart = _get_cart(session)
    pid = str(product_id)
    q = int(quantity)
    if q <= 0:
        cart.pop(pid, None)
    else:
        cart[pid] = max(MIN_QTY, min(MAX_QTY, q))
    _save(session, cart)
    return cart


def cart_remove(session, product_id: int) -> dict:
    cart = _get_cart(session)
    cart.pop(str(product_id), None)
    _save(session, cart)
    return cart


def cart_clear(session):
    session[CART_KEY] = {}
    session.modified = True


def cart_summary(session) -> dict:
    cart = _get_cart(session)
    if not cart:
        return {"items": [], "total_items": 0, "subtotal": 0, "delivery_fee": 0, "total": 0}

    pids = [int(p) for p in cart.keys()]
    products = {p.pk: p for p in Product.objects.filter(pk__in=pids, is_active=True)}

    items = []
    subtotal = 0
    total_qty = 0
    for pid_str, qty in list(cart.items()):
        p = products.get(int(pid_str))
        if not p:
            cart.pop(pid_str, None)
            continue
        line = p.price * qty
        subtotal += line
        total_qty += qty
        items.append({
            "id": p.pk, "name": p.name, "emoji": p.emoji,
            "price": p.price, "quantity": qty, "line_total": line,
            "image": p.image_url, "weight": p.weight,
        })

    delivery_fee = 0
    if subtotal > 0 and subtotal < settings.FREE_DELIVERY_FROM:
        delivery_fee = settings.DELIVERY_FEE
    total = subtotal + delivery_fee
    _save(session, cart)
    return {
        "items": items,
        "total_items": total_qty,
        "subtotal": subtotal,
        "delivery_fee": delivery_fee,
        "total": total,
    }


@transaction.atomic
def create_order(session, *, user, customer_name, customer_phone, region, district, mahalla, house, note=""):
    summary = cart_summary(session)
    if not summary["items"]:
        raise ValueError("Savat bo'sh")

    order = Order.objects.create(
        user=user if user and user.is_authenticated else None,
        customer_name=customer_name,
        customer_phone=customer_phone,
        region=region,
        district=district,
        mahalla=mahalla,
        house=house,
        note=note,
        subtotal=summary["subtotal"],
        delivery_fee=summary["delivery_fee"],
        total=summary["total"],
    )
    for it in summary["items"]:
        OrderItem.objects.create(
            order=order,
            product_id=it["id"],
            product_name=it["name"],
            unit_price=it["price"],
            quantity=it["quantity"],
        )
    cart_clear(session)
    return order
