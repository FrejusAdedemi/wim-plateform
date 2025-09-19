from django.contrib import admin
from .models import LessonProgress, QuizAttempt, StudySession, UserStatistics

@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'lesson', 'is_completed', 'time_spent', 'completed_at']
    list_filter = ['is_completed', 'completed_at']
    search_fields = ['enrollment__user__email', 'lesson__title']
    date_hierarchy = 'completed_at'

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'lesson', 'score', 'is_passed', 'started_at']
    list_filter = ['is_passed', 'started_at']
    search_fields = ['enrollment__user__email', 'lesson__title']
    date_hierarchy = 'started_at'

@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'started_at', 'ended_at', 'duration']
    list_filter = ['started_at']
    search_fields = ['user__email', 'course__title']
    date_hierarchy = 'started_at'

@admin.register(UserStatistics)
class UserStatisticsAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_courses_enrolled', 'total_courses_completed', 'current_streak_days']
    list_filter = ['updated_at']
    search_fields = ['user__email']
    readonly_fields = ['updated_at']