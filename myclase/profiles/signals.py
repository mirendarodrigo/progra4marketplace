import os
import hashlib
import requests
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.core.files.base import ContentFile
from django.conf import settings

from .models import Profile

def _best_external_avatar_url(user):
    # 1) Social
    try:
        from allauth.socialaccount.models import SocialAccount
        sa = SocialAccount.objects.filter(user=user).first()
        if sa and sa.extra_data:
            for key in ("picture", "avatar_url", "avatar"):
                if sa.extra_data.get(key):
                    return sa.extra_data[key]
    except Exception:
        pass

    # 2) Gravatar
    email = (user.email or "").strip().lower().encode("utf-8")
    if email:
        h = hashlib.md5(email).hexdigest()
        return f"https://www.gravatar.com/avatar/{h}?s=256&d=404"

    return None

def _download_bytes(url, timeout=10):
    try:
        r = requests.get(url, timeout=timeout)
        if r.status_code == 200 and r.content:
            return r.content
    except Exception:
        return None
    return None

@receiver(user_logged_in)
def copy_avatar_to_profile_on_login(sender, request, user, **kwargs):
    """
    Si el usuario inicia sesión y su Profile.foto está vacío:
    - intenta bajar el avatar del proveedor social o gravatar
    - lo guarda en Profile.foto para que quede en tu media/
    """
    profile, _ = Profile.objects.get_or_create(user=user)

    if profile.foto:  # ya tiene foto, no hacemos nada
        return

    url = _best_external_avatar_url(user)
    if not url:
        return

    data = _download_bytes(url)
    if not data:
        return

    # Nombre de archivo estable
    ext = ".jpg"
    # algunos proveedores devuelven webp/png; opcional: sniff del content-type
    filename = f"user_{user.id}_avatar{ext}"

    # Guardar en ImageField (usa el storage configurado)
    profile.foto.save(filename, ContentFile(data), save=True)
