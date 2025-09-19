"""
Views Certificates - WIM Platform
Gestion des certificats
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.http import HttpResponse, JsonResponse
from django.contrib import messages

from apps.certificates.models import Certificate
from apps.enrollments.models import Enrollment
from apps.courses.models import Course


class CertificateGalleryView(LoginRequiredMixin, ListView):
    """Galerie des certificats de l'utilisateur"""
    model = Certificate
    template_name = 'certificates/gallery.html'
    context_object_name = 'certificates'

    def get_queryset(self):
        return Certificate.objects.filter(
            user=self.request.user
        ).select_related('course').order_by('-issued_at')


class CertificateDetailView(DetailView):
    """Détails d'un certificat"""
    model = Certificate
    template_name = 'certificates/detail.html'
    context_object_name = 'certificate'
    slug_field = 'certificate_id'
    slug_url_kwarg = 'certificate_id'


@login_required
def download_certificate(request, certificate_id):
    """Télécharger un certificat en PDF"""
    certificate = get_object_or_404(
        Certificate,
        certificate_id=certificate_id,
        user=request.user
    )

    # Générer le PDF (à implémenter avec reportlab ou weasyprint)
    # Pour l'instant, retourner une réponse simple

    messages.info(request, 'Fonction de téléchargement PDF à implémenter')
    return redirect('certificates:detail', certificate_id=certificate_id)


def verify_certificate(request, verification_code):
    """Vérifier l'authenticité d'un certificat"""
    try:
        certificate = Certificate.objects.get(verification_code=verification_code)

        return render(request, 'certificates/verify.html', {
            'certificate': certificate,
            'is_valid': True
        })
    except Certificate.DoesNotExist:
        return render(request, 'certificates/verify.html', {
            'is_valid': False
        })


@login_required
def generate_certificate(request, course_id):
    """Générer un certificat pour un cours complété"""
    course = get_object_or_404(Course, id=course_id)

    # Vérifier que l'utilisateur a complété le cours
    try:
        enrollment = Enrollment.objects.get(
            user=request.user,
            course=course,
            is_completed=True
        )
    except Enrollment.DoesNotExist:
        messages.error(request, "Vous devez compléter le cours pour obtenir un certificat")
        return redirect('courses:detail', slug=course.slug)

    # Vérifier si le certificat existe déjà
    certificate, created = Certificate.objects.get_or_create(
        user=request.user,
        course=course,
        defaults={'enrollment': enrollment}
    )

    if created:
        messages.success(request, 'Certificat généré avec succès!')
    else:
        messages.info(request, 'Certificat déjà généré pour ce cours')

    return redirect('certificates:detail', certificate_id=certificate.certificate_id)

