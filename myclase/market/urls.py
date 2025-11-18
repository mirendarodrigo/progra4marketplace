from django.urls import path
from . import views

app_name = "market"

urlpatterns = [
    path("add/", views.add_product, name="add_product"),
    path("productos/", views.product_list, name="product_list"),
    path("search/", views.search_products, name="search_products"),
    path("<int:product_id>/modificar/", views.mod_product, name="mod_product"),
    path("api/seller/<int:pk>/", views.seller_api, name="seller_api"),

    path("mis-productos/", views.seller_products_dashboard, name="seller_products"),
    path("mis-productos/<int:product_id>/estado/", views.toggle_product_active, name="toggle_product_active"),
    path("mis-productos/<int:product_id>/eliminar/", views.delete_product, name="delete_product"),

    path("api/event/cart-add/", views.register_cart_add, name="register_cart_add"),
    path("api/event/cart-remove/", views.register_cart_remove, name="register_cart_remove"),
    path("api/event/purchase/", views.register_purchase, name="register_purchase"),

    path("api/notifications/seen/", views.mark_notifications_seen, name="mark_notifications_seen"),
    path('sesion-expirada/', views.session_expired, name='session_expired'),
]
