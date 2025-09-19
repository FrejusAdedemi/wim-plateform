from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserPreference


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'name', 'is_staff', 'is_instructor', 'date_joined']
    list_filter = ['is_staff', 'is_instructor', 'is_active', 'date_joined']
    search_fields = ['email', 'name']
    ordering = ['-date_joined']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations personnelles', {'fields': ('name', 'bio', 'avatar', 'phone', 'location')}),
        ('Permissions',
         {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_instructor', 'groups', 'user_permissions')}),
        ('Préférences', {'fields': ('newsletter_subscribed', 'email_notifications')}),
        ('Dates importantes', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2'),
        }),
    )


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'preferred_language', 'theme', 'reminder_enabled']
    list_filter = ['theme', 'reminder_enabled']
    search_fields = ['user__email']