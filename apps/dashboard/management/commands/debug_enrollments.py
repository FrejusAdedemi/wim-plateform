# apps/dashboard/management/commands/debug_enrollments.py

import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model
from apps.enrollments.models import Enrollment
from apps.courses.models import Course, Category
from apps.progress.models import LessonProgress
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    help = 'Debug et diagnostic des inscriptions WIM Platform'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-test-data',
            action='store_true',
            help='Créer des données de test',
        )
        parser.add_argument(
            '--check-enrollments',
            action='store_true',
            help='Vérifier les inscriptions',
        )
        parser.add_argument(
            '--fix-data',
            action='store_true',
            help='Corriger les données incohérentes',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔍 WIM Platform Debug Tool - Enrollments\n')
        )

        if options['create_test_data']:
            self.create_test_data()

        if options['check_enrollments']:
            self.check_enrollments()

        if options['fix_data']:
            self.fix_data()

        if not any(options.values()):
            self.run_full_diagnostic()

    def create_test_data(self):
        """Créer des données de test pour diagnostiquer"""
        self.stdout.write('\n📝 Création de données de test...\n')

        # Vérifier qu'on a des utilisateurs
        users = User.objects.all()
        if not users.exists():
            self.stdout.write(self.style.ERROR('❌ Aucun utilisateur trouvé. Créez d\'abord des utilisateurs.'))
            return

        # Vérifier qu'on a des cours
        courses = Course.objects.filter(is_published=True)
        if not courses.exists():
            self.stdout.write(self.style.ERROR('❌ Aucun cours publié trouvé.'))
            return

        # Créer des inscriptions de test
        test_user = users.first()
        self.stdout.write(f'Utilisateur de test: {test_user.email}')

        # Inscrire l'utilisateur aux 2 premiers cours
        for course in courses[:2]:
            enrollment, created = Enrollment.objects.get_or_create(
                user=test_user,
                course=course,
                defaults={
                    'is_active': True,
                    'progress_percentage': Decimal(str(random.uniform(10, 80))),
                    'total_time_spent': random.randint(300, 3600)
                }
            )

            if created:
                self.stdout.write(f'✅ Inscription créée: {course.title}')
            else:
                self.stdout.write(f'ℹ️ Inscription existe déjà: {course.title}')

    def check_enrollments(self):
        """Vérifier l'état des inscriptions"""
        self.stdout.write('\n📊 Vérification des inscriptions...\n')

        # Statistiques globales
        total_users = User.objects.count()
        total_courses = Course.objects.filter(is_published=True).count()
        total_enrollments = Enrollment.objects.count()
        active_enrollments = Enrollment.objects.filter(is_active=True).count()

        self.stdout.write(f'👥 Utilisateurs: {total_users}')
        self.stdout.write(f'📚 Cours publiés: {total_courses}')
        self.stdout.write(f'📝 Inscriptions totales: {total_enrollments}')
        self.stdout.write(f'✅ Inscriptions actives: {active_enrollments}')

        # Vérifier chaque utilisateur
        self.stdout.write('\n👤 Détail par utilisateur:')
        for user in User.objects.all()[:5]:  # Limiter à 5 pour le debug
            user_enrollments = Enrollment.objects.filter(user=user, is_active=True)
            self.stdout.write(f'  {user.email}: {user_enrollments.count()} cours actifs')

            for enrollment in user_enrollments:
                self.stdout.write(f'    - {enrollment.course.title} ({enrollment.progress_percentage}%)')

    def fix_data(self):
        """Corriger les données incohérentes"""
        self.stdout.write('\n🔧 Correction des données...\n')

        # Recalculer les progressions
        fixed_count = 0
        for enrollment in Enrollment.objects.filter(is_active=True):
            old_progress = enrollment.progress_percentage
            enrollment.calculate_progress()
            if old_progress != enrollment.progress_percentage:
                fixed_count += 1
                self.stdout.write(
                    f'✅ Progression corrigée pour {enrollment.course.title}: {old_progress}% → {enrollment.progress_percentage}%')

        if fixed_count == 0:
            self.stdout.write('ℹ️ Aucune correction nécessaire')
        else:
            self.stdout.write(f'✅ {fixed_count} progressions corrigées')

    def run_full_diagnostic(self):
        """Diagnostic complet"""
        self.stdout.write('\n🔍 Diagnostic complet...\n')

        # 1. Vérifier les modèles de base
        self.check_base_models()

        # 2. Vérifier les inscriptions
        self.check_enrollments()

        # 3. Vérifier les URLs
        self.check_urls()

        # 4. Recommandations
        self.show_recommendations()

    def check_base_models(self):
        """Vérifier les modèles de base"""
        self.stdout.write('\n📋 Vérification des modèles de base...\n')

        # Utilisateurs
        users_count = User.objects.count()
        self.stdout.write(f'👥 Utilisateurs: {users_count}')
        if users_count == 0:
            self.stdout.write(self.style.WARNING('⚠️ Aucun utilisateur trouvé'))

        # Catégories
        categories_count = Category.objects.filter(is_active=True).count()
        self.stdout.write(f'📂 Catégories actives: {categories_count}')

        # Cours
        courses_count = Course.objects.filter(is_published=True).count()
        self.stdout.write(f'📚 Cours publiés: {courses_count}')
        if courses_count == 0:
            self.stdout.write(self.style.WARNING('⚠️ Aucun cours publié trouvé'))

        # Modules et leçons
        from apps.courses.models import Module, Lesson
        modules_count = Module.objects.filter(is_published=True).count()
        lessons_count = Lesson.objects.filter(is_published=True).count()
        self.stdout.write(f'📖 Modules publiés: {modules_count}')
        self.stdout.write(f'📝 Leçons publiées: {lessons_count}')

    def check_urls(self):
        """Vérifier les URLs importantes"""
        self.stdout.write('\n🔗 Vérification des URLs...\n')

        from django.urls import reverse

        urls_to_check = [
            ('dashboard:index', 'Tableau de bord'),
            ('courses:list', 'Liste des cours'),
            ('enrollments:my-courses', 'Mes cours'),
            ('authentication:login', 'Connexion'),
        ]

        for url_name, description in urls_to_check:
            try:
                url = reverse(url_name)
                self.stdout.write(f'✅ {description}: {url}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ {description}: {e}'))

    def show_recommendations(self):
        """Afficher les recommandations"""
        self.stdout.write('\n💡 Recommandations...\n')

        # Vérifier s'il y a des inscriptions
        enrollments_count = Enrollment.objects.filter(is_active=True).count()
        if enrollments_count == 0:
            self.stdout.write('📝 Aucune inscription trouvée. Actions recommandées:')
            self.stdout.write('   1. Créer des données de test: python manage.py debug_enrollments --create-test-data')
            self.stdout.write('   2. Ou utiliser: python manage.py populate_db')

        # Vérifier les cours sans modules
        courses_without_modules = Course.objects.filter(
            is_published=True,
            modules__isnull=True
        ).distinct()

        if courses_without_modules.exists():
            self.stdout.write(f'⚠️ {courses_without_modules.count()} cours sans modules:')
            for course in courses_without_modules[:3]:
                self.stdout.write(f'   - {course.title}')

        self.stdout.write('\n🎯 Actions recommandées:')
        self.stdout.write('1. Vérifiez que les templates existent')
        self.stdout.write('2. Vérifiez les relations entre modèles')
        self.stdout.write('3. Créez des données de test si nécessaire')
        self.stdout.write('4. Vérifiez les permissions des URLs')


import random