
from django.contrib import admin
from django.urls import path, include
from core.views import home
from django.conf import settings
from django.conf.urls.static import static  # 👈 asegurate de importar esto
from market import views
    
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('accounts/', include('allauth.urls')),
    path('productos/', include('market.urls')),
    path('market/', include('market.urls')),
    path('chat/', include('chat.urls')),
    path('scanner/', include('scanner.urls')),
    path("crear-preferencia/", views.crear_preferencia, name="crear_preferencia"),
    path('dashboard/', include('dashboard.urls')),
    path('perfil/', include('profiles.urls', namespace='profiles'))
    
    
]

# Archivos estáticos y media solo en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
