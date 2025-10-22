from django.urls import path
from . import views
app_name = "scanner"
urlpatterns = [
    path('scan/', views.scan, name='scan'),
    path("check_barcode/", views.check_barcode, name="check_barcode"),
]
