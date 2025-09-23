# config/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

# ============================================================================
# PERSONNALISATION DU SITE ADMIN
# ============================================================================
admin.site.site_header = "WIM Platform - Administration"
admin.site.site_title = "WIM Admin"
admin.site.index_title = "Tableau de bord administrateur"

# ============================================================================
# URLS
# ============================================================================
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/dashboard/'), name='home'),
    path('auth/', include('apps.authentication.urls')),
    path('accounts/', include('allauth.urls')),
    path('users/', include('apps.users.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('courses/', include('apps.courses.urls')),
    path('enrollments/', include('apps.enrollments.urls')),
    path('progress/', include('apps.progress.urls')),
    path('certificates/', include('apps.certificates.urls')),
]

# Configuration pour servir les fichiers média et statiques en développement
if settings.DEBUG:
    # Servir les fichiers média (uploads d'utilisateurs)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Servir les fichiers statiques (CSS, JS, images du site)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Gestionnaires d'erreurs personnalisés
handler404 = 'apps.dashboard.views.custom_404'
handler500 = 'apps.dashboard.views.custom_500'
handler403 = 'apps.dashboard.views.custom_403'
handler400 = 'apps.dashboard.views.custom_400'