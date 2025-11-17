from django.contrib import admin
from django.urls import path, include
from core.views import home
from django.conf import settings
from django.conf.urls.static import static
from market import views as market_views   # 👈 renombrado por prolijidad

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),

    # Auth
    path('accounts/', include('allauth.urls')),

    # --- MARKET ---
    # Usamos UN solo include con namespace "market"
    # Las rutas reales quedan así:
    #   - /productos/          -> market:product_list
    #   - /add/                -> market:add_product
    #   - /search/             -> market:search_products
    #   - /<id>/modificar/     -> market:mod_product
    #   - /api/seller/<pk>/    -> market:seller_api
    path('', include(('market.urls', 'market'), namespace='market')),

    # Crear preferencia MP (fuera del include)
    path("crear-preferencia/", market_views.crear_preferencia, name="crear_preferencia"),

    # Chat
    path('chat/', include('chat.urls')),

    # Scanner
    path('scanner/', include('scanner.urls')),

    # Dashboard
    path('dashboard/', include('dashboard.urls')),

    # Perfiles
    path('perfil/', include('profiles.urls', namespace='profiles')),
    
]

# Archivos estáticos y media solo en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
