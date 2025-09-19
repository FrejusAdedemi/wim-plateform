"""
Views Progress - WIM Platform
Gestion de la progression
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, DetailView
from django.http import JsonResponse
from django.db.models import Avg, Count, Sum

from apps.progress.models import LessonProgress, UserStatistics
from apps.enrollments.models import Enrollment
from apps.courses.models import Course


class ProgressOverviewView(LoginRequiredMixin, TemplateView):
    """Vue d'ensemble de la progression"""
    template_name = 'progress/overview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Statistiques globales
        enrollments = Enrollment.objects.filter(user=user, is_active=True)

        context['total_courses'] = enrollments.count()
        context['completed_courses'] = enrollments.filter(is_completed=True).count()
        context['in_progress_courses'] = enrollments.filter(is_completed=False).count()

        # Progression moyenne
        avg_progress = enrollments.aggregate(
            avg=Avg('progress_percentage')
        )['avg'] or 0
        context['average_progress'] = round(avg_progress, 1)

        # Cours actifs avec progression
        context['active_enrollments'] = enrollments.select_related('course')

        return context


class CourseProgressView(LoginRequiredMixin, DetailView):
    """Progression détaillée pour un cours"""
    model = Course
    template_name = 'progress/course_progress.html'
    context_object_name = 'course'
    pk_url_kwarg = 'course_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        course = self.object

        # Récupérer l'inscription
        try:
            enrollment = Enrollment.objects.get(
                user=user,
                course=course,
                is_active=True
            )
            context['enrollment'] = enrollment

            # Progression par module
            modules = course.modules.filter(is_published=True).prefetch_related('lessons')

            module_progress = []
            for module in modules:
                total_lessons = module.lessons.count()
                completed_lessons = LessonProgress.objects.filter(
                    enrollment=enrollment,
                    lesson__module=module,
                    is_completed=True
                ).count()

                module_progress.append({
                    'module': module,
                    'total': total_lessons,
                    'completed': completed_lessons,
                    'percentage': (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
                })

            context['module_progress'] = module_progress

        except Enrollment.DoesNotExist:
            context['enrollment'] = None

        return context


@login_required
def user_statistics(request):
    """Statistiques utilisateur détaillées"""
    user = request.user

    # Créer ou récupérer les statistiques
    stats, created = UserStatistics.objects.get_or_create(user=user)

    # Calculer les statistiques actuelles
    enrollments = Enrollment.objects.filter(user=user, is_active=True)

    stats_data = {
        'total_courses': enrollments.count(),
        'completed_courses': enrollments.filter(is_completed=True).count(),
        'total_lessons': LessonProgress.objects.filter(
            enrollment__user=user
        ).count(),
        'completed_lessons': LessonProgress.objects.filter(
            enrollment__user=user,
            is_completed=True
        ).count(),
        'total_study_time': stats.total_study_time,
        'current_streak': stats.current_streak,
        'longest_streak': stats.longest_streak,
        'total_points': stats.total_points,
    }

    if request.htmx:
        return render(request, 'progress/partials/statistics.html', {
            'stats': stats_data
        })

    return JsonResponse(stats_data)


@login_required
def update_progress(request):
    """Mettre à jour la progression (HTMX)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

    lesson_id = request.POST.get('lesson_id')
    action = request.POST.get('action', 'complete')

    if not lesson_id:
        return JsonResponse({'error': 'ID de leçon manquant'}, status=400)

    try:
        # Récupérer la progression
        progress = LessonProgress.objects.get(
            id=lesson_id,
            enrollment__user=request.user
        )

        if action == 'complete':
            progress.mark_completed()
        elif action == 'incomplete':
            progress.is_completed = False
            progress.completed_at = None
            progress.save()

        # Recalculer la progression du cours
        enrollment = progress.enrollment
        enrollment.calculate_progress()

        return JsonResponse({
            'success': True,
            'progress': float(enrollment.progress_percentage)
        })

    except LessonProgress.DoesNotExist:
        return JsonResponse({'error': 'Progression non trouvée'}, status=404)

