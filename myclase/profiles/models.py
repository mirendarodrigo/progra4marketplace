from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.core.validators import RegexValidator
from django.apps import AppConfig
import os

class ProfilesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "profiles"

    def ready(self):
        # importa señales a la carga
        import profiles.signals  # noqa

def profile_photo_path(instance, filename):
    # media/profiles/user_<id>/<filename>
    return f'profiles/user_{instance.user_id}/{filename}'

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    telefono = models.CharField(
        max_length=30, blank=True,
        validators=[RegexValidator(r'^[0-9+\-\s()\.]+$', 'Formato de teléfono inválido.')]
    )
    direccion = models.CharField(max_length=255, blank=True)
    localidad = models.CharField(max_length=120, blank=True)
    datos_personales = models.TextField(blank=True)
    foto = models.ImageField(upload_to=profile_photo_path, blank=True, null=True)

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"

    def __str__(self):
        return f'Perfil de {self.user.get_full_name() or self.user.username}'

# --- Señales ---
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_for_new_user(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

def _delete_file(path):
    if path and os.path.isfile(path):
        try:
            os.remove(path)
        except Exception:
            pass

@receiver(pre_save, sender=Profile)
def delete_old_photo_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = Profile.objects.get(pk=instance.pk)
    except Profile.DoesNotExist:
        return
    if old.foto and old.foto != instance.foto:
        _delete_file(old.foto.path)

@receiver(post_delete, sender=Profile)
def delete_photo_on_delete(sender, instance, **kwargs):
    if instance.foto:
        _delete_file(instance.foto.path)
