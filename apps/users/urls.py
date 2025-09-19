# ============================================================================
# apps/users/urls.py
# ============================================================================

from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('profile/<int:pk>/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.EditProfileView.as_view(), name='edit_profile'),
    path('settings/', views.SettingsView.as_view(), name='settings'),
]