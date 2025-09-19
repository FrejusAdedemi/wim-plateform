from django.contrib import admin
from .models import Certificate, CertificateTemplate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['certificate_id', 'student_name', 'course_title', 'issued_at', 'is_valid', 'download_count']
    list_filter = ['is_valid', 'issued_at']
    search_fields = ['certificate_id', 'student_name', 'course_title', 'verification_code']
    date_hierarchy = 'issued_at'

    readonly_fields = ['certificate_id', 'verification_code', 'issued_at', 'download_count']

    actions = ['invalidate_certificates']

    def invalidate_certificates(self, request, queryset):
        queryset.update(is_valid=False)
        self.message_user(request, f"{queryset.count()} certificats invalidés")

    invalidate_certificates.short_description = "Invalider les certificats"


@admin.register(CertificateTemplate)
class CertificateTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'is_default', 'created_at']
    list_filter = ['is_active', 'is_default']
    search_fields = ['name']