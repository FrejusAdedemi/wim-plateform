from django.contrib import admin
from .models import Enrollment, Review, Favorite


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'progress_percentage', 'enrolled_at', 'is_completed', 'is_active']
    list_filter = ['is_completed', 'is_active', 'enrolled_at']
    search_fields = ['user__email', 'course__title']
    date_hierarchy = 'enrolled_at'

    readonly_fields = ['enrolled_at', 'started_at', 'completed_at', 'last_accessed']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'rating', 'created_at', 'is_verified', 'helpful_count']
    list_filter = ['rating', 'is_verified', 'is_featured', 'created_at']
    search_fields = ['user__email', 'course__title', 'comment']
    date_hierarchy = 'created_at'

    actions = ['mark_as_verified', 'mark_as_featured']

    def mark_as_verified(self, request, queryset):
        queryset.update(is_verified=True)
        self.message_user(request, f"{queryset.count()} avis marqués comme vérifiés")

    mark_as_verified.short_description = "Marquer comme vérifié"

    def mark_as_featured(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, f"{queryset.count()} avis mis en avant")

    mark_as_featured.short_description = "Mettre en avant"


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'added_at']
    list_filter = ['added_at']
    search_fields = ['user__email', 'course__title']
    date_hierarchy = 'added_at'