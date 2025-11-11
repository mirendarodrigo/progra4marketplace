import time
from PIL import Image, ImageOps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View

from .forms import UserForm, ProfileForm
from .models import Profile


def _disable_form(form):
    for f in form.fields.values():
        f.required = False
        if hasattr(f.widget, 'attrs'):
            f.widget.attrs['disabled'] = True
            f.widget.attrs['readonly'] = True


def _square_fit_image(path, size=600, fmt='JPEG', quality=90):
    """
    Abre la imagen en `path`, corrige orientación EXIF, la recorta/escala centrada
    a size×size y la guarda optimizada (reemplazando el archivo).
    """
    with Image.open(path) as im:
        im = ImageOps.exif_transpose(im).convert('RGB')
        im = ImageOps.fit(im, (size, size), method=Image.LANCZOS, centering=(0.5, 0.5))
        im.save(path, format=fmt, quality=quality, optimize=True)


class ProfileAccessView(LoginRequiredMixin, View):
    template_name = 'profiles/profile_form.html'

    def get(self, request):
        if request.user.is_staff or request.user.is_superuser:
            uform = UserForm()
            pform = ProfileForm()
            _disable_form(uform)
            _disable_form(pform)
            mode = 'staff_preview'
        else:
            profile, _ = Profile.objects.get_or_create(user=request.user)
            uform = UserForm(instance=request.user)
            pform = ProfileForm(instance=profile)
            mode = 'user_edit'

        return render(request, self.template_name, {
            'uform': uform,
            'pform': pform,
            'mode': mode,
        })

    def post(self, request):
        if request.user.is_staff or request.user.is_superuser:
            return redirect('profiles:edit')

        profile, _ = Profile.objects.get_or_create(user=request.user)
        uform = UserForm(request.POST, instance=request.user)
        pform = ProfileForm(request.POST, request.FILES, instance=profile)

        if uform.is_valid() and pform.is_valid():
            uform.save()
            # IMPORTANTE: quedarnos con la instancia guardada
            profile = pform.save()

            # Procesar la imagen subida (si hay)
            if getattr(profile, 'foto', None):
                try:
                    _square_fit_image(profile.foto.path, size=600)
                    # Forzar refresh de avatar en todas las vistas (cache-buster)
                    request.session['avatar_bust'] = str(int(time.time()))
                except Exception as e:
                    messages.warning(request, f"No pude procesar la foto: {e}")

            messages.success(request, "¡Datos actualizados correctamente!")
            return redirect('profiles:edit')

        # Si hay errores, render normal
        mode = 'user_edit'
        return render(request, self.template_name, {
            'uform': uform,
            'pform': pform,
            'mode': mode,
        })


@login_required
def delete_profile_photo(request):
    if request.user.is_staff or request.user.is_superuser:
        messages.info(request, 'No disponible para administradores.')
        return redirect('profiles:edit')

    profile, _ = Profile.objects.get_or_create(user=request.user)
    if getattr(profile, 'foto', None):
        try:
            profile.foto.delete(save=False)
        except Exception:
            pass
        profile.foto = None
        profile.save()
        messages.success(request, 'Foto de perfil eliminada.')
        request.session['avatar_bust'] = str(int(time.time()))
    else:
        messages.info(request, 'No había foto para eliminar.')

    return redirect('profiles:edit')
