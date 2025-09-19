# ============================================================================
# apps/progress/urls.py
# ============================================================================

from django.urls import path
from . import views

app_name = 'progress'

urlpatterns = [
    path('overview/', views.ProgressOverviewView.as_view(), name='overview'),
    path('course/<int:course_id>/', views.CourseProgressView.as_view(), name='course_progress'),
    path('stats/', views.user_statistics, name='stats'),
    path('update/', views.update_progress, name='update'),
]