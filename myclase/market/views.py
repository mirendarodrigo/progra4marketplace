from django.shortcuts import render, redirect
from .models import Product
from .forms import ProductForm

def product_list(request):
    products = Product.objects.filter(active=True).order_by("-created_at")
    return render(request, "market/product_list.html", {"products": products})


def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user   # el usuario logueado será el vendedor
            product.save()
            return redirect("product_list")  # redirigimos a la lista de productos
    else:
        form = ProductForm()
    
    return render(request, "market/add_product.html", {"form": form})
