# apps/youtube/management/commands/test_youtube_setup.py

from django.core.management.base import BaseCommand
from apps.users.models import User
from apps.courses.models import Category
from apps.youtube.services import YouTubeService
from django.conf import settings


class Command(BaseCommand):
    help = 'Teste la configuration YouTube sans importer de playlist'

    def handle(self, *args, **options):
        self.stdout.write('🔍 Test de la configuration YouTube...\n')

        # 1. Vérifier la clé API
        api_key = getattr(settings, 'YOUTUBE_API_KEY', '')
        if not api_key:
            self.stdout.write(
                self.style.ERROR('❌ YOUTUBE_API_KEY non configurée')
            )
            self.stdout.write('Ajoutez dans settings.py : YOUTUBE_API_KEY = "votre_cle"')
            return
        else:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Clé API configurée : {api_key[:10]}...')
            )

        # 2. Vérifier les utilisateurs
        users = User.objects.all()
        if not users.exists():
            self.stdout.write(
                self.style.WARNING('⚠️  Aucun utilisateur trouvé')
            )
            self.stdout.write('Créez un superuser : python manage.py createsuperuser')
        else:
            self.stdout.write(
                self.style.SUCCESS(f'✅ {users.count()} utilisateurs trouvés')
            )
            for user in users[:3]:
                self.stdout.write(f'   - {user.email}')

        # 3. Vérifier les catégories
        categories = Category.objects.all()
        if not categories.exists():
            # Créer une catégorie par défaut
            cat = Category.objects.create(
                name='Développement Web',
                slug='dev-web',
                description='Cours de développement web'
            )
            self.stdout.write(
                self.style.SUCCESS(f'✅ Catégorie créée : {cat.name}')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'✅ {categories.count()} catégories trouvées')
            )

        # 4. Tester l'API YouTube
        try:
            youtube_service = YouTubeService()
            # Test simple : récupérer une vidéo connue
            test_video = youtube_service.get_video_details('dQw4w9WgXcQ')  # Never Gonna Give You Up
            if test_video:
                self.stdout.write(
                    self.style.SUCCESS('✅ API YouTube fonctionne')
                )
                self.stdout.write(f'   Test vidéo : {test_video["title"]}')
            else:
                self.stdout.write(
                    self.style.ERROR('❌ Impossible de récupérer la vidéo de test')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erreur API YouTube : {e}')
            )

        # 5. Exemples de commandes
        self.stdout.write('\n💡 Exemples de commandes à utiliser :')

        if users.exists():
            user_email = users.first().email
            self.stdout.write(
                f'python manage.py import_youtube_playlist PLillGF-RfqbYeckUaD1z6nviTp31GLTH8 --instructor-email {user_email}'
            )

        self.stdout.write('\n🎯 Playlists publiques pour tester :')
        test_playlists = [
            ('PLillGF-RfqbYeckUaD1z6nviTp31GLTH8', 'HTML/CSS Crash Course'),
            ('PLsyeobzWxl7poL9JTVyndKe62ieoN-MZ3', 'Python Programming'),
            ('PLDyQo7g0_nsX8_gZAB8KD1lL4j4halQBJ', 'JavaScript Basics'),
        ]

        for playlist_id, description in test_playlists:
            self.stdout.write(f'   {playlist_id} - {description}')

        self.stdout.write('\n✨ Configuration terminée!')