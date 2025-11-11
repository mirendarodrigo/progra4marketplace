from django.urls import path
from .views import ProfileAccessView, delete_profile_photo

app_name = 'profiles'

urlpatterns = [
    path('', ProfileAccessView.as_view(), name='edit'),  # /perfil/ abre la pantalla con campos
    path('borrar-foto/', delete_profile_photo, name='delete_photo'),
]
