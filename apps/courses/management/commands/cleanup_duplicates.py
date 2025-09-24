from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.courses.models import Course, Category


class Command(BaseCommand):
    help = 'Nettoie les doublons et corrige les slugs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Affiche ce qui serait fait sans l\'exécuter',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('Mode dry-run activé - aucune modification ne sera effectuée'))

        self.stdout.write('Analyse des doublons...')

        # 1. Analyser les catégories en doublon
        categories_by_slug = {}
        for category in Category.objects.all():
            if category.slug in categories_by_slug:
                categories_by_slug[category.slug].append(category)
            else:
                categories_by_slug[category.slug] = [category]

        for slug, categories in categories_by_slug.items():
            if len(categories) > 1:
                self.stdout.write(f'Catégorie doublon trouvée: {slug} ({len(categories)} occurrences)')
                # Garder la première, supprimer les autres
                for category in categories[1:]:
                    if not dry_run:
                        category.delete()
                    self.stdout.write(f'  - Supprimé: {category.name} (ID: {category.id})')

        # 2. Analyser les cours en doublon
        courses_by_slug = {}
        for course in Course.objects.all():
            if course.slug in courses_by_slug:
                courses_by_slug[course.slug].append(course)
            else:
                courses_by_slug[course.slug] = [course]

        for slug, courses in courses_by_slug.items():
            if len(courses) > 1:
                self.stdout.write(f'Cours doublon trouvé: {slug} ({len(courses)} occurrences)')
                # Renommer les doublons
                for i, course in enumerate(courses[1:], 1):
                    base_slug = slugify(course.title)
                    new_slug = f"{base_slug}-{i}"

                    # S'assurer que le nouveau slug est unique
                    counter = i
                    while Course.objects.filter(slug=new_slug).exists():
                        counter += 1
                        new_slug = f"{base_slug}-{counter}"

                    if not dry_run:
                        course.slug = new_slug
                        course.save()

                    self.stdout.write(f'  - Renommé: {course.title} -> slug: {new_slug}')

        if dry_run:
            self.stdout.write(
                self.style.SUCCESS('Analyse terminée! Utilisez sans --dry-run pour appliquer les modifications.'))
        else:
            self.stdout.write(self.style.SUCCESS('Nettoyage terminé!'))