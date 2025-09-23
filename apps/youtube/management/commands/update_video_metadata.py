# apps/youtube/management/commands/update_video_metadata.py
from django.core.management.base import BaseCommand
from apps.courses.models import Lesson
from apps.youtube.services import YouTubeService
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Met à jour les métadonnées des vidéos YouTube'

    def add_arguments(self, parser):
        parser.add_argument(
            '--lesson-id',
            type=int,
            help='ID de la leçon à mettre à jour (optionnel)'
        )
        parser.add_argument(
            '--older-than-days',
            type=int,
            default=7,
            help='Mettre à jour les leçons non mises à jour depuis X jours'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=50,
            help='Nombre de vidéos à traiter par batch'
        )

    def handle(self, *args, **options):
        youtube_service = YouTubeService()

        # Filtrer les leçons à mettre à jour
        lessons_query = Lesson.objects.filter(
            lesson_type='video',
            is_published=True
        ).exclude(
            youtube_video_id=''
        )

        if options['lesson_id']:
            lessons_query = lessons_query.filter(id=options['lesson_id'])
        else:
            # Leçons non mises à jour récemment
            cutoff_date = timezone.now() - timedelta(days=options['older_than_days'])
            lessons_query = lessons_query.filter(
                updated_at__lt=cutoff_date
            )

        lessons = lessons_query.all()

        if not lessons:
            self.stdout.write(
                self.style.WARNING('Aucune leçon à mettre à jour')
            )
            return

        self.stdout.write(f'Mise à jour de {lessons.count()} leçons...')

        # Traiter par batches pour optimiser les appels API
        batch_size = options['batch_size']
        updated_count = 0

        for i in range(0, len(lessons), batch_size):
            batch = lessons[i:i + batch_size]
            video_ids = [lesson.youtube_video_id for lesson in batch]

            # Récupérer les métadonnées en batch
            videos_data = youtube_service.get_videos_details(video_ids)
            videos_dict = {video['id']: video for video in videos_data}

            # Mettre à jour chaque leçon
            for lesson in batch:
                if lesson.youtube_video_id in videos_dict:
                    video_data = videos_dict[lesson.youtube_video_id]

                    # Mettre à jour les métadonnées
                    lesson.youtube_title = video_data['title']
                    lesson.youtube_description = video_data['description']
                    lesson.youtube_thumbnail_url = video_data['thumbnail_url']
                    lesson.youtube_duration_seconds = video_data['duration_seconds']
                    lesson.youtube_view_count = video_data['view_count']
                    lesson.youtube_published_at = video_data['published_at']

                    # Mettre à jour la durée en minutes
                    if video_data['duration_seconds']:
                        lesson.duration = max(1, video_data['duration_seconds'] // 60)

                    lesson.save()
                    updated_count += 1

                    self.stdout.write(f'  ✓ {lesson.title}')
                else:
                    self.stdout.write(
                        self.style.WARNING(f'  ⚠ Vidéo non trouvée: {lesson.youtube_video_id}')
                    )

        self.stdout.write(
            self.style.SUCCESS(f'✓ {updated_count} leçons mises à jour')
        )
