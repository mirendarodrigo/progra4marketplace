from django.shortcuts import render

def scan(request):
    return render(request, 'scanner/scan.html')
from django.http import JsonResponse
from market.models import Product

def check_barcode(request):
    code = request.GET.get("barcode")
    if not code:
        return JsonResponse({"error": "No se envió código"}, status=400)

    product = Product.objects.filter(barcode=code).first()
    if product:
        return JsonResponse({
            "exists": True,
            "title": product.title,
            "marca": product.marca,
            "price": float(product.price),
            "image": product.image.url if product.image else None,
            "id": product.id
        })
    else:
        return JsonResponse({"exists": False})
