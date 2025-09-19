# ============================================================================
# apps/authentication/views.py - COMPLET
# ============================================================================

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.users.models import User


def login_view(request):
    """Vue de connexion"""
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember = request.POST.get('remember')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)

            # Gérer "Se souvenir de moi"
            if not remember:
                request.session.set_expiry(0)

            messages.success(request, f'Bienvenue {user.get_full_name()}!')

            # Rediriger vers la page demandée ou dashboard
            next_url = request.GET.get('next', 'dashboard:index')
            return redirect(next_url)
        else:
            messages.error(request, 'Email ou mot de passe incorrect')

    return render(request, 'authentication/login.html')


def register_view(request):
    """Vue d'inscription"""
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        # Validation
        if password != password2:
            messages.error(request, 'Les mots de passe ne correspondent pas')
            return render(request, 'authentication/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Cet email est déjà utilisé')
            return render(request, 'authentication/register.html')

        # Créer l'utilisateur
        user = User.objects.create_user(
            email=email,
            password=password,
            name=name
        )

        # Connecter automatiquement
        login(request, user)
        messages.success(request, 'Compte créé avec succès!')

        return redirect('dashboard:index')

    return render(request, 'authentication/register.html')


@login_required
def logout_view(request):
    """Vue de déconnexion"""
    logout(request)
    messages.info(request, 'Vous êtes déconnecté')
    return redirect('authentication:login')