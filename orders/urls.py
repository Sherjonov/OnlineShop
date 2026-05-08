from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    # Cart views
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/", views.cart_add, name="cart_add"),
    path("cart/set/", views.cart_set, name="cart_set"),
    path("cart/remove/", views.cart_remove, name="cart_remove"),
    path("cart/clear/", views.cart_clear, name="cart_clear"),
    path("cart/summary/", views.cart_summary, name="cart_summary"),
    
    # Checkout
    path("checkout/", views.checkout_view, name="checkout"),
    
    # API endpoints
    path("api/create/", views.api_create_order, name="api_create_order"),
    path("api/list/", views.api_list_orders, name="api_list_orders"),
    
    # Order detail
    path("<str:number>/", views.order_detail, name="detail"),
]
