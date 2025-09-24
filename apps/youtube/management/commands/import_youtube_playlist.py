# Modifications à apporter dans apps/youtube/management/commands/import_youtube_playlist.py

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.courses.models import Course, Category
from apps.users.models import User
import uuid


class Command(BaseCommand):
    help = 'Import une playlist YouTube en tant que cours'

    def add_arguments(self, parser):
        parser.add_argument('playlist_id', type=str, help='ID de la playlist YouTube')
        parser.add_argument('--instructor-email', required=True, help='Email de l\'instructeur')
        parser.add_argument('--category', help='Slug de la catégorie')
        parser.add_argument('--difficulty', choices=['beginner', 'intermediate', 'advanced'], default='beginner')
        parser.add_argument('--price', type=float, default=0.0)

    def generate_unique_slug(self, title, model_class):
        """Génère un slug unique pour éviter les conflits"""
        base_slug = slugify(title)
        if not base_slug:
            base_slug = f"course-{uuid.uuid4().hex[:8]}"

        slug = base_slug
        counter = 1

        while model_class.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug

    def handle(self, *args, **options):
        playlist_id = options['playlist_id']
        instructor_email = options['instructor_email']
        category_slug = options.get('category', 'dev-web')

        self.stdout.write(f'Import de la playlist YouTube: {playlist_id}')

        # 1. Vérifier que l'instructeur existe
        try:
            instructor = User.objects.get(email=instructor_email)
            self.stdout.write(f'Instructeur trouvé: {instructor.email}')
        except User.DoesNotExist:
            available_emails = list(User.objects.values_list('email', flat=True))
            self.stdout.write(
                self.style.ERROR(f'Instructeur avec email {instructor_email} non trouvé')
            )
            self.stdout.write(f'Emails disponibles: {", ".join(available_emails)}')
            return

        # 2. Récupérer ou créer la catégorie
        try:
            category = Category.objects.get(slug=category_slug)
            self.stdout.write(f'Catégorie existante: {category.name}')
        except Category.DoesNotExist:
            # Utiliser get_or_create pour éviter les contraintes d'unicité
            category, created = Category.objects.get_or_create(
                slug=category_slug,
                defaults={
                    'name': 'Développement Web',
                    'description': 'Cours de développement web'
                }
            )
            if created:
                self.stdout.write(f'Catégorie créée: {category.name}')
            else:
                self.stdout.write(f'Catégorie récupérée: {category.name}')

        # 3. Récupérer les infos de la playlist via l'API YouTube
        # (ici vous devez ajouter votre logique existante pour récupérer les données YouTube)
        try:
            # Votre code existant pour récupérer course_title et autres données
            # course_title = ... (récupéré via l'API YouTube)

            # Pour cet exemple, on utilise un titre par défaut
            course_title = f"Cours importé depuis {playlist_id}"

            # 4. Générer un slug unique pour le cours
            course_slug = self.generate_unique_slug(course_title, Course)

            # 5. Créer le cours avec gestion d'erreur
            course, created = Course.objects.get_or_create(
                slug=course_slug,
                defaults={
                    'title': course_title,
                    'description': f'Cours importé depuis la playlist YouTube {playlist_id}',
                    'instructor': instructor,
                    'category': category,
                    'difficulty': options['difficulty'],
                    'price': options['price'],
                    'youtube_playlist_id': playlist_id,
                    'is_published': True,
                    'is_youtube_synced': False
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f'Cours créé: {course.title} (slug: {course.slug})'))
            else:
                self.stdout.write(f'Cours existant mis à jour: {course.title}')

            # 6. Ici vous ajouteriez la logique pour créer les leçons depuis les vidéos
            # de la playlist

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erreur lors de l\'import: {str(e)}'))
            return

        self.stdout.write(self.style.SUCCESS('Import terminé avec succès!'))