from django import forms
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')
        labels = {'first_name': 'Nombre', 'last_name': 'Apellido'}
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('telefono', 'direccion', 'localidad', 'datos_personales', 'foto')
        labels = {
            'telefono': 'Teléfono',
            'direccion': 'Dirección',
            'localidad': 'Localidad',
            'datos_personales': 'Datos personales',
            'foto': 'Foto de perfil',
        }
        widgets = {
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+54 9 11 ...'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Calle 123'}),
            'localidad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu ciudad'}),
            'datos_personales': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notas, bio, etc.'}),
            'foto': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
