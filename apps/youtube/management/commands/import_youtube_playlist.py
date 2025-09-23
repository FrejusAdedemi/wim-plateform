# apps/youtube/management/commands/import_youtube_playlist.py
from django.core.management.base import BaseCommand, CommandError
from apps.courses.models import Course, Module, Lesson, Category
from apps.users.models import User
from apps.youtube.services import YouTubeService
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Importe une playlist YouTube comme nouveau cours'

    def add_arguments(self, parser):
        parser.add_argument(
            'playlist_id',
            type=str,
            help='ID de la playlist YouTube à importer'
        )
        parser.add_argument(
            '--instructor-email',
            type=str,
            required=True,
            help='Email de l\'instructeur pour ce cours'
        )
        parser.add_argument(
            '--category',
            type=str,
            help='Slug de la catégorie (par défaut: dev-web)'
        )
        parser.add_argument(
            '--difficulty',
            type=str,
            choices=['beginner', 'intermediate', 'advanced'],
            default='beginner',
            help='Niveau de difficulté du cours'
        )
        parser.add_argument(
            '--price',
            type=float,
            default=0.0,
            help='Prix du cours (défaut: gratuit)'
        )

    def handle(self, *args, **options):
        youtube_service = YouTubeService()
        playlist_id = options['playlist_id']

        self.stdout.write(f'Import de la playlist YouTube: {playlist_id}')

        # Récupérer les détails de la playlist
        playlist_data = youtube_service.get_playlist_details(playlist_id)
        if not playlist_data:
            raise CommandError(f'Impossible de récupérer la playlist {playlist_id}')

        # Vérifier l'instructeur
        try:
            instructor = User.objects.get(email=options['instructor_email'])
        except User.DoesNotExist:
            raise CommandError(f'Instructeur {options["instructor_email"]} introuvable')

        # Récupérer la catégorie
        category_slug = options.get('category', 'dev-web')
        try:
            category = Category.objects.get(slug=category_slug)
        except Category.DoesNotExist:
            # Créer la catégorie par défaut si elle n'existe pas
            category = Category.objects.create(
                name='Développement Web',
                slug='dev-web',
                description='Cours de développement web'
            )

        # Créer le cours
        course_title = playlist_data['title']
        course = Course.objects.create(
            title=course_title,
            slug=slugify(course_title),
            description=playlist_data['description'][:500] if playlist_data[
                'description'] else f"Cours basé sur la playlist {course_title}",
            full_description=playlist_data[
                                 'description'] or f"Cours complet basé sur la playlist YouTube '{course_title}'",
            category=category,
            instructor=instructor,
            difficulty=options['difficulty'],
            price=options['price'],
            youtube_playlist_id=playlist_id,
            youtube_channel_name=playlist_data['channel_name'],
            youtube_thumbnail_url=playlist_data['thumbnail_url'],
            is_published=True,
            is_youtube_synced=False
        )

        self.stdout.write(f'Cours créé: {course.title} (ID: {course.id})')

        # Créer un module par défaut
        module = Module.objects.create(
            course=course,
            title='Contenu principal',
            description='Leçons importées depuis YouTube',
            order=1
        )

        # Récupérer et importer les vidéos
        videos = youtube_service.get_playlist_videos(playlist_id)

        if not videos:
            self.stdout.write(
                self.style.WARNING('Aucune vidéo trouvée dans la playlist')
            )
            return

        self.stdout.write(f'Import de {len(videos)} vidéos...')

        for i, video in enumerate(videos):
            lesson = Lesson.objects.create(
                module=module,
                title=video['title'][:200],
                lesson_type='video',
                order=i + 1,
                youtube_video_id=video['id'],
                youtube_title=video['title'],
                youtube_description=video['description'],
                youtube_thumbnail_url=video['thumbnail_url'],
                youtube_duration_seconds=video['duration_seconds'],
                youtube_view_count=video['view_count'],
                youtube_published_at=video['published_at'],
                duration=max(1, video['duration_seconds'] // 60),
                video_url=f"https://www.youtube.com/watch?v={video['id']}",
                content=f"Vidéo: {video['title']}",
                is_published=True
            )

            self.stdout.write(f'  ✓ Leçon créée: {lesson.title}')

        # Calculer la durée totale
        course.calculate_duration()
        course.is_youtube_synced = True
        course.save()

        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Import terminé! Cours "{course.title}" créé avec {len(videos)} leçons'
            )
        )
        self.stdout.write(f'URL du cours: /courses/{course.slug}/')
