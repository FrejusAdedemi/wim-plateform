"""
Formulaires d'authentification - WIM Platform
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import re

User = get_user_model()


class RegisterForm(UserCreationForm):
    """Formulaire d'inscription"""

    name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Nom complet'
        })
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
            'placeholder': 'votre@email.com'
        })
    )

    password1 = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
            'placeholder': '••••••••'
        })
    )

    password2 = forms.CharField(
        label='Confirmer le mot de passe',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
            'placeholder': '••••••••'
        })
    )

    terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500'
        })
    )

    class Meta:
        model = User
        fields = ['name', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Cette adresse email est déjà utilisée.')
        return email

    def clean_password1(self):
        password = self.cleaned_data.get('password1')

        # Minimum 8 caractères
        if len(password) < 8:
            raise ValidationError('Le mot de passe doit contenir au moins 8 caractères.')

        # Au moins une majuscule
        if not re.search(r'[A-Z]', password):
            raise ValidationError('Le mot de passe doit contenir au moins une majuscule.')

        # Au moins un chiffre
        if not re.search(r'\d', password):
            raise ValidationError('Le mot de passe doit contenir au moins un chiffre.')

        # Au moins un caractère spécial
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError('Le mot de passe doit contenir au moins un caractère spécial.')

        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.name = self.cleaned_data['name']

        if commit:
            user.save()

        return user


class LoginForm(AuthenticationForm):
    """Formulaire de connexion"""

    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
            'placeholder': 'votre@email.com',
            'autofocus': True
        })
    )

    password = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
            'placeholder': '••••••••'
        })
    )

    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500'
        })
    )


class PasswordResetRequestForm(forms.Form):
    """Formulaire de demande de réinitialisation"""

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
            'placeholder': 'votre@email.com'
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise ValidationError('Aucun compte n\'est associé à cette adresse email.')
        return email