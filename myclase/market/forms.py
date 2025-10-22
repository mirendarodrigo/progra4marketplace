from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        
        fields = ["title", "description", "marca", "price", "active", "image","barcode","stock",]
        
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control"}),
            "marca": forms.TextInput(attrs={"class": "form-control"}),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
            "active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            # widget del campo image con id y aceptando solo imágenes
            "image": forms.ClearableFileInput(attrs={
                "id": "id_image",
                "accept": "image/*"
            }),
            "barcode": forms.TextInput(attrs={
               "class": "form-control",
               "placeholder": "Ej: 0000000000000"
           }),
            "stock": forms.NumberInput(attrs={
               "class": "form-control",
               "min": "0",
               "placeholder": "Cantidad disponible"
           }),
        }
