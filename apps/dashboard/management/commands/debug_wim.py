# apps/dashboard/management/commands/debug_wim.py

import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.urls import reverse
from django.test import RequestFactory
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Debug WIM Platform issues'

    def add_arguments(self, parser):
        parser.add_argument(
            '--check-urls',
            action='store_true',
            help='Check URL configuration',
        )
        parser.add_argument(
            '--check-media',
            action='store_true',
            help='Check media configuration',
        )
        parser.add_argument(
            '--check-templates',
            action='store_true',
            help='Check templates',
        )
        parser.add_argument(
            '--fix-permissions',
            action='store_true',
            help='Fix file permissions',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔍 WIM Platform Debug Tool\n')
        )

        if options['check_urls']:
            self.check_urls()

        if options['check_media']:
            self.check_media()

        if options['check_templates']:
            self.check_templates()

        if options['fix_permissions']:
            self.fix_permissions()

        if not any(options.values()):
            self.run_all_checks()

    def check_urls(self):
        """Vérifier la configuration des URLs"""
        self.stdout.write('\n📍 Vérification des URLs...\n')

        urls_to_check = [
            ('authentication:login', {}),
            ('authentication:register', {}),
            ('authentication:password_reset', {}),
            ('authentication:password_reset_done', {}),
            ('dashboard:index', {}),
            ('courses:list', {}),
        ]

        for url_name, kwargs in urls_to_check:
            try:
                url = reverse(url_name, kwargs=kwargs)
                self.stdout.write(
                    self.style.SUCCESS(f'✅ {url_name}: {url}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ {url_name}: {e}')
                )

    def check_media(self):
        """Vérifier la configuration des médias"""
        self.stdout.write('\n📁 Vérification des médias...\n')

        # Vérifier MEDIA_ROOT
        media_root = getattr(settings, 'MEDIA_ROOT', None)
        if media_root:
            if os.path.exists(media_root):
                self.stdout.write(
                    self.style.SUCCESS(f'✅ MEDIA_ROOT existe: {media_root}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️ MEDIA_ROOT n\'existe pas: {media_root}')
                )
                # Créer le dossier
                os.makedirs(media_root, exist_ok=True)
                self.stdout.write(
                    self.style.SUCCESS(f'✅ MEDIA_ROOT créé: {media_root}')
                )
        else:
            self.stdout.write(
                self.style.ERROR('❌ MEDIA_ROOT non configuré')
            )

        # Vérifier MEDIA_URL
        media_url = getattr(settings, 'MEDIA_URL', None)
        if media_url:
            self.stdout.write(
                self.style.SUCCESS(f'✅ MEDIA_URL: {media_url}')
            )
        else:
            self.stdout.write(
                self.style.ERROR('❌ MEDIA_URL non configuré')
            )

        # Créer les dossiers de médias nécessaires
        media_folders = [
            'avatars',
            'course_images',
            'certificates',
            'certificate_templates',
            'certificate_backgrounds'
        ]

        for folder in media_folders:
            folder_path = os.path.join(media_root, folder)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path, exist_ok=True)
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Dossier créé: {folder}')
                )

    def check_templates(self):
        """Vérifier les templates"""
        self.stdout.write('\n📄 Vérification des templates...\n')

        template_dirs = settings.TEMPLATES[0]['DIRS']
        for template_dir in template_dirs:
            if os.path.exists(template_dir):
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Template dir existe: {template_dir}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ Template dir manquant: {template_dir}')
                )

        # Vérifier des templates clés
        key_templates = [
            'base.html',
            'authentication/login.html',
            'authentication/password_reset.html',
            'dashboard/index.html',
        ]

        base_template_dir = template_dirs[0] if template_dirs else None
        if base_template_dir:
            for template in key_templates:
                template_path = os.path.join(base_template_dir, template)
                if os.path.exists(template_path):
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Template existe: {template}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️ Template manquant: {template}')
                    )

    def fix_permissions(self):
        """Corriger les permissions des fichiers"""
        self.stdout.write('\n🔧 Correction des permissions...\n')

        # Corriger les permissions du dossier media
        media_root = getattr(settings, 'MEDIA_ROOT', None)
        if media_root and os.path.exists(media_root):
            try:
                os.chmod(media_root, 0o755)
                for root, dirs, files in os.walk(media_root):
                    for d in dirs:
                        os.chmod(os.path.join(root, d), 0o755)
                    for f in files:
                        os.chmod(os.path.join(root, f), 0o644)
                self.stdout.write(
                    self.style.SUCCESS('✅ Permissions média corrigées')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Erreur permissions: {e}')
                )

    def run_all_checks(self):
        """Exécuter toutes les vérifications"""
        self.check_urls()
        self.check_media()
        self.check_templates()

        # Informations système
        self.stdout.write('\n💻 Informations système...\n')
        self.stdout.write(f'DEBUG: {settings.DEBUG}')
        self.stdout.write(f'ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}')
        self.stdout.write(f'SECRET_KEY: {"✅ Configuré" if settings.SECRET_KEY else "❌ Manquant"}')

        # Vérifications de base de données
        self.stdout.write('\n🗄️ Base de données...\n')
        try:
            user_count = User.objects.count()
            self.stdout.write(
                self.style.SUCCESS(f'✅ Connexion DB OK - {user_count} utilisateurs')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erreur DB: {e}')
            )

        # Recommandations
        self.stdout.write(self.style.SUCCESS('\n🎯 Actions recommandées:'))
        self.stdout.write('1. Vérifiez que tous les templates existent')
        self.stdout.write('2. Configurez EMAIL_BACKEND pour les mots de passe')
        self.stdout.write('3. Créez des données de test avec: python manage.py populate_db')
        self.stdout.write('4. Collectez les fichiers statiques: python manage.py collectstatic')
        self.stdout.write('\n✨ WIM Platform Debug terminé!')