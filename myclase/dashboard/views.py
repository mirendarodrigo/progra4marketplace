from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncDate, TruncMonth
from datetime import datetime, timedelta
from .models import Sale
from market.models import Product

@login_required
def dashboard_view(request):
    # Obtener ventas del usuario actual
    user_sales = Sale.objects.filter(seller=request.user)
    
    # Estadísticas generales
    total_sales = user_sales.filter(status='completed').aggregate(
        total=Sum('total_price'),
        count=Count('id')
    )
    
   
    pending_sales = user_sales.filter(status='pending').count()
    
 
    user_products = Product.objects.filter(seller=request.user)
    total_products = user_products.count()
    active_products = user_products.filter(active=True).count()
    

    seven_days_ago = datetime.now() - timedelta(days=7)
    recent_sales = user_sales.filter(
        status='completed',
        created_at__gte=seven_days_ago
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        total=Sum('total_price'),
        count=Count('id')
    ).order_by('date')
    
  
    six_months_ago = datetime.now() - timedelta(days=180)
    monthly_sales = user_sales.filter(
        status='completed',
        created_at__gte=six_months_ago
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        total=Sum('total_price'),
        count=Count('id')
    ).order_by('month')
    
   
    top_products = user_sales.filter(
        status='completed'
    ).values(
        'product__title',
        'product__id'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum('total_price')
    ).order_by('-total_quantity')[:5]
    
   
    recent_transactions = user_sales.select_related(
        'product', 'buyer'
    ).order_by('-created_at')[:10]
    
    context = {
        'total_revenue': total_sales['total'] or 0,
        'total_sales_count': total_sales['count'] or 0,
        'pending_sales': pending_sales,
        'total_products': total_products,
        'active_products': active_products,
        'recent_sales': recent_sales,
        'monthly_sales': monthly_sales,
        'top_products': top_products,
        'recent_transactions': recent_transactions,
    }
    
    return render(request, 'dashboard/dashboard.html', context)