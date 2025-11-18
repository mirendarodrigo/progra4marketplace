from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL

class Product(models.Model):
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="products"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    marca = models.CharField(max_length=100, blank=True, default="Generico")
    price = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.TextField(max_length=50, blank=True, default= "Varios")
    
    image = models.ImageField(
        upload_to="products/",  
        blank=True,
        null=True,
        default="products/placeholder.png"
    )   
    
    barcode = models.CharField(
        max_length=13,  
        blank=True,
        default="0000000000000"
    )

    stock = models.IntegerField(
        blank=True,
        default=1
    )

    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    source = models.CharField(max_length=100, blank=True, default="Coto")  # supermercado
    query = models.CharField(max_length=100, blank=True, null=True)  # término de búsqueda

    def __str__(self):
        return self.title

class ProductNotification(models.Model):
    NOTIF_TYPES = (
        ("cart", "Agregado al carrito"),
        ("cart_remove", "Quitado del carrito"),  # 👈 NUEVO
        ("purchase", "Compra realizada"),
    )

    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="notifications")
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="product_notifications")
    buyer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="purchase_notifications")
    type = models.CharField(max_length=20, choices=NOTIF_TYPES)
    quantity = models.PositiveIntegerField(default=1)
    seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_type_display()} - {self.product.title} ({self.seller})"
    
class ProductEvent(models.Model):
    EVENT_TYPES = (
        ("cart_add", "Agregado al carrito"),
        ("cart_remove", "Quitado del carrito"),  # 👈 NUEVO
        ("purchase", "Compra"),
    )

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="product_events",
    )
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="events",
    )
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_event_type_display()} - {self.product} x{self.quantity}"
