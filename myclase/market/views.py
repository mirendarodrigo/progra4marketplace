from django.shortcuts import render, redirect
from .models import Product
from .forms import ProductForm
import mercadopago
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# @csrf_exempt
# def crear_preferencia(request):
#     if request.method == "POST":
#         try:
#             body = json.loads(request.body)

#             sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

#             preference_data = {
#                 "items": body.get("items", []),
#                 "back_urls": {
#                     "success": "http://localhost:8000/success/",
#                     "failure": "http://localhost:8000/failure/",
#                     "pending": "http://localhost:8000/pending/"
#                 },
#                 "auto_return": "approved"
#             }

#             preference_response = sdk.preference().create(preference_data)
#             preference = preference_response["response"]

#             return JsonResponse({
#                 "id": preference["id"],
#                 "init_point": preference["init_point"]
#             })

#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def crear_preferencia(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            print("Body recibido:", body)  # 🔹 log para ver qué llega
            
            sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

            preference_data = {
                "items": body.get("items", []),
                "back_urls": {
                    # Usa URLs de prueba que Mercado Pago acepte.
                    # El dominio debe ser público, no localhost.
                    "success": "https://www.google.com/success", 
                    "failure": "https://www.google.com/failure",
                    "pending": "https://www.google.com/pending"
                },
                "auto_return": "approved"
            }

            preference_response = sdk.preference().create(preference_data)
            print("Respuesta de MP:", preference_response)  # 🔹 log para ver la respuesta

            preference = preference_response.get("response")
            if not preference or "init_point" not in preference:
                print("Error: init_point no está en la respuesta")
                return JsonResponse({"error": "init_point no generado"}, status=500)

            return JsonResponse({
                "id": preference["id"],
                "init_point": preference["init_point"]
            })

        except Exception as e:
            print("Error crear_preferencia:", e)  # 🔹 log del error real
            return JsonResponse({"error": f"Error al crear la preferencia: {str(e)}"}, status=500)


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
