# core/decorators.py
from functools import wraps
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse, NoReverseMatch

def user_profile_complete(user) -> bool:
    """
    Reglas de “perfil completo”.
    Ajustá acá lo que quieras exigir.
    """
    if not user.is_authenticated:
        return False

    # Datos del User que quiero exigir
    must_user = [
        user.first_name,
        user.last_name,
        user.email,
    ]

    profile = getattr(user, "profile", None)
    if not profile:
        return False

    # Datos del Profile que quiero exigir
    must_profile = [
        getattr(profile, "localidad", ""),
        getattr(profile, "telefono", ""),
        # Si querés exigir foto, descomentá:
        # getattr(profile, "foto", None),
    ]

    def _filled(x):
        if x is None:
            return False
        return str(x).strip() != ""

    return all(_filled(v) for v in (must_user + must_profile))


def require_complete_profile(view_func):
    """
    Decorador: exige login + perfil completo.
    Si no cumple, redirige a /perfil/ (o a 'profiles:access' si existe)
    y deja un mensaje.
    """
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        # Si no está logueado → a login con next
        if not request.user.is_authenticated:
            login_url = getattr(settings, "LOGIN_URL", "/accounts/login/")
            return redirect(f"{login_url}?next={request.path}")

        # Si no tiene el perfil completo → a perfil con aviso
        if not user_profile_complete(request.user):
            try:
                perfil_url = reverse("profiles:access")  # si tenés nombrada esa vista
            except NoReverseMatch:
                perfil_url = "/perfil/"  # fallback directo

            messages.warning(
                request,
                "Para publicar o modificar productos tenés que completar tu perfil."
            )
            # Volvés a donde estabas una vez completado
            return redirect(f"{perfil_url}?next={request.path}")

        # Si pasa las validaciones → continuar
        return view_func(request, *args, **kwargs)
    return _wrapped
