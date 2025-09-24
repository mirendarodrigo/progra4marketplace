from django.conf import settings
from django.db import models

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
    
    # Imagen del producto
    image = models.ImageField(
    upload_to="products/",  
    blank=True,
    null=True,
    default="products/placeholder.png"
)

    
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
