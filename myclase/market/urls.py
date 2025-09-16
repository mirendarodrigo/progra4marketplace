
from django.contrib import admin
from django.urls import path, include
from .views import product_list, add_product
from . import views

urlpatterns = [
    path("add/", add_product, name="add_product"),
    path("", product_list, name="product_list")
]
