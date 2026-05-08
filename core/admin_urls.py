from django.urls import path
from . import admin_views

app_name = "admin_panel"

urlpatterns = [
    path("", admin_views.dashboard, name="dashboard"),
    path("products/", admin_views.products_list, name="products"),
    path("products/new/", admin_views.product_form, name="product_create"),
    path("products/<int:product_id>/edit/", admin_views.product_form, name="product_edit"),
    path("products/<int:product_id>/toggle/", admin_views.product_toggle, name="product_toggle"),
    path("products/<int:product_id>/delete/", admin_views.product_delete, name="product_delete"),
    path("orders/", admin_views.orders_history, name="orders"),
    path("orders/<str:number>/status/", admin_views.order_status, name="order_status"),
    path("activity/", admin_views.login_activity, name="login_activity"),
    path("users/", admin_views.users_list, name="users"),
    path("users/<int:user_id>/toggle/", admin_views.user_toggle, name="user_toggle"),
]
