# market/middleware.py

from django.contrib.auth import logout
from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse
import time

class AutoLogoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Solo verificamos si el usuario está logueado
        if request.user.is_authenticated:
            
            # Obtenemos el tiempo actual
            current_time = time.time()
            
            # Obtenemos la última actividad de la sesión
            last_activity = request.session.get('last_activity')

            # Si existe un registro de actividad previa
            if last_activity:
                # Calculamos cuánto tiempo pasó
                wait_period = current_time - last_activity

                # Si el tiempo pasado es mayor al configurado en settings
                if wait_period > getattr(settings, 'AUTO_LOGOUT_DELAY', 300):
                    
                    # Cerramos la sesión
                    logout(request)
                    
                    # Limpiamos la data de la sesión para evitar conflictos
                    request.session.flush()
                    
                    # Redirigimos a la página de explicación
                    # Asegúrate de que 'session_expired' sea el name de tu url
                    return redirect('market:session_expired')

            # Si no ha expirado, actualizamos el tiempo de última actividad
            request.session['last_activity'] = current_time

        response = self.get_response(request)
        return response