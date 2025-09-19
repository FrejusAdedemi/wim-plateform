# ============================================================================
# apps/certificates/urls.py
# ============================================================================

from django.urls import path
from . import views

app_name = 'certificates'

urlpatterns = [
    path('gallery/', views.CertificateGalleryView.as_view(), name='gallery'),
    path('<str:certificate_id>/', views.CertificateDetailView.as_view(), name='detail'),
    path('download/<str:certificate_id>/', views.download_certificate, name='download'),
    path('verify/<str:verification_code>/', views.verify_certificate, name='verify'),
    path('generate/<int:course_id>/', views.generate_certificate, name='generate'),
]