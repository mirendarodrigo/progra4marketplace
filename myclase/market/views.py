from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, ProductEvent, ProductNotification   # 👈 agregado ProductEvent
from .forms import ProductForm
import mercadopago
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .scraper import scrape_coto
import mercadopago
import json
from django.db.models import Q
from profiles.models import Profile
from django.contrib.auth import get_user_model
from core.decorators import require_complete_profile
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST


def session_expired(request):
    return render(request, 'market/session_expired.html')

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
    sort_by = request.GET.get("sort", "recent")

    # 1. Empezar con el filtro base (SIN ordenar)
    products = Product.objects.filter(active=True)

    # 2. Aplicar el filtro de BÚSQUEDA (si existe)
    if query:
        products = products.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    # 3. Definir las opciones de ordenamiento
    sort_options = {
        'recent': '-created_at',
        'oldest': 'created_at',
        'price_asc': 'price',
        'price_desc': '-price',
        'alpha': 'title',
    }

    # 4. Obtener el campo de ordenamiento
    order_field = sort_options.get(sort_by, '-created_at')

    # 5. Aplicar el ORDENAMIENTO al FINAL de todo
    products = products.order_by(order_field)

    # 6. Enviar al template
    return render(request, "market/product_list.html", {
        "products": products,
        "query": query,          # 'query' para rellenar el input
        "current_sort": sort_by, # 'current_sort' para seleccionar la opción del menú
    })


# =====================================================================================
#  PANEL "MIS PRODUCTOS" DEL VENDEDOR + NOTIFICACIONES
# =====================================================================================

@login_required
@require_complete_profile
def seller_products_dashboard(request):
    """
    Lista de productos del vendedor + notificaciones separadas por tipo.
    Además calcula contadores de NOTIFICACIONES NO LEÍDAS por tipo.
    """
    my_products = Product.objects.filter(seller=request.user).order_by('-created_at')

    # Últimas notificaciones (las que se muestran en las listas)
    notifications_qs = ProductNotification.objects.filter(
        seller=request.user
    ).select_related('product', 'buyer').order_by('-created_at')[:50]

    # Separar por tipo (lo que se muestra en cada acordeón)
    notifications_cart = [n for n in notifications_qs if n.type == "cart"]
    notifications_cart_remove = [n for n in notifications_qs if n.type == "cart_remove"]
    notifications_purchase = [n for n in notifications_qs if n.type == "purchase"]

    # Contadores de NO LEÍDAS (para los badges)
    notifications_cart_unseen_count = ProductNotification.objects.filter(
        seller=request.user, seen=False, type="cart"
    ).count()
    notifications_cart_remove_unseen_count = ProductNotification.objects.filter(
        seller=request.user, seen=False, type="cart_remove"
    ).count()
    notifications_purchase_unseen_count = ProductNotification.objects.filter(
        seller=request.user, seen=False, type="purchase"
    ).count()

    user_products_unread_count = (
        notifications_cart_unseen_count
        + notifications_cart_remove_unseen_count
        + notifications_purchase_unseen_count
    )

    return render(request, "market/seller_products.html", {
        "my_products": my_products,

        "notifications_cart": notifications_cart,
        "notifications_cart_remove": notifications_cart_remove,
        "notifications_purchase": notifications_purchase,

        "notifications_cart_unseen_count": notifications_cart_unseen_count,
        "notifications_cart_remove_unseen_count": notifications_cart_remove_unseen_count,
        "notifications_purchase_unseen_count": notifications_purchase_unseen_count,
        "user_products_unread_count": user_products_unread_count,
    })


@csrf_exempt
@require_POST
def register_cart_add(request):
    """
    Agregado al carrito.
    Espera JSON: { "product_id": ..., "quantity": ... }
    """
    try:
        body = json.loads(request.body.decode('utf-8'))
        product_id = body.get("product_id")
        quantity = int(body.get("quantity", 1))

        product = get_object_or_404(Product, pk=product_id)

        # Evento histórico
        ProductEvent.objects.create(
            seller=product.seller,
            product=product,
            event_type="cart_add",
            quantity=quantity,
        )

        # Notificación
        ProductNotification.objects.create(
            product=product,
            seller=product.seller,
            buyer=request.user if request.user.is_authenticated else None,
            type="cart",
            quantity=quantity,
        )

        return JsonResponse({"ok": True})
    except Exception as e:
        print("Error en register_cart_add:", e)
        return JsonResponse({"ok": False, "error": str(e)}, status=400)


@csrf_exempt
@require_POST
def register_purchase(request):
    """
    Compra realizada.
    Espera JSON: { "items": [ { "product_id": ..., "quantity": ... }, ... ] }
    """
    try:
        body = json.loads(request.body.decode('utf-8'))
        items = body.get("items", [])

        buyer = request.user if request.user.is_authenticated else None

        for item in items:
            pid = item.get("product_id")
            qty = int(item.get("quantity", 1))
            if not pid:
                continue

            product = get_object_or_404(Product, pk=pid)

            # Evento
            ProductEvent.objects.create(
                seller=product.seller,
                product=product,
                event_type="purchase",
                quantity=qty,
            )

            # Notificación
            ProductNotification.objects.create(
                product=product,
                seller=product.seller,
                buyer=buyer,
                type="purchase",
                quantity=qty,
            )

            # Stock
            if product.stock is not None:
                product.stock = max(product.stock - qty, 0)
                product.save(update_fields=["stock"])

        return JsonResponse({"ok": True})
    except Exception as e:
        print("Error en register_purchase:", e)
        return JsonResponse({"ok": False, "error": str(e)}, status=400)


# =====================================================================================
#   ALTA / MODIFICACIÓN DE PRODUCTOS (con perfil completo requerido)
# =====================================================================================

@login_required
@require_complete_profile
def add_product(request):
    print("➡️ ENTRÓ a add_product, method:", request.method)
    barcode = request.GET.get("barcode", "")

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)  # <-- asegurate de incluir FILES si subís imagen
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            if not product.barcode and barcode:
                product.barcode = barcode
            product.save()
            print("✅ Producto creado:", product.id)
            return redirect("market:product_list")
        else:
            print("❌ Form inválido:", form.errors)
    else:
        form = ProductForm(initial={"barcode": barcode})

    return render(request, "market/add_product.html", {"form": form})


@login_required
@require_complete_profile
def mod_product(request, product_id):
    print("➡️ ENTRÓ a mod_product:", product_id)
    product = get_object_or_404(Product, pk=product_id)

    # (Opcional) solo el dueño puede editar:
    # if product.seller_id != request.user.id:
    #     messages.warning(request, "No tenés permiso para editar este producto.")
    #     return redirect("market:product_list")

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            print("✅ Producto modificado:", product.id)
            return redirect('market:product_list')
        else:
            print("❌ Form inválido:", form.errors)
    else:
        form = ProductForm(instance=product)
    return render(request, 'market/mod_product.html', {'form': form})

@login_required
@require_complete_profile
@require_POST
def delete_product(request, product_id):
    """
    Elimina DEFINITIVAMENTE un producto del vendedor actual.
    """
    product = get_object_or_404(Product, pk=product_id, seller=request.user)
    product.delete()
    return redirect("market:seller_products")

@login_required
@require_complete_profile
@require_POST
def toggle_product_active(request, product_id):
    """
    Activa o desactiva (da de baja) un producto del vendedor actual.
    Usa el campo 'active' del modelo Product.
    """
    product = get_object_or_404(Product, pk=product_id, seller=request.user)

    action = request.POST.get("action", "deactivate")
    if action == "deactivate":
        product.active = False
    elif action == "activate":
        product.active = True

    product.save(update_fields=["active"])

    # Volvemos al panel de mis productos
    return redirect("market:seller_products")

@csrf_exempt
@require_POST
def register_cart_remove(request):
    """
    Quitado del carrito.
    Espera JSON: { "product_id": ..., "quantity": ... }
    """
    try:
        body = json.loads(request.body.decode('utf-8'))
        product_id = body.get("product_id")
        quantity = int(body.get("quantity", 1))

        product = get_object_or_404(Product, pk=product_id)

        # Evento histórico
        ProductEvent.objects.create(
            seller=product.seller,
            product=product,
            event_type="cart_remove",
            quantity=quantity,
        )

        # Notificación
        ProductNotification.objects.create(
            product=product,
            seller=product.seller,
            buyer=request.user if request.user.is_authenticated else None,
            type="cart_remove",   # 👈 IMPORTANTE
            quantity=quantity,
        )

        return JsonResponse({"ok": True})
    except Exception as e:
        print("Error en register_cart_remove:", e)
        return JsonResponse({"ok": False, "error": str(e)}, status=400)
    
# =====================================================================================
#   BÚSQUEDA EXTERNA / API VENDEDOR
# =====================================================================================

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


def seller_api(request, pk):
    """
    Retorna JSON con datos del vendedor y su perfil:
    { id, name, email, localidad, telefono, products_count }
    """
    User = get_user_model()
    user = get_object_or_404(User, pk=pk)

    # Obtener Profile si existe
    profile = Profile.objects.filter(user_id=pk).first()

    # Contar publicaciones
    qs = Product.objects.filter(seller_id=pk)
    if hasattr(Product, "active"):
        qs = qs.filter(active=True)

    data = {
        "id": user.id,
        "name": user.get_full_name() or user.username,
        "email": user.email or "",
        "localidad": getattr(profile, "localidad", "") if profile else "",
        "telefono": getattr(profile, "telefono", "") if profile else "",
        "products_count": qs.count(),
    }
    return JsonResponse(data)

@csrf_exempt
@login_required
@require_POST
def mark_notifications_seen(request):
    """
    Marca notificaciones como 'seen=True' para el vendedor actual.
    JSON esperado: { "type": "cart" | "cart_remove" | "purchase" | null }
    Si no se envía type o es inválido, marca TODAS como vistas.
    """
    try:
        body = json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        body = {}

    notif_type = body.get("type")

    qs = ProductNotification.objects.filter(seller=request.user, seen=False)
    if notif_type in ["cart", "cart_remove", "purchase"]:
        qs = qs.filter(type=notif_type)

    updated = qs.update(seen=True)

    # Recalcular contadores NO LEÍDOS por tipo
    counts = {
        "cart": ProductNotification.objects.filter(
            seller=request.user, seen=False, type="cart"
        ).count(),
        "cart_remove": ProductNotification.objects.filter(
            seller=request.user, seen=False, type="cart_remove"
        ).count(),
        "purchase": ProductNotification.objects.filter(
            seller=request.user, seen=False, type="purchase"
        ).count(),
    }
    counts["total"] = counts["cart"] + counts["cart_remove"] + counts["purchase"]

    return JsonResponse({
        "ok": True,
        "updated": updated,
        "counts": counts,
    })
