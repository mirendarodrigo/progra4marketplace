from django.contrib import admin
from .models import Sale

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'seller', 'buyer', 'quantity', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'seller']
    search_fields = ['product__title', 'buyer__username', 'seller__username']
    date_hierarchy = 'created_at'
    readonly_fields = ['total_price', 'created_at']