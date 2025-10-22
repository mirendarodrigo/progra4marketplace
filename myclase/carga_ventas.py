
import random
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from market.models import Product
from dashboard.models import Sale
from django.utils import timezone
import os
import django

# Establecer la configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myclase/myclase.settings')

# Inicializar Django
django.setup()

# Ahora ya podés importar modelos
from django.contrib.auth.models import User
from myapp.models import Venta  # <-- tu modelo

# Ejemplo de uso
usuarios = User.objects.all()
print(usuarios)


print("🚀 Iniciando generación de ventas de prueba...")

# Obtener todos los productos y usuarios
products = list(Product.objects.all())
users = list(User.objects.all())

if not products:
    print("❌ No hay productos en la base de datos. Por favor crea algunos productos primero.")
    exit()

if len(users) < 2:
    print("❌ Se necesitan al menos 2 usuarios (vendedor y comprador). Por favor crea más usuarios.")
    exit()

# Limpiar ventas existentes (opcional, comentar si no quieres borrar)
Sale.objects.all().delete()
print("🗑️  Ventas anteriores eliminadas")

# Estados de ventas
statuses = ['pending', 'completed', 'cancelled']
status_weights = [0.2, 0.7, 0.1]  # 70% completadas, 20% pendientes, 10% canceladas

# Generar ventas de los últimos 180 días
sales_created = 0
errors = 0

for product in products:
    seller = product.seller
    
    # Cada producto tendrá entre 5 y 20 ventas
    num_sales = random.randint(5, 20)
    
    for _ in range(num_sales):
        try:
            # Seleccionar un comprador diferente al vendedor
            potential_buyers = [u for u in users if u.id != seller.id]
            if not potential_buyers:
                print(f"⚠️  No hay compradores disponibles para el producto {product.title}")
                continue
                
            buyer = random.choice(potential_buyers)
            
            # Fecha aleatoria en los últimos 180 días
            days_ago = random.randint(0, 180)
            sale_date = timezone.now() - timedelta(days=days_ago)
            
            # Cantidad aleatoria (1-5 unidades)
            quantity = random.randint(1, 5)
            
            # Precio unitario (puede variar ligeramente del precio actual)
            price_variation = random.uniform(0.9, 1.1)
            unit_price = float(product.price) * price_variation
            
            # Estado de la venta
            status = random.choices(statuses, weights=status_weights)[0]
            
            # Crear la venta
            sale = Sale.objects.create(
                product=product,
                buyer=buyer,
                seller=seller,
                quantity=quantity,
                unit_price=round(unit_price, 2),
                status=status,
            )
            
            # Ajustar la fecha de creación
            sale.created_at = sale_date
            
            # Si está completada, agregar fecha de completado (1-3 días después)
            if status == 'completed':
                completion_days = random.randint(1, 3)
                sale.completed_at = sale_date + timedelta(days=completion_days)
            
            sale.save()
            sales_created += 1
            
        except Exception as e:
            errors += 1
            print(f"❌ Error al crear venta: {e}")

print(f"\n✅ Proceso completado!")
print(f"📊 Ventas creadas: {sales_created}")
print(f"❌ Errores: {errors}")
print(f"\n📈 Resumen por vendedor:")

for user in users:
    user_sales = Sale.objects.filter(seller=user)
    total_sales = user_sales.count()
    completed_sales = user_sales.filter(status='completed').count()
    total_revenue = sum(sale.total_price for sale in user_sales.filter(status='completed'))
    
    if total_sales > 0:
        print(f"  👤 {user.username}: {total_sales} ventas ({completed_sales} completadas) - ${total_revenue:.2f}")

print("\n🎉 ¡Listo! Ahora puedes ver el dashboard con datos.")