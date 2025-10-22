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
