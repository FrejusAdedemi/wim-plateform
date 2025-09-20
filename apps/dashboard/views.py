# apps/dashboard/views.py - Version corrigée

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
    login_url = '/auth/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Statistiques principales
        enrollments = Enrollment.objects.filter(user=user, is_active=True)

        # Calculer le temps d'étude total (en heures)
        total_seconds = sum([e.total_time_spent for e in enrollments]) if enrollments.exists() else 0
        total_hours = round(total_seconds / 3600, 1) if total_seconds > 0 else 0

        # Calculer la progression moyenne
        if enrollments.exists():
            avg_progress = enrollments.aggregate(Avg('progress_percentage'))['progress_percentage__avg'] or 0
            avg_progress = round(avg_progress, 1)
        else:
            avg_progress = 0

        # Compter les certificats
        certificates_count = Certificate.objects.filter(user=user, is_valid=True).count()

        # Compter les cours complétés
        completed_count = enrollments.filter(is_completed=True).count()

        context.update({
            'active_courses_count': enrollments.count(),
            'completed_courses_count': completed_count,
            'certificates_count': certificates_count,
            'total_study_hours': total_hours,
            'average_progress': avg_progress,

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
        try:
            enrollments = Enrollment.objects.filter(
                user=user,
                is_active=True
            ).select_related('course', 'course__category').order_by('-last_accessed')[:limit]
            return enrollments
        except Exception as e:
            print(f"Erreur get_recent_courses: {e}")
            return []

    def get_recommended_courses(self, user, limit=4):
        """Cours recommandés basés sur les catégories des cours suivis"""
        try:
            # Catégories des cours actuels
            enrolled_categories = Enrollment.objects.filter(
                user=user
            ).values_list('course__category', flat=True).distinct()

            if not enrolled_categories:
                # Si pas de cours, recommander les cours populaires
                return Course.objects.filter(
                    is_published=True
                ).order_by('-total_students')[:limit]

            # Cours recommandés dans les mêmes catégories
            return Course.objects.filter(
                category__in=enrolled_categories,
                is_published=True
            ).exclude(
                enrollments__user=user
            ).order_by('-rating', '-total_students')[:limit]
        except Exception as e:
            print(f"Erreur get_recommended_courses: {e}")
            return []

    def get_recent_activity(self, user, days=7):
        """Activité récente (leçons complétées)"""
        try:
            since_date = timezone.now() - timedelta(days=days)
            activities = LessonProgress.objects.filter(
                enrollment__user=user,
                is_completed=True,
                completed_at__gte=since_date
            ).select_related('lesson', 'lesson__module', 'lesson__module__course').order_by('-completed_at')[:10]
            return activities
        except Exception as e:
            print(f"Erreur get_recent_activity: {e}")
            return []

    def get_weekly_progress(self, user):
        """Progression sur 7 jours"""
        try:
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
        except Exception as e:
            print(f"Erreur get_weekly_progress: {e}")
            # Retourner des données vides en cas d'erreur
            return [{'date': timezone.now().date(), 'count': 0} for _ in range(7)]


@login_required
def search_courses(request):
    """Recherche de cours en temps réel avec HTMX"""
    query = request.GET.get('q', '').strip()

    try:
        if query:
            courses = Course.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query),
                is_published=True
            ).distinct()[:12]
        else:
            courses = Course.objects.filter(is_published=True).order_by('-created_at')[:12]

        # Vérifier si c'est une requête HTMX
        if hasattr(request, 'htmx') and request.htmx:
            return render(request, 'dashboard/partials/course_grid.html', {
                'courses': courses
            })

        return render(request, 'dashboard/index.html', {'courses': courses})
    except Exception as e:
        print(f"Erreur search_courses: {e}")
        return render(request, 'dashboard/partials/course_grid.html', {'courses': []})


@login_required
def filter_courses(request):
    """Filtrage dynamique des cours avec HTMX"""
    category = request.GET.get('category')
    difficulty = request.GET.get('difficulty')

    try:
        courses = Course.objects.filter(is_published=True)

        if category:
            courses = courses.filter(category__slug=category)

        if difficulty:
            courses = courses.filter(difficulty=difficulty)

        courses = courses.order_by('-rating')[:12]

        # Vérifier si c'est une requête HTMX
        if hasattr(request, 'htmx') and request.htmx:
            return render(request, 'dashboard/partials/course_grid.html', {
                'courses': courses
            })

        return redirect('dashboard:index')
    except Exception as e:
        print(f"Erreur filter_courses: {e}")
        return redirect('dashboard:index')


@login_required
def user_stats(request):
    """Statistiques détaillées de l'utilisateur"""
    user = request.user

    try:
        # Récupérer ou créer les statistiques
        stats, created = UserStatistics.objects.get_or_create(
            user=user,
            defaults={
                'total_courses_enrolled': 0,
                'total_courses_completed': 0,
                'total_lessons_completed': 0,
                'total_study_time': 0,
            }
        )

        context = {
            'stats': stats,
            'enrollments': Enrollment.objects.filter(user=user, is_active=True),
        }

        return render(request, 'dashboard/stats.html', context)
    except Exception as e:
        print(f"Erreur user_stats: {e}")
        context = {
            'stats': None,
            'enrollments': [],
        }
        return render(request, 'dashboard/stats.html', context)


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
