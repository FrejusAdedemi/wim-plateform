"""
Views Enrollments - WIM Platform
Gestion des inscriptions
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.contrib import messages
from django.http import JsonResponse

from apps.enrollments.models import Enrollment, Review
from apps.courses.models import Course


class MyCoursesView(LoginRequiredMixin, ListView):
    """Mes cours - Liste des cours inscrits"""
    model = Enrollment
    template_name = 'enrollments/my_courses.html'
    context_object_name = 'enrollments'

    def get_queryset(self):
        return Enrollment.objects.filter(
            user=self.request.user,
            is_active=True
        ).select_related('course', 'course__category').order_by('-enrolled_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Filtrer par statut
        status = self.request.GET.get('status', 'all')

        if status == 'completed':
            context['enrollments'] = context['enrollments'].filter(is_completed=True)
        elif status == 'in_progress':
            context['enrollments'] = context['enrollments'].filter(is_completed=False)
        elif status == 'favorites':
            context['enrollments'] = context['enrollments'].filter(is_favorite=True)

        context['status_filter'] = status

        return context


class FavoritesView(LoginRequiredMixin, ListView):
    """Cours favoris"""
    model = Enrollment
    template_name = 'enrollments/favorites.html'
    context_object_name = 'enrollments'

    def get_queryset(self):
        return Enrollment.objects.filter(
            user=self.request.user,
            is_favorite=True,
            is_active=True
        ).select_related('course')


@login_required
def enroll_course(request, course_id):
    """S'inscrire à un cours"""
    course = get_object_or_404(Course, id=course_id, is_published=True)

    # Vérifier si déjà inscrit
    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user,
        course=course,
        defaults={'is_active': True}
    )

    if created:
        # Mettre à jour le compteur
        course.total_students += 1
        course.save()
        messages.success(request, f'Inscription réussie au cours "{course.title}"!')
    else:
        if not enrollment.is_active:
            enrollment.is_active = True
            enrollment.save()
            messages.success(request, 'Réinscription effectuée!')
        else:
            messages.info(request, 'Vous êtes déjà inscrit à ce cours')

    return redirect('courses:detail', slug=course.slug)


@login_required
def unenroll_course(request, enrollment_id):
    """Se désinscrire d'un cours"""
    enrollment = get_object_or_404(
        Enrollment,
        id=enrollment_id,
        user=request.user
    )

    course_title = enrollment.course.title

    # Désactiver l'inscription
    enrollment.is_active = False
    enrollment.save()

    # Mettre à jour le compteur
    course = enrollment.course
    course.total_students = max(0, course.total_students - 1)
    course.save()

    messages.success(request, f'Désinscription du cours "{course_title}" effectuée')

    return redirect('enrollments:my-courses')


@login_required
def submit_review(request, course_id):
    """Soumettre un avis sur un cours"""
    if request.method != 'POST':
        return redirect('courses:detail', course_id=course_id)

    course = get_object_or_404(Course, id=course_id)

    # Vérifier que l'utilisateur est inscrit
    try:
        enrollment = Enrollment.objects.get(
            user=request.user,
            course=course,
            is_active=True
        )
    except Enrollment.DoesNotExist:
        messages.error(request, 'Vous devez être inscrit pour laisser un avis')
        return redirect('courses:detail', slug=course.slug)

    # Récupérer les données
    rating = int(request.POST.get('rating', 5))
    comment = request.POST.get('comment', '').strip()

    # Créer ou mettre à jour l'avis
    review, created = Review.objects.update_or_create(
        user=request.user,
        course=course,
        defaults={
            'rating': rating,
            'comment': comment
        }
    )

    # Recalculer la note moyenne du cours
    course.update_rating()

    if created:
        messages.success(request, 'Merci pour votre avis!')
    else:
        messages.success(request, 'Votre avis a été mis à jour')

    return redirect('courses:detail', slug=course.slug)


@login_required
def toggle_favorite(request, enrollment_id):
    """Ajouter/retirer des favoris (HTMX)"""
    enrollment = get_object_or_404(
        Enrollment,
        id=enrollment_id,
        user=request.user
    )

    enrollment.is_favorite = not enrollment.is_favorite
    enrollment.save()

    if request.htmx:
        return render(request, 'enrollments/partials/favorite_button.html', {
            'enrollment': enrollment
        })

    return JsonResponse({
        'success': True,
        'is_favorite': enrollment.is_favorite
    })