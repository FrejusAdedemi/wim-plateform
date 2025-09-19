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
    path('users/', include('apps.users.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('courses/', include('apps.courses.urls')),
    path('enrollments/', include('apps.enrollments.urls')),
    path('progress/', include('apps.progress.urls')),
    path('certificates/', include('apps.certificates.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

