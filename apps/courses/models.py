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