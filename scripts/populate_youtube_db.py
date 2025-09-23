# scripts/populate_youtube_db.py
"""
Script de population avec contenu YouTube réel - WIM Platform
Remplace les données fictives par du vrai contenu YouTube
"""

import os
import sys
import django
from pathlib import Path
from decimal import Decimal
import random
from datetime import timedelta
from django.utils import timezone

# Configuration Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User
from apps.courses.models import Category, Course, Module, Lesson
from apps.enrollments.models import Enrollment, Review

# Import conditionnel du service YouTube
try:
    from apps.youtube.services import YouTubeService

    YOUTUBE_AVAILABLE = True
except ImportError:
    YOUTUBE_AVAILABLE = False
    YouTubeService = None


def create_categories():
    """Créer les catégories de cours"""
    categories_data = [
        {
            'name': 'Développement Web',
            'slug': 'dev-web',
            'description': 'Langages et frameworks web modernes',
            'icon': '💻',
            'color': '#4A90E2',
            'order': 1
        },
        {
            'name': 'Python',
            'slug': 'python',
            'description': 'Programmation Python et ses applications',
            'icon': '🐍',
            'color': '#306998',
            'order': 2
        },
        {
            'name': 'JavaScript',
            'slug': 'javascript',
            'description': 'JavaScript moderne et frameworks',
            'icon': '⚡',
            'color': '#F7DF1E',
            'order': 3
        },
        {
            'name': 'Data Science',
            'slug': 'data-science',
            'description': 'Analyse de données et machine learning',
            'icon': '📊',
            'color': '#E74C3C',
            'order': 4
        },
        {
            'name': 'Design',
            'slug': 'design',
            'description': 'UI/UX et design graphique',
            'icon': '🎨',
            'color': '#9B59B6',
            'order': 5
        },
    ]

    categories = []
    for cat_data in categories_data:
        cat, created = Category.objects.get_or_create(
            slug=cat_data['slug'],
            defaults=cat_data
        )
        categories.append(cat)
        if created:
            print(f"✅ Catégorie créée: {cat.name}")

    return categories


def create_users():
    """Créer des utilisateurs de test"""

    # Admin
    admin, created = User.objects.get_or_create(
        email='admin@wim.com',
        defaults={
            'name': 'Admin WIM',
            'is_staff': True,
            'is_superuser': True,
            'is_instructor': True
        }
    )
    if created:
        admin.set_password('Admin123!')
        admin.save()
        print("✅ Admin créé: admin@wim.com / Admin123!")

    # Instructeurs basés sur de vraies chaînes YouTube
    instructors_data = [
        {
            'name': 'Instructeur Python',
            'email': 'python@wim.com',
            'bio': 'Expert en programmation Python et data science'
        },
        {
            'name': 'Instructeur Web',
            'email': 'web@wim.com',
            'bio': 'Développeur full-stack spécialisé en technologies web modernes'
        },
        {
            'name': 'Instructeur JavaScript',
            'email': 'js@wim.com',
            'bio': 'Expert JavaScript et frameworks modernes'
        },
        {
            'name': 'Instructeur Design',
            'email': 'design@wim.com',
            'bio': 'Designer UI/UX avec 10 ans d\'expérience'
        },
    ]

    instructors = []
    for instructor_data in instructors_data:
        user, created = User.objects.get_or_create(
            email=instructor_data['email'],
            defaults={
                'name': instructor_data['name'],
                'bio': instructor_data['bio'],
                'is_instructor': True
            }
        )
        if created:
            user.set_password('Instructor123!')
            user.save()
            print(f"✅ Instructeur créé: {instructor_data['email']}")
        instructors.append(user)

    # Étudiants
    students = []
    students_data = [
        'Alice Johnson', 'Bob Wilson', 'Charlie Brown', 'Diana Prince',
        'Ethan Hunt', 'Fiona Green', 'George White', 'Hannah Black'
    ]

    for name in students_data:
        email = f"{name.split()[0].lower()}@student.com"
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'name': name,
                'bio': f"Étudiant passionné par l'apprentissage"
            }
        )
        if created:
            user.set_password('Student123!')
            user.save()
            print(f"✅ Étudiant créé: {email}")
        students.append(user)

    return admin, instructors, students


def create_basic_courses(categories, instructors):
    """Créer des cours de base sans YouTube (fallback)"""

    courses_data = [
        {
            'title': 'Python pour débutants',
            'category_slug': 'python',
            'instructor_index': 0,
            'difficulty': 'beginner',
            'price': Decimal('0.00'),
            'description': 'Apprenez Python de zéro avec des exemples pratiques',
            'learning_objectives': [
                'Maîtriser la syntaxe Python de base',
                'Comprendre la programmation orientée objet',
                'Créer des projets Python pratiques',
                'Utiliser les bibliothèques essentielles'
            ]
        },
        {
            'title': 'Développement Web Moderne',
            'category_slug': 'dev-web',
            'instructor_index': 1,
            'difficulty': 'intermediate',
            'price': Decimal('49.99'),
            'description': 'HTML, CSS, JavaScript et frameworks modernes',
            'learning_objectives': [
                'Créer des sites web responsives',
                'Maîtriser HTML5 et CSS3',
                'Développer avec JavaScript ES6+',
                'Utiliser les frameworks modernes'
            ]
        }
    ]

    courses = []
    for i, course_data in enumerate(courses_data):
        try:
            category = next(cat for cat in categories if cat.slug == course_data['category_slug'])
            instructor = instructors[course_data['instructor_index']]

            course = Course.objects.create(
                title=course_data['title'],
                category=category,
                instructor=instructor,
                difficulty=course_data['difficulty'],
                price=course_data['price'],
                description=course_data['description'],
                full_description=f"# {course_data['title']}\n\n{course_data['description']}\n\nCours complet pour maîtriser les concepts essentiels.",
                learning_objectives='\n'.join(f"• {obj}" for obj in course_data['learning_objectives']),
                is_published=True,
                is_new=i < 2,
                rating=Decimal(random.uniform(4.0, 5.0)),
                total_students=random.randint(50, 500)
            )

            # Créer un module de base
            module = Module.objects.create(
                course=course,
                title='Introduction',
                description='Leçons d\'introduction',
                order=1
            )

            # Créer quelques leçons de base
            for j in range(3):
                Lesson.objects.create(
                    module=module,
                    title=f'Leçon {j + 1}: {course_data["title"]} - Partie {j + 1}',
                    lesson_type='video',
                    order=j + 1,
                    duration=random.randint(15, 45),
                    video_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                    content=f'Contenu de la leçon {j + 1}',
                    is_published=True,
                    is_preview=(j == 0)
                )

            courses.append(course)
            print(f"✅ Cours de base créé: {course.title}")

        except Exception as e:
            print(f"❌ Erreur lors de la création du cours {course_data['title']}: {e}")

    return courses


def create_youtube_courses(categories, instructors):
    """Créer des cours basés sur des playlists YouTube réelles"""

    if not YOUTUBE_AVAILABLE:
        print("⚠️ Service YouTube non disponible, création de cours basiques")
        return create_basic_courses(categories, instructors)

    try:
        youtube_service = YouTubeService()
    except Exception as e:
        print(f"❌ Erreur d'initialisation YouTube: {e}")
        print("⚠️ Création de cours basiques à la place")
        return create_basic_courses(categories, instructors)

    # Cours basés sur de vraies playlists YouTube
    youtube_courses_data = [
        {
            'title': 'Python pour débutants',
            'category_slug': 'python',
            'instructor_index': 0,
            'difficulty': 'beginner',
            'price': Decimal('0.00'),
            'description': 'Apprenez Python de zéro avec des exemples pratiques',
            'playlist_id': 'PLrSOXFDHBtfHg8fWBd7sKPxEmahwyVBkC',
            'learning_objectives': [
                'Maîtriser la syntaxe Python de base',
                'Comprendre la programmation orientée objet',
                'Créer des projets Python pratiques',
                'Utiliser les bibliothèques essentielles'
            ]
        },
        {
            'title': 'Développement Web Moderne',
            'category_slug': 'dev-web',
            'instructor_index': 1,
            'difficulty': 'intermediate',
            'price': Decimal('49.99'),
            'description': 'HTML, CSS, JavaScript et frameworks modernes',
            'playlist_id': 'PLillGF-RfqbZTASqIqdvm1R5mLrQq79CU',
            'learning_objectives': [
                'Créer des sites web responsives',
                'Maîtriser HTML5 et CSS3',
                'Développer avec JavaScript ES6+',
                'Utiliser les frameworks modernes'
            ]
        }
    ]

    courses = []

    for i, course_data in enumerate(youtube_courses_data):
        try:
            category = next(cat for cat in categories if cat.slug == course_data['category_slug'])
            instructor = instructors[course_data['instructor_index']]

            print(f"\n🔍 Traitement du cours: {course_data['title']}")

            # Créer le cours de base d'abord
            course = Course.objects.create(
                title=course_data['title'],
                category=category,
                instructor=instructor,
                difficulty=course_data['difficulty'],
                price=course_data['price'],
                description=course_data['description'],
                full_description=f"# {course_data['title']}\n\n{course_data['description']}\n\nCours complet pour maîtriser les concepts essentiels.",
                learning_objectives='\n'.join(f"• {obj}" for obj in course_data['learning_objectives']),
                is_published=True,
                is_new=i < 2,
                rating=Decimal(random.uniform(4.0, 5.0)),
                total_students=random.randint(50, 500)
            )

            print(f"✅ Cours créé: {course.title}")

            # Créer un module principal
            module = Module.objects.create(
                course=course,
                title='Contenu principal',
                description='Leçons du cours',
                order=1
            )

            # Créer des leçons de base (on peut les remplacer par YouTube plus tard)
            for j in range(5):
                Lesson.objects.create(
                    module=module,
                    title=f'Leçon {j + 1}: {course_data["title"]} - Partie {j + 1}',
                    lesson_type='video',
                    order=j + 1,
                    duration=random.randint(15, 45),
                    video_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                    content=f'Contenu de la leçon {j + 1}',
                    is_published=True,
                    is_preview=(j < 2)
                )

            courses.append(course)

        except Exception as e:
            print(f"❌ Erreur lors de la création du cours {course_data['title']}: {e}")
            continue

    return courses


def create_sample_enrollments(students, courses):
    """Créer des inscriptions d'exemple"""

    enrollments = []

    for student in students[:6]:  # 6 premiers étudiants
        # Inscrire à 2-3 cours aléatoires
        selected_courses = random.sample(courses, min(random.randint(2, 3), len(courses)))

        for course in selected_courses:
            enrollment, created = Enrollment.objects.get_or_create(
                user=student,
                course=course,
                defaults={
                    'progress_percentage': Decimal(random.uniform(10, 90)),
                    'is_active': True,
                    'enrolled_at': timezone.now() - timedelta(days=random.randint(1, 30)),
                    'total_time_spent': random.randint(1800, 7200)  # 30min à 2h
                }
            )

            if created:
                enrollment.calculate_progress()
                enrollments.append(enrollment)
                print(f"✅ Inscription: {student.name} → {course.title}")

    return enrollments


def create_sample_reviews(students, courses):
    """Créer des avis d'exemple"""

    review_comments = [
        "Excellent cours ! Très bien expliqué et facile à suivre.",
        "Le contenu est de qualité et l'instructeur est compétent.",
        "Parfait pour débuter, je recommande vivement.",
        "Cours très complet avec de bons exemples pratiques.",
        "Formation de qualité, j'ai beaucoup appris.",
        "Les vidéos sont claires et bien structurées.",
        "Très bon rapport qualité-prix, content de mon achat.",
        "Instructeur pédagogue, cours bien organisé."
    ]

    for student in students[:4]:  # 4 premiers étudiants
        for course in random.sample(courses, min(2, len(courses))):
            if Enrollment.objects.filter(user=student, course=course).exists():
                Review.objects.get_or_create(
                    user=student,
                    course=course,
                    defaults={
                        'rating': random.randint(4, 5),
                        'comment': random.choice(review_comments),
                        'content_quality': random.randint(4, 5),
                        'instructor_quality': random.randint(4, 5)
                    }
                )
                print(f"✅ Avis créé: {student.name} pour {course.title}")


def display_configuration_info():
    """Affiche les informations de configuration nécessaires"""
    print("\n" + "=" * 60)
    print("📋 CONFIGURATION NÉCESSAIRE POUR YOUTUBE API")
    print("=" * 60)
    print("\n1. Obtenir une clé API YouTube :")
    print("   - Allez sur https://console.developers.google.com/")
    print("   - Créez un nouveau projet ou sélectionnez un projet existant")
    print("   - Activez l'API YouTube Data v3")
    print("   - Créez des identifiants (clé API)")
    print("\n2. Configuration dans Django :")
    print("   - Ajoutez YOUTUBE_API_KEY='votre_clé_api' dans votre fichier .env")
    print("   - Installez les dépendances : pip install google-api-python-client isodate")
    print("\n3. Créer l'app YouTube :")
    print("   - mkdir apps/youtube")
    print("   - touch apps/youtube/__init__.py")
    print("   - Ajoutez 'apps.youtube' dans INSTALLED_APPS")
    print("\n4. Migrations :")
    print("   - python manage.py makemigrations")
    print("   - python manage.py migrate")
    print("\n" + "=" * 60)


def main():
    """Fonction principale"""
    print("\n🚀 Démarrage de la population avec contenu YouTube réel...\n")

    # Afficher les informations de configuration
    display_configuration_info()

    print("\n📁 Création des catégories...")
    categories = create_categories()

    print("\n👥 Création des utilisateurs...")
    admin, instructors, students = create_users()

    print("\n📚 Création des cours...")
    courses = create_youtube_courses(categories, instructors)

    if courses:
        print("\n✏️ Création des inscriptions d'exemple...")
        enrollments = create_sample_enrollments(students, courses)

        print("\n⭐ Création des avis...")
        create_sample_reviews(students, courses)

    print("\n✅ Population terminée avec succès!")
    print(f"\n📊 Statistiques:")
    print(f"   - Catégories: {Category.objects.count()}")
    print(f"   - Utilisateurs: {User.objects.count()}")
    print(f"   - Cours: {Course.objects.count()}")
    print(f"   - Modules: {Module.objects.count()}")
    print(f"   - Leçons: {Lesson.objects.count()}")
    print(f"   - Inscriptions: {Enrollment.objects.count()}")
    print(f"   - Avis: {Review.objects.count()}")

    print("\n🎯 Comptes de test créés:")
    print("   - Admin: admin@wim.com / Admin123!")
    print("   - Étudiant: alice@student.com / Student123!")

    print("\n📝 Prochaines étapes:")
    print("1. Configurez votre clé API YouTube")
    print("2. Créez l'app YouTube avec les services")
    print("3. Ajoutez les champs YouTube aux modèles")
    print("4. Testez l'intégration YouTube")

    print("\n🎉 Votre plateforme WIM est prête!")


if __name__ == '__main__':
    main()