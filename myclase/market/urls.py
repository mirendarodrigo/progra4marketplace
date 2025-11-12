
from django.contrib import admin
from django.urls import path, include
from .views import product_list, add_product
from . import views
from django.conf.urls.static import static


app_name = "market"
urlpatterns = [
    path("add/", add_product, name="add_product"),
    path('productos/', views.product_list, name='product_list'),
    path("search/", views.search_products, name="search_products"),
    path('<int:product_id>/modificar/', views.mod_product, name='mod_product'),
    path("api/seller/<int:pk>/", views.seller_api, name="seller_api"),
]