# apps/youtube/management/commands/test_import.py

from django.core.management.base import BaseCommand
from apps.youtube.services import YouTubeService
from django.conf import settings
from apps.users.models import User


class Command(BaseCommand):
    help = 'Test rapide de l\'import YouTube'

    def handle(self, *args, **options):
        self.stdout.write('🧪 Test de configuration YouTube...\n')

        # 1. Vérifier la clé API
        api_key = getattr(settings, 'YOUTUBE_API_KEY', '')
        if not api_key:
            self.stdout.write(
                self.style.ERROR('❌ YOUTUBE_API_KEY manquante dans settings.py')
            )
            return

        self.stdout.write(f'✅ Clé API configurée: {api_key[:10]}...')

        # 2. Tester l'API
        try:
            youtube_service = YouTubeService()

            # Test avec une playlist éducative connue
            playlist_id = 'PLillGF-RfqbYeckUaD1z6nviTp31GLTH8'
            playlist_data = youtube_service.get_playlist_details(playlist_id)

            if playlist_data:
                self.stdout.write('✅ API YouTube fonctionne!')
                self.stdout.write(f'   Playlist trouvée: {playlist_data["title"]}')
                self.stdout.write(f'   Nombre de vidéos: {playlist_data["video_count"]}')
            else:
                self.stdout.write(
                    self.style.ERROR('❌ Impossible de récupérer la playlist de test')
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erreur API: {e}')
            )
            return

        # 3. Vérifier les utilisateurs
        users = User.objects.all()
        if users.exists():
            self.stdout.write(f'✅ {users.count()} utilisateurs trouvés')
            admin_email = users.first().email
        else:
            self.stdout.write('⚠️  Créez un superuser d\'abord!')
            return

        # 4. Exemple de commande
        self.stdout.write('\n🚀 Commande pour importer le cours de test:')
        self.stdout.write(
            f'python manage.py import_youtube_playlist {playlist_id} --instructor-email {admin_email}'
        )

        self.stdout.write('\n✨ Configuration OK! Prêt à importer des cours YouTube!')