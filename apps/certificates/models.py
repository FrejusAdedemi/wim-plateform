from django.db import models
from django.urls import reverse
from django.utils import timezone
import uuid
import hashlib


class Certificate(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='certificates')
    enrollment = models.OneToOneField('enrollments.Enrollment', on_delete=models.CASCADE, related_name='certificate')

    pdf_file = models.FileField(upload_to='certificates/', blank=True, null=True)

    certificate_id = models.CharField('ID certificat', max_length=50, unique=True, editable=False, blank=True)
    verification_code = models.CharField('code vérification', max_length=64, unique=True, editable=False, blank=True)

    issued_at = models.DateTimeField('délivré le', auto_now_add=True)

    student_name = models.CharField('nom étudiant', max_length=200, blank=True)
    course_title = models.CharField('titre cours', max_length=200, blank=True)
    instructor_name = models.CharField('nom instructeur', max_length=200, blank=True)
    completion_date = models.DateField('date complétion', blank=True, null=True)

    final_score = models.DecimalField('score final', max_digits=5, decimal_places=2, null=True, blank=True)

    is_valid = models.BooleanField('valide', default=True)
    download_count = models.IntegerField('téléchargements', default=0)

    class Meta:
        verbose_name = 'certificat'
        verbose_name_plural = 'certificats'
        ordering = ['-issued_at']
        unique_together = [['user', 'course']]

    def __str__(self):
        return f"Certificat - {self.student_name} - {self.course_title}"

    def save(self, *args, **kwargs):
        if not self.certificate_id:
            year = timezone.now().year
            random_part = str(uuid.uuid4().hex)[:5].upper()
            self.certificate_id = f"WIM-{year}-{random_part}"

        if not self.verification_code:
            data = f"{self.user.id}{self.course.id}{timezone.now().isoformat()}"
            self.verification_code = hashlib.sha256(data.encode()).hexdigest()

        if not self.student_name:
            self.student_name = self.user.get_full_name()

        if not self.course_title:
            self.course_title = self.course.title

        if not self.instructor_name:
            self.instructor_name = self.course.instructor.get_full_name()

        if not self.completion_date and self.enrollment.completed_at:
            self.completion_date = self.enrollment.completed_at.date()

        super().save(*args, **kwargs)


class CertificateTemplate(models.Model):
    name = models.CharField('nom', max_length=100, unique=True)
    description = models.TextField('description', blank=True)

    template_file = models.FileField(upload_to='certificate_templates/')
    background_image = models.ImageField(upload_to='certificate_backgrounds/', blank=True, null=True)

    primary_color = models.CharField('couleur principale', max_length=7, default='#4A90E2')
    font_family = models.CharField('police', max_length=100, default='Inter')

    is_active = models.BooleanField('actif', default=True)
    is_default = models.BooleanField('par défaut', default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'template de certificat'
        verbose_name_plural = 'templates de certificats'
        ordering = ['-is_default', 'name']

    def __str__(self):
        return self.name