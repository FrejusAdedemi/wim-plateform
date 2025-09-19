from django.contrib import admin
from .models import Category, Course, Module, Lesson


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1
    fields = ['title', 'description', 'order', 'is_published']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'instructor', 'difficulty', 'price', 'rating', 'total_students',
                    'is_published']
    list_filter = ['category', 'difficulty', 'is_published', 'is_new', 'created_at']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ModuleInline]

    fieldsets = (
        ('Informations de base', {
            'fields': ('title', 'slug', 'category', 'instructor', 'image')
        }),
        ('Contenu', {
            'fields': ('description', 'full_description', 'prerequisites', 'learning_objectives')
        }),
        ('Caractéristiques', {
            'fields': ('difficulty', 'duration', 'price')
        }),
        ('Statuts', {
            'fields': ('is_published', 'is_new', 'is_featured')
        }),
        ('Statistiques', {
            'fields': ('rating', 'total_students', 'total_reviews'),
            'classes': ('collapse',)
        }),
    )


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ['title', 'lesson_type', 'duration', 'order', 'is_published']


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'duration', 'is_published']
    list_filter = ['course', 'is_published']
    search_fields = ['title', 'course__title']
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'lesson_type', 'duration', 'order', 'is_published']
    list_filter = ['lesson_type', 'is_published', 'is_preview']
    search_fields = ['title', 'module__title']
    prepopulated_fields = {'slug': ('title',)}