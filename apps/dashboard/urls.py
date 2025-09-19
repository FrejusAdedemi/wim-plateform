# ============================================================================
# apps/dashboard/urls.py
# ============================================================================

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='index'),
    path('search/', views.search_courses, name='search'),
    path('filter/', views.filter_courses, name='filter'),
    path('stats/', views.user_stats, name='stats'),
]