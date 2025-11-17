from django.urls import path
from . import views

app_name = "market"

urlpatterns = [
    # Lista de productos
    path("productos/", views.product_list, name="product_list"),

    # Alta de producto
    path("add/", views.add_product, name="add_product"),

    # Modificación de producto
    path("<int:product_id>/modificar/", views.mod_product, name="mod_product"),

    # Búsqueda externa / scraper
    path("search/", views.search_products, name="search_products"),

    # API para datos del vendedor
    path("api/seller/<int:pk>/", views.seller_api, name="seller_api"),
]
