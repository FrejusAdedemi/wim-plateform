from django.db import models
from django.utils.text import slugify
from django.urls import reverse


class Category(models.Model):
    name = models.CharField('nom', max_length=100, unique=True)
    slug = models.SlugField('slug', max_length=100, unique=True, blank=True)
    description = models.TextField('description', blank=True)
    icon = models.CharField('icône', max_length=50, blank=True)
    color = models.CharField('couleur', max_length=7, default='#4A90E2')
    order = models.IntegerField('ordre', default=0)
    is_active = models.BooleanField('actif', default=True)

    class Meta:
        verbose_name = 'catégorie'
        verbose_name_plural = 'catégories'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Course(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Débutant'),
        ('intermediate', 'Intermédiaire'),
        ('advanced', 'Avancé'),
    ]

    title = models.CharField('titre', max_length=200)
    slug = models.SlugField('slug', max_length=250, unique=True, blank=True)
    description = models.TextField('description courte', max_length=500)
    full_description = models.TextField('description complète')

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='courses',
                                 verbose_name='catégorie')
    instructor = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='taught_courses',
                                   verbose_name='instructeur')

    image = models.ImageField(upload_to='course_images/', verbose_name='image', blank=True, null=True)

    difficulty = models.CharField('difficulté', max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    duration = models.IntegerField('durée (minutes)', default=0)
    price = models.DecimalField('prix', max_digits=10, decimal_places=2, default=0)

    rating = models.DecimalField('note', max_digits=3, decimal_places=2, default=0)
    total_students = models.IntegerField('étudiants', default=0)
    total_reviews = models.IntegerField('avis', default=0)

    is_published = models.BooleanField('publié', default=False)
    is_new = models.BooleanField('nouveau', default=True)
    is_featured = models.BooleanField('mis en avant', default=False)

    prerequisites = models.TextField('prérequis', blank=True)
    learning_objectives = models.TextField('objectifs', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'cours'
        verbose_name_plural = 'cours'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('courses:detail', kwargs={'slug': self.slug})

    def update_students_count(self):
        """Met à jour le nombre d'étudiants inscrits"""
        self.total_students = self.enrollments.filter(is_active=True).count()
        self.save(update_fields=['total_students'])

    def update_rating(self):
        """Met à jour la note moyenne du cours"""
        from django.db.models import Avg
        reviews = self.reviews.all()
        if reviews.exists():
            avg_rating = reviews.aggregate(avg=Avg('rating'))['avg']
            self.rating = round(avg_rating, 2) if avg_rating else 0
            self.total_reviews = reviews.count()
        else:
            self.rating = 0
            self.total_reviews = 0
        self.save(update_fields=['rating', 'total_reviews'])

    def get_completion_rate(self):
        """Retourne le taux de complétion du cours"""
        total_enrolled = self.enrollments.filter(is_active=True).count()
        if total_enrolled == 0:
            return 0
        completed = self.enrollments.filter(is_completed=True).count()
        return round((completed / total_enrolled) * 100, 1)

    def get_total_lessons(self):
        """Retourne le nombre total de leçons publiées"""
        total = 0
        for module in self.modules.filter(is_published=True):
            total += module.lessons.filter(is_published=True).count()
        return total

    def calculate_duration(self):
        """Calcule la durée totale du cours"""
        total_duration = 0
        for module in self.modules.filter(is_published=True):
            for lesson in module.lessons.filter(is_published=True):
                total_duration += lesson.duration
        self.duration = total_duration
        self.save(update_fields=['duration'])

    def get_first_lesson(self):
        """Retourne la première leçon du cours"""
        first_module = self.modules.filter(is_published=True).order_by('order').first()
        if first_module:
            return first_module.lessons.filter(is_published=True).order_by('order').first()
        return None


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules', verbose_name='cours')
    title = models.CharField('titre', max_length=200)
    description = models.TextField('description', blank=True)
    order = models.IntegerField('ordre', default=0)
    duration = models.IntegerField('durée (minutes)', default=0)
    is_published = models.BooleanField('publié', default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'module'
        verbose_name_plural = 'modules'
        ordering = ['course', 'order']
        unique_together = [['course', 'order']]

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    def calculate_duration(self):
        """Calcule la durée du module"""
        total_duration = self.lessons.filter(is_published=True).aggregate(
            total=models.Sum('duration')
        )['total'] or 0
        self.duration = total_duration
        self.save(update_fields=['duration'])

    def get_lessons_count(self):
        """Retourne le nombre de leçons publiées"""
        return self.lessons.filter(is_published=True).count()


class Lesson(models.Model):
    LESSON_TYPE_CHOICES = [
        ('video', 'Vidéo'),
        ('text', 'Texte'),
        ('quiz', 'Quiz'),
        ('exercise', 'Exercice'),
    ]

    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons', verbose_name='module')
    title = models.CharField('titre', max_length=200)
    slug = models.SlugField('slug', max_length=250, blank=True)

    lesson_type = models.CharField('type', max_length=20, choices=LESSON_TYPE_CHOICES, default='video')

    content = models.TextField('contenu', blank=True)
    video_url = models.URLField('URL vidéo', blank=True)

    duration = models.IntegerField('durée (minutes)', default=0)
    order = models.IntegerField('ordre', default=0)

    resources = models.TextField('ressources', blank=True)
    is_preview = models.BooleanField('aperçu gratuit', default=False)
    is_published = models.BooleanField('publié', default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'leçon'
        verbose_name_plural = 'leçons'
        ordering = ['module', 'order']
        unique_together = [['module', 'order']]

    def __str__(self):
        return f"{self.module.title} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_previous_lesson(self):
        """Retourne la leçon précédente"""
        # Chercher dans le même module
        previous_in_module = self.module.lessons.filter(
            order__lt=self.order,
            is_published=True
        ).order_by('-order').first()

        if previous_in_module:
            return previous_in_module

        # Chercher dans le module précédent
        previous_module = self.module.course.modules.filter(
            order__lt=self.module.order,
            is_published=True
        ).order_by('-order').first()

        if previous_module:
            return previous_module.lessons.filter(
                is_published=True
            ).order_by('-order').first()

        return None

    def get_next_lesson(self):
        """Retourne la leçon suivante"""
        # Chercher dans le même module
        next_in_module = self.module.lessons.filter(
            order__gt=self.order,
            is_published=True
        ).order_by('order').first()

        if next_in_module:
            return next_in_module

        # Chercher dans le module suivant
        next_module = self.module.course.modules.filter(
            order__gt=self.module.order,
            is_published=True
        ).order_by('order').first()

        if next_module:
            return next_module.lessons.filter(
                is_published=True
            ).order_by('order').first()

        return None

    def is_completed_by_user(self, user):
        """Vérifie si la leçon est complétée par un utilisateur"""
        from apps.progress.models import LessonProgress
        from apps.enrollments.models import Enrollment

        try:
            enrollment = Enrollment.objects.get(
                user=user,
                course=self.module.course,
                is_active=True
            )
            progress = LessonProgress.objects.get(
                enrollment=enrollment,
                lesson=self
            )
            return progress.is_completed
        except (Enrollment.DoesNotExist, LessonProgress.DoesNotExist):
            return False