"""
Views Courses - WIM Platform
Gestion de l'affichage des cours, modules et leçons
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib import messages

from .models import Course, Module, Lesson, Category
from apps.enrollments.models import Enrollment, Review
from apps.progress.models import LessonProgress


class CourseListView(ListView):
    """Liste paginée des cours"""
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    paginate_by = 12

    def get_queryset(self):
        queryset = Course.objects.filter(is_published=True).select_related(
            'category', 'instructor'
        ).prefetch_related('tags')

        # Recherche
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(tags__name__icontains=query)
            ).distinct()

        # Filtrage par catégorie
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)

        # Filtrage par difficulté
        difficulty = self.request.GET.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)

        # Tri
        sort = self.request.GET.get('sort', '-created_at')
        allowed_sorts = ['-created_at', 'title', '-rating', 'price', '-total_students']
        if sort in allowed_sorts:
            queryset = queryset.order_by(sort)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['difficulty_choices'] = Course.DIFFICULTY_CHOICES
        return context


class CourseDetailView(DetailView):
    """Détails d'un cours"""
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        user = self.request.user

        # Modules et leçons
        context['modules'] = course.modules.filter(
            is_published=True
        ).prefetch_related('lessons').order_by('order')

        # Vérifier si l'utilisateur est inscrit
        is_enrolled = False
        enrollment = None

        if user.is_authenticated:
            try:
                enrollment = Enrollment.objects.get(
                    user=user,
                    course=course,
                    is_active=True
                )
                is_enrolled = True
                context['enrollment'] = enrollment
            except Enrollment.DoesNotExist:
                pass

        context['is_enrolled'] = is_enrolled

        # Avis du cours
        reviews = Review.objects.filter(
            course=course
        ).select_related('user').order_by('-created_at')[:10]

        context['reviews'] = reviews
        context['reviews_count'] = course.total_reviews

        # Statistiques des avis
        review_stats = reviews.aggregate(
            avg_rating=Avg('rating'),
            five_stars=Count('id', filter=Q(rating=5)),
            four_stars=Count('id', filter=Q(rating=4)),
            three_stars=Count('id', filter=Q(rating=3)),
            two_stars=Count('id', filter=Q(rating=2)),
            one_star=Count('id', filter=Q(rating=1)),
        )

        context['review_stats'] = review_stats

        # Cours similaires
        context['similar_courses'] = Course.objects.filter(
            category=course.category,
            is_published=True
        ).exclude(id=course.id)[:3]

        return context


class LessonView(LoginRequiredMixin, DetailView):
    """Vue d'une leçon"""
    model = Lesson
    template_name = 'courses/lesson_view.html'
    context_object_name = 'lesson'
    slug_field = 'slug'
    slug_url_kwarg = 'lesson_slug'

    def get_object(self):
        course_slug = self.kwargs.get('course_slug')
        lesson_slug = self.kwargs.get('lesson_slug')

        lesson = get_object_or_404(
            Lesson,
            module__course__slug=course_slug,
            slug=lesson_slug
        )

        # Vérifier que l'utilisateur est inscrit au cours
        enrollment = get_object_or_404(
            Enrollment,
            user=self.request.user,
            course=lesson.module.course,
            is_active=True
        )

        # Créer ou récupérer la progression de la leçon
        progress, created = LessonProgress.objects.get_or_create(
            enrollment=enrollment,
            lesson=lesson
        )

        return lesson

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = self.object
        user = self.request.user

        # Récupérer l'inscription
        enrollment = Enrollment.objects.get(
            user=user,
            course=lesson.module.course,
            is_active=True
        )

        # Progression de cette leçon
        try:
            progress = LessonProgress.objects.get(
                enrollment=enrollment,
                lesson=lesson
            )
            context['progress'] = progress
        except LessonProgress.DoesNotExist:
            context['progress'] = None

        # Leçons précédente et suivante
        context['previous_lesson'] = lesson.get_previous_lesson()
        context['next_lesson'] = lesson.get_next_lesson()

        # Tous les modules du cours
        context['modules'] = lesson.module.course.modules.filter(
            is_published=True
        ).prefetch_related('lessons').order_by('order')

        context['enrollment'] = enrollment

        return context


@login_required
def complete_lesson(request, lesson_id):
    """Marquer une leçon comme complétée (HTMX)"""
    lesson = get_object_or_404(Lesson, id=lesson_id)

    # Vérifier l'inscription
    try:
        enrollment = Enrollment.objects.get(
            user=request.user,
            course=lesson.module.course,
            is_active=True
        )
    except Enrollment.DoesNotExist:
        return JsonResponse({'error': 'Non inscrit'}, status=403)

    # Mettre à jour la progression
    progress, created = LessonProgress.objects.get_or_create(
        enrollment=enrollment,
        lesson=lesson
    )

    progress.mark_completed()

    # Recalculer la progression globale
    enrollment.calculate_progress()

    if request.htmx:
        return render(request, 'courses/partials/lesson_completed.html', {
            'lesson': lesson,
            'progress': progress,
            'enrollment': enrollment
        })

    return JsonResponse({
        'success': True,
        'progress': float(enrollment.progress_percentage)
    })


@login_required
def toggle_favorite(request, course_id):
    """Ajouter/retirer un cours des favoris (HTMX)"""
    course = get_object_or_404(Course, id=course_id)

    try:
        enrollment = Enrollment.objects.get(
            user=request.user,
            course=course,
            is_active=True
        )
        enrollment.is_favorite = not enrollment.is_favorite
        enrollment.save()

        if request.htmx:
            return render(request, 'courses/partials/favorite_button.html', {
                'course': course,
                'is_favorite': enrollment.is_favorite
            })

        return JsonResponse({
            'success': True,
            'is_favorite': enrollment.is_favorite
        })

    except Enrollment.DoesNotExist:
        return JsonResponse({'error': 'Non inscrit'}, status=403)


def htmx_search_courses(request):
    """Recherche en temps réel avec HTMX"""
    query = request.GET.get('q', '').strip()

    courses = Course.objects.filter(is_published=True)

    if query:
        courses = courses.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()

    courses = courses[:12]

    return render(request, 'courses/partials/course_cards.html', {
        'courses': courses
    })


def htmx_filter_courses(request):
    """Filtrage dynamique avec HTMX"""
    category = request.GET.get('category')
    difficulty = request.GET.get('difficulty')
    price_range = request.GET.get('price')

    courses = Course.objects.filter(is_published=True)

    if category:
        courses = courses.filter(category__slug=category)

    if difficulty:
        courses = courses.filter(difficulty=difficulty)

    if price_range == 'free':
        courses = courses.filter(price=0)
    elif price_range == 'paid':
        courses = courses.filter(price__gt=0)

    courses = courses.order_by('-rating')[:12]

    return render(request, 'courses/partials/course_cards.html', {
        'courses': courses
    })


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
        # Mettre à jour le nombre d'étudiants
        course.update_students_count()
        messages.success(request, f'Vous êtes inscrit au cours "{course.title}"!')
    else:
        if not enrollment.is_active:
            enrollment.is_active = True
            enrollment.save()
            messages.success(request, f'Réinscription au cours "{course.title}" effectuée!')
        else:
            messages.info(request, 'Vous êtes déjà inscrit à ce cours.')

    return redirect('courses:detail', slug=course.slug)