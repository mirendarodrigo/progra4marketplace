# Contenido FINAL y corregido para core/views.py

from django.shortcuts import render
from market.models import Product 
# Asegúrate de que la importación de Product sea correcta

def home(request):
    # OJO: Se cambió [:10] por [:8] para mostrar solo 8 productos
    products = Product.objects.filter(active=True).order_by('-created_at')[:8]
    
    context = {
        'products': products
    }
    
    return render(request, "home.html", context)