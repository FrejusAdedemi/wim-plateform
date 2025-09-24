# apps/courses/models.py - Version mise à jour

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

    # Champs YouTube
    youtube_playlist_id = models.CharField('ID Playlist YouTube', max_length=100, blank=True)
    youtube_channel_id = models.CharField('ID Chaîne YouTube', max_length=100, blank=True)
    youtube_channel_name = models.CharField('Nom Chaîne YouTube', max_length=200, blank=True)
    youtube_thumbnail_url = models.URLField('URL Miniature YouTube', blank=True)
    is_youtube_synced = models.BooleanField('Synchronisé YouTube', default=False)
    last_youtube_sync = models.DateTimeField('Dernière sync YouTube', null=True, blank=True)

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

    def update_from_youtube(self):
        """Met à jour les métadonnées du cours depuis YouTube"""
        if self.youtube_playlist_id:
            from apps.youtube.services import YouTubeService
            try:
                youtube_service = YouTubeService()
                playlist_data = youtube_service.get_playlist_details(self.youtube_playlist_id)

                if playlist_data:
                    self.youtube_channel_name = playlist_data['channel_name']
                    self.youtube_thumbnail_url = playlist_data['thumbnail_url']

                    # Mettre à jour l'image du cours si pas définie
                    if not self.image and playlist_data['thumbnail_url']:
                        # Optionnel: télécharger et sauver l'image
                        pass

                    self.save(update_fields=['youtube_channel_name', 'youtube_thumbnail_url'])
            except Exception as e:
                print(f"Erreur mise à jour YouTube: {e}")

    # ... Autres méthodes existantes ...
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

    def calculate_duration(self):
        """Calcule la durée totale du cours"""
        total_duration = 0
        for module in self.modules.filter(is_published=True):
            for lesson in module.lessons.filter(is_published=True):
                total_duration += lesson.duration
        self.duration = total_duration
        self.save(update_fields=['duration'])


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

    # Champs YouTube
    youtube_video_id = models.CharField('ID Vidéo YouTube', max_length=20, blank=True)
    youtube_title = models.CharField('Titre YouTube', max_length=300, blank=True)
    youtube_description = models.TextField('Description YouTube', blank=True)
    youtube_thumbnail_url = models.URLField('Miniature YouTube', blank=True)
    youtube_duration_seconds = models.IntegerField('Durée YouTube (sec)', null=True, blank=True)
    youtube_view_count = models.IntegerField('Vues YouTube', default=0)
    youtube_published_at = models.DateTimeField('Publié sur YouTube', null=True, blank=True)

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

        # Générer l'URL vidéo à partir de l'ID YouTube
        if self.youtube_video_id and not self.video_url:
            self.video_url = f"https://www.youtube.com/watch?v={self.youtube_video_id}"

        # Utiliser le titre YouTube si pas de titre défini
        if self.youtube_title and not self.title:
            self.title = self.youtube_title[:200]

        # Utiliser la durée YouTube si définie
        if self.youtube_duration_seconds and not self.duration:
            self.duration = max(1, self.youtube_duration_seconds // 60)

        super().save(*args, **kwargs)

    # ... Autres méthodes existantes ...
    def get_previous_lesson(self):
        """Retourne la leçon précédente"""
        previous_in_module = self.module.lessons.filter(
            order__lt=self.order,
            is_published=True
        ).order_by('-order').first()

        if previous_in_module:
            return previous_in_module

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
        next_in_module = self.module.lessons.filter(
            order__gt=self.order,
            is_published=True
        ).order_by('order').first()

        if next_in_module:
            return next_in_module

        next_module = self.module.course.modules.filter(
            order__gt=self.module.order,
            is_published=True
        ).order_by('order').first()

        if next_module:
            return next_module.lessons.filter(
                is_published=True
            ).order_by('order').first()

        return None