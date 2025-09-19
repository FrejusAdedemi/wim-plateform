"""
Views Dashboard - WIM Platform
Tableau de bord principal avec statistiques
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from datetime import timedelta

from apps.enrollments.models import Enrollment
from apps.courses.models import Course, Category
from apps.progress.models import LessonProgress, UserStatistics
from apps.certificates.models import Certificate


class DashboardView(LoginRequiredMixin, TemplateView):
    """Vue principale du dashboard"""
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Statistiques principales
        enrollments = Enrollment.objects.filter(user=user, is_active=True)

        context.update({
            'active_courses_count': enrollments.count(),
            'completed_courses_count': enrollments.filter(is_completed=True).count(),
            'certificates_count': Certificate.objects.filter(user=user).count(),
            'total_study_hours': user.total_study_time,
            'average_progress': user.average_progress,

            # Cours récents
            'recent_courses': self.get_recent_courses(user),

            # Cours recommandés
            'recommended_courses': self.get_recommended_courses(user),

            # Activité récente
            'recent_activity': self.get_recent_activity(user),

            # Progression hebdomadaire
            'weekly_progress': self.get_weekly_progress(user),
        })

        return context

    def get_recent_courses(self, user, limit=6):
        """Récupérer les cours récemment consultés"""
        return Enrollment.objects.filter(
            user=user,
            is_active=True
        ).select_related('course', 'course__category').order_by('-last_accessed')[:limit]

    def get_recommended_courses(self, user, limit=4):
        """Cours recommandés basés sur les catégories des cours suivis"""
        # Catégories des cours actuels
        enrolled_categories = Enrollment.objects.filter(
            user=user
        ).values_list('course__category', flat=True)

        # Cours recommandés dans les mêmes catégories
        return Course.objects.filter(
            category__in=enrolled_categories,
            is_published=True
        ).exclude(
            enrollments__user=user
        ).order_by('-rating', '-total_students')[:limit]

    def get_recent_activity(self, user, days=7):
        """Activité récente (leçons complétées)"""
        since_date = timezone.now() - timedelta(days=days)
        return LessonProgress.objects.filter(
            enrollment__user=user,
            is_completed=True,
            completed_at__gte=since_date
        ).select_related('lesson', 'lesson__module').order_by('-completed_at')[:10]

    def get_weekly_progress(self, user):
        """Progression sur 7 jours"""
        progress_data = []
        for i in range(7):
            date = timezone.now().date() - timedelta(days=6 - i)
            completed = LessonProgress.objects.filter(
                enrollment__user=user,
                is_completed=True,
                completed_at__date=date
            ).count()
            progress_data.append({
                'date': date,
                'count': completed
            })
        return progress_data


@login_required
def search_courses(request):
    """Recherche de cours en temps réel avec HTMX"""
    query = request.GET.get('q', '').strip()

    if query:
        courses = Course.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__name__icontains=query),
            is_published=True
        ).distinct()[:12]
    else:
        courses = Course.objects.filter(is_published=True)[:12]

    if request.htmx:
        return render(request, 'dashboard/partials/course_grid.html', {
            'courses': courses
        })

    return render(request, 'dashboard/index.html', {'courses': courses})


@login_required
def filter_courses(request):
    """Filtrage dynamique des cours avec HTMX"""
    category = request.GET.get('category')
    difficulty = request.GET.get('difficulty')

    courses = Course.objects.filter(is_published=True)

    if category:
        courses = courses.filter(category__slug=category)

    if difficulty:
        courses = courses.filter(difficulty=difficulty)

    courses = courses.order_by('-rating')[:12]

    if request.htmx:
        return render(request, 'dashboard/partials/course_grid.html', {
            'courses': courses
        })

    return redirect('dashboard:index')


# Gestionnaires d'erreurs personnalisés
def custom_404(request, exception):
    """Page 404 personnalisée"""
    return render(request, 'errors/404.html', status=404)


def custom_500(request):
    """Page 500 personnalisée"""
    return render(request, 'errors/500.html', status=500)


def custom_403(request, exception):
    """Page 403 personnalisée"""
    return render(request, 'errors/403.html', status=403)


def custom_400(request, exception):
    """Page 400 personnalisée"""
    return render(request, 'errors/400.html', status=400)