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
from apps.youtube.services import YouTubeService


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


def create_youtube_courses(categories, instructors):
    """Créer des cours basés sur des playlists YouTube réelles"""

    youtube_service = YouTubeService()

    # Cours basés sur de vraies playlists YouTube
    youtube_courses_data = [
        {
            'title': 'Python pour débutants',
            'category_slug': 'python',
            'instructor_index': 0,
            'difficulty': 'beginner',
            'price': Decimal('0.00'),
            'description': 'Apprenez Python de zéro avec des exemples pratiques',
            'playlist_id': 'PLrSOXFDHBtfHg8fWBd7sKPxEmahwyVBkC',  # Exemple de playlist Python
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
            'playlist_id': 'PLillGF-RfqbZTASqIqdvm1R5mLrQq79CU',  # Exemple web dev
            'learning_objectives': [
                'Créer des sites web responsives',
                'Maîtriser HTML5 et CSS3',
                'Développer avec JavaScript ES6+',
                'Utiliser les frameworks modernes'
            ]
        },
        {
            'title': 'JavaScript Avancé',
            'category_slug': 'javascript',
            'instructor_index': 2,
            'difficulty': 'advanced',
            'price': Decimal('69.99'),
            'description': 'Concepts avancés de JavaScript et programmation asynchrone',
            'playlist_id': 'PLWKjhJtqVAbnZtkAI25U6GfnKklJNJn3p',  # Exemple JS avancé
            'learning_objectives': [
                'Maîtriser la programmation asynchrone',
                'Comprendre les closures et prototypes',
                'Utiliser les design patterns',
                'Optimiser les performances'
            ]
        },
        {
            'title': 'Data Science avec Python',
            'category_slug': 'data-science',
            'instructor_index': 0,
            'difficulty': 'intermediate',
            'price': Decimal('89.99'),
            'description': 'Analyse de données, visualisation et machine learning',
            'playlist_id': 'PLeo1K3hjS3us_ELKYSj_Fth2tIEkdKXvV',  # Exemple Data Science
            'learning_objectives': [
                'Analyser des données avec Pandas',
                'Créer des visualisations',
                'Implémenter des algorithmes ML',
                'Utiliser Jupyter Notebooks'
            ]
        },
        {
            'title': 'Design UI/UX Moderne',
            'category_slug': 'design',
            'instructor_index': 3,
            'difficulty': 'beginner',
            'price': Decimal('39.99'),
            'description': 'Principes de design et création d\'interfaces',
            'playlist_id': 'PLDtHAiqIa4wa5MBbE5ak9QBPdWpbGgQJQ',  # Exemple Design
            'learning_objectives': [
                'Comprendre les principes UX',
                'Créer des maquettes efficaces',
                'Utiliser les outils de design',
                'Appliquer la théorie des couleurs'
            ]
        }
    ]

    courses = []

    for i, course_data in enumerate(youtube_courses_data):
        try:
            category = next(cat for cat in categories if cat.slug == course_data['category_slug'])
            instructor = instructors[course_data['instructor_index']]

            print(f"\n🔍 Traitement du cours: {course_data['title']}")
            print(f"   Playlist ID: {course_data['playlist_id']}")

            # Vérifier si la playlist existe et récupérer ses métadonnées
            playlist_data = youtube_service.get_playlist_details(course_data['playlist_id'])

            if not playlist_data:
                print(f"⚠️ Playlist {course_data['playlist_id']} non trouvée, utilisation de données par défaut")
                # Créer un cours avec des données par défaut
                course = Course.objects.create(
                    title=course_data['title'],
                    category=category,
                    instructor=instructor,
                    difficulty=course_data['difficulty'],
                    price=course_data['price'],
                    description=course_data['description'],
                    full_description=f"# {course_data['title']}\n\n{course_data['description']}\n\nCours complet pour maîtriser les concepts essentiels.",
                    learning_objectives='\n'.join(f"• {obj}" for obj in course_data['learning_objectives']),
                    youtube_playlist_id=course_data['playlist_id'],
                    is_published=True,
                    is_new=i < 2,
                    rating=Decimal(random.uniform(4.0, 5.0))
                )
                courses.append(course)
                continue

            # Récupérer les vidéos de la playlist
            videos = youtube_service.get_playlist_videos(course_data['playlist_id'], max_results=20)

            if not videos:
                print(f"⚠️ Aucune vidéo trouvée dans la playlist")
                continue

            # Créer le cours avec les métadonnées YouTube
            course = Course.objects.create(
                title=course_data['title'],
                category=category,
                instructor=instructor,
                difficulty=course_data['difficulty'],
                price=course_data['price'],
                description=course_data['description'],
                full_description=playlist_data.get('description', course_data['description']),
                learning_objectives='\n'.join(f"• {obj}" for obj in course_data['learning_objectives']),
                youtube_playlist_id=course_data['playlist_id'],
                youtube_channel_name=playlist_data.get('channel_name', ''),
                youtube_thumbnail_url=playlist_data.get('thumbnail_url', ''),
                is_published=True,
                is_new=i < 2,
                is_youtube_synced=True,
                last_youtube_sync=timezone.now(),
                rating=Decimal(random.uniform(4.0, 5.0)),
                total_students=random.randint(50, 500)
            )

            print(f"✅ Cours créé: {course.title}")
            print(f"   - {len(videos)} vidéos trouvées")
            print(f"   - Chaîne: {playlist_data.get('channel_name', 'N/A')}")

            # Créer un module principal
            module = Module.objects.create(
                course=course,
                title='Contenu principal',
                description='Leçons importées depuis YouTube',
                order=1
            )

            # Créer les leçons basées sur les vidéos YouTube
            total_duration = 0
            for j, video in enumerate(videos[:15]):  # Limiter à 15 vidéos max
                lesson = Lesson.objects.create(
                    module=module,
                    title=video['title'][:200],
                    lesson_type='video',
                    order=j + 1,
                    youtube_video_id=video['id'],
                    youtube_title=video['title'],
                    youtube_description=video['description'][:1000] if video['description'] else '',
                    youtube_thumbnail_url=video['thumbnail_url'],
                    youtube_duration_seconds=video['duration_seconds'],
                    youtube_view_count=video['view_count'],
                    youtube_published_at=video['published_at'],
                    duration=max(1, video['duration_seconds'] // 60),
                    video_url=f"https://www.youtube.com/watch?v={video['id']}",
                    content=f"Cette leçon couvre: {video['title']}",
                    is_published=True,
                    is_preview=(j < 2)  # Les 2 premières leçons en aperçu
                )
                total_duration += lesson.duration

                print(f"   ✓ Leçon {j+1}: {lesson.title[:50]}...")

            # Mettre à jour la durée du cours
            course.duration = total_duration
            course.save()

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
    review_comments = [
        "Excellent cours ! Très bien expliqué et facile à suivre.",
        "Le contenu est de qualité et l'instructeur est compétent.",
        "Parfait pour débuter, je recommande vivement.",
        "Cours très complet avec de bons exemples pratiques.",
        "Formation de qualité, j'ai beaucoup appris.",
        "Les vidéos sont claires et bien structurées.",
        "Très bon rapport qualité-prix, content de mon achat.",
        "Instructeur pédagogue, cours bien organisé."
    ];

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
                );
                print(f"✅ Avis créé: {student.name} pour {course.title}")


def display_configuration_info():
    """Affiche les informations de configuration nécessaires"""
    print("\n" + "="*60)
    print("📋 CONFIGURATION NÉCESSAIRE POUR YOUTUBE API")
    print("="*60)
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
    print("\n5. Cache (optionnel mais recommandé) :")
    print("   - python manage.py createcachetable youtube_cache_table")
    print("\n" + "="*60)


def main():
    """Fonction principale"""
    print("\n🚀 Démarrage de la population avec contenu YouTube réel...\n")

    # Afficher les informations de configuration
    display_configuration_info()

    # Vérifier si la clé API YouTube est configurée
    try:
        youtube_service = YouTubeService()
        print("✅ Service YouTube initialisé avec succès")
    except Exception as e:
        print(f"❌ Erreur d'initialisation YouTube API: {e}")
        print("\n⚠️  Veuillez configurer votre clé API YouTube avant de continuer.")
        print("   Vous pouvez continuer sans YouTube pour créer la structure de base.")

        response = input("\nContinuer sans YouTube API ? (y/N): ")
        if response.lower() != 'y':
            print("Configuration requise. Arrêt du script.")
            return

    print("\n📁 Création des catégories...")
    categories = create_categories()

    print("\n👥 Création des utilisateurs...")
    admin, instructors, students = create_users()

    print("\n📚 Création des cours avec contenu YouTube...")
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

    print("\n🎯 Prochaines étapes:")
    print("1. Configurez votre clé API YouTube si ce n'est pas fait")
    print("2. Utilisez les commandes de gestion YouTube :")
    print("   - python manage.py sync_youtube_content")
    print("   - python manage.py import_youtube_playlist <playlist_id> --instructor-email admin@wim.com")
    print("   - python manage.py update_video_metadata")
    print("\n3. Testez votre plateforme :")
    print("   - Admin: admin@wim.com / Admin123!")
    print("   - Étudiant: alice@student.com / Student123!")
    print("\n🎉 Votre plateforme WIM est prête avec du contenu YouTube authentique!")


if __name__ == '__main__':
    main()