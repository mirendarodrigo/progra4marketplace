from django.shortcuts import render, redirect
from .models import Product
from .forms import ProductForm

def product_list(request):
    query = request.GET.get("q")
    products = Product.objects.filter(active=True).order_by("-created_at")

    if query:
        products = products.filter(title__icontains=query) | products.filter(description__icontains=query)

    return render(request, "market/product_list.html", {
        "products": products,
        "query": query,
    })

def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            return redirect("market:product_list")  # 👈 corregido con namespace
    else:
        form = ProductForm()
    
    return render(request, "market/add_product.html", {"form": form})
