"""
Views Users - WIM Platform
Gestion des profils utilisateurs
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, UpdateView, TemplateView
from django.contrib import messages
from django.urls import reverse_lazy

from apps.users.models import User
from apps.enrollments.models import Enrollment
from apps.certificates.models import Certificate


class ProfileView(LoginRequiredMixin, DetailView):
    """Vue du profil utilisateur"""
    model = User
    template_name = 'users/profile.html'
    context_object_name = 'profile_user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object

        # Statistiques de l'utilisateur
        context['enrollments_count'] = Enrollment.objects.filter(
            user=user,
            is_active=True
        ).count()

        context['completed_courses'] = Enrollment.objects.filter(
            user=user,
            is_completed=True
        ).count()

        context['certificates_count'] = Certificate.objects.filter(
            user=user
        ).count()

        # Cours en cours
        context['active_enrollments'] = Enrollment.objects.filter(
            user=user,
            is_active=True,
            is_completed=False
        ).select_related('course')[:5]

        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    """Modifier le profil"""
    model = User
    template_name = 'users/edit_profile.html'
    fields = ['name', 'email', 'bio', 'avatar', 'phone', 'location']
    success_url = reverse_lazy('users:settings')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Profil mis à jour avec succès!')
        return super().form_valid(form)


class SettingsView(LoginRequiredMixin, TemplateView):
    """Paramètres du compte"""
    template_name = 'users/settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


@login_required
def update_profile(request):
    """Mettre à jour le profil (pour HTMX)"""
    if request.method == 'POST':
        user = request.user
        user.name = request.POST.get('name', user.name)
        user.bio = request.POST.get('bio', user.bio)
        user.phone = request.POST.get('phone', user.phone)
        user.location = request.POST.get('location', user.location)
        user.save()

        messages.success(request, 'Profil mis à jour!')

        if request.htmx:
            return render(request, 'users/partials/profile_updated.html', {
                'user': user
            })

        return redirect('users:settings')

    return redirect('users:settings')


@login_required
def change_password(request):
    """Changer le mot de passe"""
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        user = request.user

        if not user.check_password(old_password):
            messages.error(request, 'Mot de passe actuel incorrect')
        elif new_password != confirm_password:
            messages.error(request, 'Les nouveaux mots de passe ne correspondent pas')
        elif len(new_password) < 8:
            messages.error(request, 'Le mot de passe doit contenir au moins 8 caractères')
        else:
            user.set_password(new_password)
            user.save()
            messages.success(request, 'Mot de passe changé avec succès!')
            return redirect('authentication:login')

    return redirect('users:settings')