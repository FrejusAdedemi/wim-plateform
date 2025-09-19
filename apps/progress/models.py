from django.db import models
from django.utils import timezone


class LessonProgress(models.Model):
    enrollment = models.ForeignKey('enrollments.Enrollment', on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey('courses.Lesson', on_delete=models.CASCADE, related_name='user_progress')

    is_completed = models.BooleanField('complété', default=False)
    time_spent = models.IntegerField('temps passé (secondes)', default=0)
    video_position = models.IntegerField('position vidéo (secondes)', default=0)

    started_at = models.DateTimeField('commencé le', null=True, blank=True)
    completed_at = models.DateTimeField('complété le', null=True, blank=True)
    last_accessed = models.DateTimeField('dernier accès', auto_now=True)

    notes = models.TextField('notes', blank=True)

    class Meta:
        verbose_name = 'progression de leçon'
        verbose_name_plural = 'progressions de leçons'
        unique_together = [['enrollment', 'lesson']]
        ordering = ['enrollment', 'lesson__module__order', 'lesson__order']

    def __str__(self):
        status = "✓" if self.is_completed else "○"
        return f"{status} {self.enrollment.user.email} - {self.lesson.title}"


class QuizAttempt(models.Model):
    enrollment = models.ForeignKey('enrollments.Enrollment', on_delete=models.CASCADE, related_name='quiz_attempts')
    lesson = models.ForeignKey('courses.Lesson', on_delete=models.CASCADE, related_name='quiz_attempts',
                               limit_choices_to={'lesson_type': 'quiz'})

    score = models.DecimalField('score', max_digits=5, decimal_places=2, default=0)
    total_questions = models.IntegerField('nombre questions', default=0)
    correct_answers = models.IntegerField('réponses correctes', default=0)

    time_taken = models.IntegerField('temps pris (secondes)', default=0)
    is_passed = models.BooleanField('réussi', default=False)

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField('terminé le', null=True, blank=True)

    answers = models.JSONField('réponses', default=dict, blank=True)

    class Meta:
        verbose_name = 'tentative de quiz'
        verbose_name_plural = 'tentatives de quiz'
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.enrollment.user.email} - {self.lesson.title} ({self.score}%)"


class StudySession(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='study_sessions')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='study_sessions')

    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField('fin', null=True, blank=True)
    duration = models.IntegerField('durée (secondes)', default=0)

    lessons_viewed = models.ManyToManyField('courses.Lesson', related_name='study_sessions')

    class Meta:
        verbose_name = 'session d\'étude'
        verbose_name_plural = 'sessions d\'étude'
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.user.email} - {self.course.title} ({self.started_at.date()})"


class UserStatistics(models.Model):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='statistics')

    total_courses_enrolled = models.IntegerField('cours inscrits', default=0)
    total_courses_completed = models.IntegerField('cours complétés', default=0)
    total_lessons_completed = models.IntegerField('leçons complétées', default=0)
    total_study_time = models.IntegerField('temps total (secondes)', default=0)
    total_quizzes_passed = models.IntegerField('quiz réussis', default=0)

    average_quiz_score = models.DecimalField('score moyen quiz', max_digits=5, decimal_places=2, default=0)
    average_progress = models.DecimalField('progression moyenne', max_digits=5, decimal_places=2, default=0)

    current_streak_days = models.IntegerField('série actuelle (jours)', default=0)
    longest_streak_days = models.IntegerField('plus longue série (jours)', default=0)
    last_study_date = models.DateField('dernière étude', null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'statistiques utilisateur'
        verbose_name_plural = 'statistiques utilisateurs'

    def __str__(self):
        return f"Stats de {self.user.email}"