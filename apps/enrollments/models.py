from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Enrollment(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='enrollments',
                             verbose_name='utilisateur')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='enrollments',
                               verbose_name='cours')

    progress_percentage = models.DecimalField('progression (%)', max_digits=5, decimal_places=2, default=0,
                                              validators=[MinValueValidator(0), MaxValueValidator(100)])

    enrolled_at = models.DateTimeField('inscrit le', auto_now_add=True)
    started_at = models.DateTimeField('commencé le', null=True, blank=True)
    completed_at = models.DateTimeField('complété le', null=True, blank=True)
    last_accessed = models.DateTimeField('dernier accès', auto_now=True)

    is_active = models.BooleanField('actif', default=True)
    is_completed = models.BooleanField('complété', default=False)
    is_favorite = models.BooleanField('favori', default=False)

    total_time_spent = models.IntegerField('temps total (secondes)', default=0)

    class Meta:
        verbose_name = 'inscription'
        verbose_name_plural = 'inscriptions'
        ordering = ['-enrolled_at']
        unique_together = [['user', 'course']]

    def __str__(self):
        return f"{self.user.email} - {self.course.title}"

    def calculate_progress(self):
        """Calcule et met à jour la progression du cours"""
        from apps.progress.models import LessonProgress

        # Compter le total de leçons dans le cours
        total_lessons = 0
        for module in self.course.modules.filter(is_published=True):
            total_lessons += module.lessons.filter(is_published=True).count()

        if total_lessons == 0:
            self.progress_percentage = 0
        else:
            # Compter les leçons complétées
            completed_lessons = LessonProgress.objects.filter(
                enrollment=self,
                is_completed=True
            ).count()

            self.progress_percentage = (completed_lessons / total_lessons) * 100

            # Marquer comme complété si 100%
            if self.progress_percentage >= 100:
                self.is_completed = True
                if not self.completed_at:
                    self.completed_at = timezone.now()

        self.save(update_fields=['progress_percentage', 'is_completed', 'completed_at'])

    def get_time_spent_hours(self):
        """Retourne le temps passé en heures"""
        return round(self.total_time_spent / 3600, 1) if self.total_time_spent > 0 else 0

    def mark_started(self):
        """Marque le cours comme commencé"""
        if not self.started_at:
            self.started_at = timezone.now()
            self.save(update_fields=['started_at'])


class Review(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='reviews', verbose_name='utilisateur')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='reviews', verbose_name='cours')
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='review', null=True, blank=True)

    rating = models.IntegerField('note', validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField('commentaire', max_length=1000, blank=True)

    content_quality = models.IntegerField('qualité contenu', validators=[MinValueValidator(1), MaxValueValidator(5)],
                                          null=True, blank=True)
    instructor_quality = models.IntegerField('qualité instructeur',
                                             validators=[MinValueValidator(1), MaxValueValidator(5)], null=True,
                                             blank=True)
    value_for_money = models.IntegerField('rapport qualité/prix',
                                          validators=[MinValueValidator(1), MaxValueValidator(5)], null=True,
                                          blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_verified = models.BooleanField('vérifié', default=False)
    is_featured = models.BooleanField('mis en avant', default=False)
    helpful_count = models.IntegerField('votes utiles', default=0)

    class Meta:
        verbose_name = 'avis'
        verbose_name_plural = 'avis'
        ordering = ['-created_at']
        unique_together = [['user', 'course']]

    def __str__(self):
        return f"{self.user.email} - {self.course.title} ({self.rating}★)"


class Favorite(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='favorites')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='favorited_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'favori'
        verbose_name_plural = 'favoris'
        ordering = ['-added_at']
        unique_together = [['user', 'course']]

    def __str__(self):
        return f"{self.user.email} - {self.course.title}"