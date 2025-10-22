from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from .forms import ProductForm
import mercadopago
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .scraper import scrape_coto
import mercadopago
import json




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
    # Si viene un código por GET, lo tomamos
    barcode = request.GET.get("barcode", "")

    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user

            # Si el campo barcode viene vacío en el form pero había uno en la URL, lo usamos
            if not product.barcode and barcode:
                product.barcode = barcode

            product.save()
            return redirect("market:product_list")
    else:
        # Precargamos el código en el formulario si vino por GET
        form = ProductForm(initial={"barcode": barcode})

    return render(request, "market/add_product.html", {"form": form})

def mod_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('market:product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'market/mod_product.html', {'form': form})

def search_products(request):
    query = request.GET.get("q", "")
    if not query:
        return JsonResponse({"error": "Falta parámetro 'q'"}, status=400)

    productos = Product.objects.filter(query=query).order_by('-created_at')[:10]

    if not productos:
        scraped = scrape_coto(query)
        User = get_user_model()
        seller, _ = User.objects.get_or_create(username="CotoBot")
        for p in scraped:
            Product.objects.create(
                seller=seller,
                title=p['title'],
                marca=p['marca'],
                price=p['price'],
                stock=10,
                query=query,
                source="Coto"
            )
        productos = Product.objects.filter(query=query)

    data = [
        {
            "title": p.title,
            "marca": p.marca,
            "price": float(p.price),
            "source": p.source,
        }
        for p in productos
    ]
    return JsonResponse(data, safe=False)



