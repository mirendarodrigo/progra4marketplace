
from django.contrib import admin
from django.urls import path, include
from .views import product_list

urlpatterns = [
   
    path("", product_list, name="porduct-list")
]
