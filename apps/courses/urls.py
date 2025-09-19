# ============================================================================
# apps/courses/urls.py
# ============================================================================

from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    # Liste des cours
    path('', views.CourseListView.as_view(), name='list'),

    # Détail d'un cours
    path('<slug:slug>/', views.CourseDetailView.as_view(), name='detail'),

    # Vue d'une leçon
    path('<slug:course_slug>/lesson/<slug:lesson_slug>/',
         views.LessonView.as_view(), name='lesson'),

    # Actions HTMX
    path('htmx/search/', views.htmx_search_courses, name='htmx_search'),
    path('htmx/filter/', views.htmx_filter_courses, name='htmx_filter'),
    path('htmx/complete/<int:lesson_id>/', views.complete_lesson, name='complete_lesson'),
    path('htmx/favorite/<int:course_id>/', views.toggle_favorite, name='toggle_favorite'),

    # Inscription
    path('enroll/<int:course_id>/', views.enroll_course, name='enroll'),
]