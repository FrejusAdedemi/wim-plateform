# apps/youtube/management/commands/sync_youtube_content.py
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from apps.courses.models import Course, Module, Lesson
from apps.youtube.services import YouTubeService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Synchronise le contenu YouTube pour tous les cours ou un cours spécifique'

    def add_arguments(self, parser):
        parser.add_argument(
            '--course-id',
            type=int,
            help='ID du cours à synchroniser (optionnel)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force la synchronisation même si récemment synchronisé',
        )
        parser.add_argument(
            '--create-modules',
            action='store_true',
            help='Crée automatiquement des modules si nécessaire',
        )

    def handle(self, *args, **options):
        youtube_service = YouTubeService()

        # Filtrer les cours à synchroniser
        courses_query = Course.objects.filter(
            is_published=True
        ).exclude(
            youtube_playlist_id='',
            youtube_channel_id=''
        )

        if options['course_id']:
            courses_query = courses_query.filter(id=options['course_id'])

        courses = courses_query.all()

        if not courses:
            self.stdout.write(
                self.style.WARNING('Aucun cours avec configuration YouTube trouvé')
            )
            return

        self.stdout.write(f'Synchronisation de {courses.count()} cours...')

        for course in courses:
            try:
                self.sync_course(course, youtube_service, options)

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Erreur lors de la sync du cours {course.title}: {e}')
                )

        self.stdout.write(
            self.style.SUCCESS('Synchronisation terminée')
        )

    def sync_course(self, course, youtube_service, options):
        """Synchronise un cours avec YouTube"""

        # Vérifier si synchronisation nécessaire
        if not options['force'] and course.last_youtube_sync:
            time_diff = timezone.now() - course.last_youtube_sync
            if time_diff.total_seconds() < 3600:  # Moins d'une heure
                self.stdout.write(f'Cours {course.title} récemment synchronisé, ignoré')
                return

        self.stdout.write(f'Synchronisation du cours: {course.title}')

        videos = []

        # Récupérer les vidéos selon la source
        if course.youtube_playlist_id:
            self.stdout.write(f'  Récupération depuis la playlist: {course.youtube_playlist_id}')
            videos = youtube_service.get_playlist_videos(course.youtube_playlist_id)
        elif course.youtube_channel_id:
            self.stdout.write(f'  Récupération depuis la chaîne: {course.youtube_channel_id}')
            videos = youtube_service.get_channel_videos(course.youtube_channel_id)

        if not videos:
            self.stdout.write(
                self.style.WARNING(f'  Aucune vidéo trouvée pour {course.title}')
            )
            return

        self.stdout.write(f'  {len(videos)} vidéos trouvées')

        # Mettre à jour les métadonnées du cours
        course.update_from_youtube()

        # Créer ou mettre à jour les leçons
        created_lessons = 0
        updated_lessons = 0

        # Obtenir ou créer un module par défaut
        if options['create_modules']:
            default_module, created = Module.objects.get_or_create(
                course=course,
                order=1,
                defaults={
                    'title': 'Contenu principal',
                    'description': 'Leçons importées depuis YouTube'
                }
            )
        else:
            default_module = course.modules.first()
            if not default_module:
                self.stdout.write(
                    self.style.WARNING(f'  Aucun module trouvé pour {course.title}. Utilisez --create-modules.')
                )
                return

        for i, video in enumerate(videos):
            lesson, created = Lesson.objects.get_or_create(
                module=default_module,
                youtube_video_id=video['id'],
                defaults={
                    'title': video['title'][:200],
                    'lesson_type': 'video',
                    'order': i + 1,
                    'youtube_title': video['title'],
                    'youtube_description': video['description'],
                    'youtube_thumbnail_url': video['thumbnail_url'],
                    'youtube_duration_seconds': video['duration_seconds'],
                    'youtube_view_count': video['view_count'],
                    'youtube_published_at': video['published_at'],
                    'duration': max(1, video['duration_seconds'] // 60),
                    'video_url': f"https://www.youtube.com/watch?v={video['id']}",
                    'is_published': True
                }
            )

            if created:
                created_lessons += 1
            else:
                # Mettre à jour les métadonnées existantes
                lesson.youtube_title = video['title']
                lesson.youtube_description = video['description']
                lesson.youtube_thumbnail_url = video['thumbnail_url']
                lesson.youtube_duration_seconds = video['duration_seconds']
                lesson.youtube_view_count = video['view_count']
                lesson.duration = max(1, video['duration_seconds'] // 60)
                lesson.save()
                updated_lessons += 1

        # Mettre à jour la durée du cours
        course.calculate_duration()
        course.last_youtube_sync = timezone.now()
        course.is_youtube_synced = True
        course.save()

        self.stdout.write(
            self.style.SUCCESS(
                f'  ✓ {created_lessons} leçons créées, {updated_lessons} mises à jour'
            )
        )

