from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views import View
from django.shortcuts import render, redirect
from .forms import UserForm, ProfileForm
from .models import Profile

def _disable_form(form):
    for f in form.fields.values():
        f.required = False
        if hasattr(f.widget, 'attrs'):
            f.widget.attrs['disabled'] = True
            f.widget.attrs['readonly'] = True

class ProfileAccessView(LoginRequiredMixin, View):
    template_name = 'profiles/profile_form.html'

    def get(self, request):
        if request.user.is_staff or request.user.is_superuser:
            uform = UserForm()
            pform = ProfileForm()
            _disable_form(uform)
            _disable_form(pform)
            return render(request, self.template_name, {
                'uform': uform, 'pform': pform, 'mode': 'staff_preview'
            })

        profile, _ = Profile.objects.get_or_create(user=request.user)
        uform = UserForm(instance=request.user)
        pform = ProfileForm(instance=profile)
        return render(request, self.template_name, {
            'uform': uform, 'pform': pform, 'mode': 'user_edit'
        })

    def post(self, request):
        if request.user.is_staff or request.user.is_superuser:
            messages.info(request, 'Vista sólo lectura para administradores.')
            return redirect('profiles:edit')

        profile, _ = Profile.objects.get_or_create(user=request.user)
        uform = UserForm(request.POST, instance=request.user)
        pform = ProfileForm(request.POST, request.FILES, instance=profile)
        if uform.is_valid() and pform.is_valid():
            uform.save()
            pform.save()
            messages.success(request, 'Perfil actualizado con éxito.')
            return redirect('profiles:edit')

        messages.error(request, 'Revisá los errores del formulario.')
        return render(request, self.template_name, {
            'uform': uform, 'pform': pform, 'mode': 'user_edit'
        })

@login_required
def delete_profile_photo(request):
    if request.user.is_staff or request.user.is_superuser:
        messages.info(request, 'No disponible para administradores.')
        return redirect('profiles:edit')

    profile, _ = Profile.objects.get_or_create(user=request.user)
    if profile.foto:
        profile.foto.delete(save=False)
        profile.foto = None
        profile.save()
        messages.success(request, 'Foto de perfil eliminada.')
    else:
        messages.info(request, 'No había foto para eliminar.')
    return redirect('profiles:edit')
