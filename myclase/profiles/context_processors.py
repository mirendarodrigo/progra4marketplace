import hashlib
import time
from django.templatetags.static import static

def _gravatar_url(email, size=128):
    if not email:
        return None
    email = email.strip().lower().encode("utf-8")
    hash_ = hashlib.md5(email).hexdigest()
    return f"https://www.gravatar.com/avatar/{hash_}?s={size}&d=identicon"

def _social_avatar_url(user):
    """
    Intenta obtener el avatar de django-allauth SocialAccount.
    No rompe si allauth no está instalado.
    """
    try:
        from allauth.socialaccount.models import SocialAccount
    except Exception:
        return None

    try:
        sa = SocialAccount.objects.filter(user=user).first()
        if not sa:
            return None

        data = sa.extra_data or {}
        for key in ("picture", "avatar_url", "avatar"):
            if data.get(key):
                return data[key]
    except Exception:
        return None
    return None


def avatar(request):
    """
    Retorna user_avatar_url con prioridades:
    1) Profile.foto
    2) Social avatar
    3) Gravatar
    4) ui-avatars

    Además, agrega un cache-buster (?v=...) cuando haya cambios.
    """
    url = None
    user = getattr(request, "user", None)

    if user and user.is_authenticated:
        # 1) Profile.foto
        profile = getattr(user, "profile", None)
        if profile and getattr(profile, "foto", None):
            try:
                url = profile.foto.url
            except Exception:
                url = None

        # 2) Social avatar
        if not url:
            url = _social_avatar_url(user)

        # 3) Gravatar
        if not url:
            url = _gravatar_url(getattr(user, "email", None))

        # 4) Fallback ui-avatars
        if not url:
            full_name = (user.get_full_name() or user.username or "User").replace(" ", "+")
            url = f"https://ui-avatars.com/api/?name={full_name}&size=256"

        # ---------- Cache-buster ----------
        # Si la vista guardó 'avatar_bust' en sesión tras actualizar la imagen, lo usamos.
        bust = None
        try:
            bust = request.session.pop("avatar_bust", None)
        except Exception:
            bust = None

        # Si no vino de sesión, intentamos derivarlo de la fecha de mod del archivo local (si existe).
        if not bust and profile and getattr(profile, "foto", None):
            try:
                storage = profile.foto.storage
                name = profile.foto.name
                ts = storage.get_modified_time(name)  # puede no estar implementado
                bust = str(int(ts.timestamp()))
            except Exception:
                bust = None

        if bust:
            sep = "&" if "?" in url else "?"
            url = f"{url}{sep}v={bust}"

    # Si el usuario no está autenticado, devolvemos un placeholder local
    if not url:
        url = static('img/avatar-default.png')

    return {"user_avatar_url": url}
