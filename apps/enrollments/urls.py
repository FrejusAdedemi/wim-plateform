# ============================================================================
# apps/enrollments/urls.py
# ============================================================================

from django.urls import path
from . import views

app_name = 'enrollments'

urlpatterns = [
    path('my-courses/', views.MyCoursesView.as_view(), name='my-courses'),
    path('enroll/<int:course_id>/', views.enroll_course, name='enroll'),
    path('unenroll/<int:enrollment_id>/', views.unenroll_course, name='unenroll'),
    path('review/<int:course_id>/', views.submit_review, name='submit_review'),
    path('favorites/', views.FavoritesView.as_view(), name='favorites'),
]