from django.urls import path

from . import views

app_name = "products"

urlpatterns = [
    path("create/", views.create_product, name="create"),
    path("<int:product_id>/update/", views.update_product, name="update"),
    path("<int:product_id>/delete/", views.delete_product, name="delete"),
    path("api/delete/<int:product_id>/", views.delete_product, name="api_delete"),
    path("api/favorites/", views.list_favorites, name="favorites"),
    path("api/favorites/<int:product_id>/toggle/", views.toggle_favorite, name="toggle_favorite"),
]
