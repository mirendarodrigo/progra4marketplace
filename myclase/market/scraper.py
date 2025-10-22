import requests
from market.models import Product

def scrape_coto(query="leche", limit=10):
    """
    Obtiene productos desde la API JSON interna de Coto Digital.
    Guarda los resultados en la base de datos.
    """
    print(f"Buscando productos en Coto: {query}")

    # Construimos la URL base
    url = f"https://www.cotodigital.com.ar/sitios/cdigi/busqueda?Ntt={query}&format=json"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0.0.0 Safari/537.36"
        )
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error al acceder a la API: {response.status_code}")
        return []

    data = response.json()
    productos_json = data.get("contents", [])
    productos = []

    for item in productos_json:
        try:
            product_data = item["mainContent"][0]["contents"][0]["records"][0]["attributes"]
            nombre = product_data["product.displayName"][0]
            precio = product_data["product.listPrice"][0]
            productos.append({"name": nombre, "price": precio})
        except Exception:
            continue

        if len(productos) >= limit:
            break

    print(f"Se encontraron {len(productos)} productos.")

    # Guardar en DB
    for p in productos:
        Product.objects.get_or_create(
            title=p["name"],
            defaults={
                "price": p["price"],
                "marca": "Coto",
                "description": f"Producto obtenido desde la búsqueda '{query}' en Coto Digital.",
            },
        )

    print(f"Se guardaron {len(productos)} productos en la base de datos.")
    return productos
