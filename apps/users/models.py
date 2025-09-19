from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email obligatoire')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField('adresse email', unique=True)
    name = models.CharField('nom complet', max_length=150, blank=True)
    bio = models.TextField('biographie', max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone = models.CharField('téléphone', max_length=20, blank=True)
    location = models.CharField('localisation', max_length=100, blank=True)

    newsletter_subscribed = models.BooleanField('newsletter', default=True)
    email_notifications = models.BooleanField('notifications', default=True)

    is_instructor = models.BooleanField('instructeur', default=False)

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='custom_users',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='custom_users',
        related_query_name='custom_user',
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        verbose_name = 'utilisateur'
        verbose_name_plural = 'utilisateurs'
        ordering = ['-date_joined']

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.name if self.name else self.email


class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')

    preferred_language = models.CharField('langue', max_length=10, default='fr')
    learning_goal = models.CharField('objectif', max_length=255, blank=True)
    daily_study_time = models.IntegerField('temps quotidien (min)', default=30)

    reminder_enabled = models.BooleanField('rappels', default=True)
    reminder_time = models.TimeField('heure rappel', null=True, blank=True)

    theme = models.CharField(
        'thème',
        max_length=20,
        choices=[('light', 'Clair'), ('dark', 'Sombre')],
        default='light'
    )

    class Meta:
        verbose_name = 'préférence'
        verbose_name_plural = 'préférences'

    def __str__(self):
        return f"Préférences de {self.user.email}"