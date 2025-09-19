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

    def mark_completed(self):
        """Marque la leçon comme complétée"""
        if not self.is_completed:
            self.is_completed = True
            self.completed_at = timezone.now()

            if not self.started_at:
                self.started_at = timezone.now()

            self.save(update_fields=['is_completed', 'completed_at', 'started_at'])

            # Recalculer la progression du cours
            self.enrollment.calculate_progress()

    def mark_started(self):
        """Marque la leçon comme commencée"""
        if not self.started_at:
            self.started_at = timezone.now()
            self.save(update_fields=['started_at'])

    def update_video_position(self, position):
        """Met à jour la position de la vidéo"""
        self.video_position = position
        self.mark_started()
        self.save(update_fields=['video_position'])


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

    def calculate_score(self):
        """Calcule le score du quiz"""
        if self.total_questions > 0:
            self.score = (self.correct_answers / self.total_questions) * 100
            self.is_passed = self.score >= 70  # Seuil de réussite à 70%
        else:
            self.score = 0
            self.is_passed = False

        self.save(update_fields=['score', 'is_passed'])

    def complete_quiz(self):
        """Marque le quiz comme terminé"""
        if not self.completed_at:
            self.completed_at = timezone.now()
            self.calculate_score()

            # Si le quiz est réussi, marquer la leçon comme complétée
            if self.is_passed:
                lesson_progress, created = LessonProgress.objects.get_or_create(
                    enrollment=self.enrollment,
                    lesson=self.lesson
                )
                lesson_progress.mark_completed()


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

    def end_session(self):
        """Termine la session d'étude"""
        if not self.ended_at:
            self.ended_at = timezone.now()
            self.duration = (self.ended_at - self.started_at).total_seconds()
            self.save(update_fields=['ended_at', 'duration'])

    def add_lesson_viewed(self, lesson):
        """Ajoute une leçon vue à la session"""
        self.lessons_viewed.add(lesson)


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

    def update_statistics(self):
        """Met à jour toutes les statistiques"""
        from apps.enrollments.models import Enrollment
        from django.db.models import Avg

        enrollments = Enrollment.objects.filter(user=self.user, is_active=True)

        # Mettre à jour les compteurs
        self.total_courses_enrolled = enrollments.count()
        self.total_courses_completed = enrollments.filter(is_completed=True).count()

        # Compter les leçons complétées
        self.total_lessons_completed = LessonProgress.objects.filter(
            enrollment__user=self.user,
            is_completed=True
        ).count()

        # Temps total d'étude
        self.total_study_time = sum(e.total_time_spent for e in enrollments)

        # Quiz réussis
        self.total_quizzes_passed = QuizAttempt.objects.filter(
            enrollment__user=self.user,
            is_passed=True
        ).count()

        # Score moyen des quiz
        avg_score = QuizAttempt.objects.filter(
            enrollment__user=self.user
        ).aggregate(avg=Avg('score'))['avg']
        self.average_quiz_score = avg_score or 0

        # Progression moyenne
        if self.total_courses_enrolled > 0:
            avg_progress = enrollments.aggregate(avg=Avg('progress_percentage'))['avg']
            self.average_progress = avg_progress or 0

        # Calculer la série de jours
        self.calculate_streak()

        self.save()

    def calculate_streak(self):
        """Calcule la série de jours consécutifs d'étude"""
        from datetime import date, timedelta

        today = date.today()
        current_date = today
        streak = 0

        # Vérifier les jours consécutifs
        while True:
            has_activity = LessonProgress.objects.filter(
                enrollment__user=self.user,
                completed_at__date=current_date
            ).exists()

            if has_activity:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break

        self.current_streak_days = streak
        if streak > self.longest_streak_days:
            self.longest_streak_days = streak

        # Dernière date d'étude
        if streak > 0:
            self.last_study_date = today