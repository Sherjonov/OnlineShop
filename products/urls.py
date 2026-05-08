from django.urls import path

from . import views

app_name = "products"

urlpatterns = [
    path("create/", views.create_product, name="create"),
    path("<int:product_id>/update/", views.update_product, name="update"),
    path("<int:product_id>/delete/", views.delete_product, name="delete"),
]
