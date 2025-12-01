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
from datetime import datetime, timedelta

# Configuration du chemin Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.courses.models import Course, Module, Lesson, Category
from apps.enrollments.models import Enrollment, Review

User = get_user_model()

# Importer le service YouTube
try:
    from apps.youtube.services import YouTubeService

    YOUTUBE_AVAILABLE = True
except ImportError:
    YOUTUBE_AVAILABLE = False
    print("⚠️ Service YouTube non disponible")


def show_configuration_info():
    """Afficher les informations de configuration"""
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
    print("\n" + "=" * 60 + "\n")


def create_categories():
    """Créer les catégories de cours"""
    print("📁 Création des catégories...")

    categories_data = [
        {'name': 'Développement Web', 'slug': 'dev-web', 'description': 'HTML, CSS, JavaScript et frameworks web'},
        {'name': 'Python', 'slug': 'python', 'description': 'Programmation Python de A à Z'},
        {'name': 'JavaScript', 'slug': 'javascript', 'description': 'JavaScript moderne et frameworks'},
        {'name': 'Data Science', 'slug': 'data-science', 'description': 'Analyse de données et Machine Learning'},
        {'name': 'Design', 'slug': 'design', 'description': 'UI/UX Design et graphisme'},
    ]

    categories = []
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            slug=cat_data['slug'],
            defaults={
                'name': cat_data['name'],
                'description': cat_data['description']
            }
        )
        categories.append(category)

    return categories


def create_users():
    """Créer des utilisateurs de test"""
    print("\n👥 Création des utilisateurs...")

    # Admin
    admin, created = User.objects.get_or_create(
        email='admin@wim.com',
        defaults={
            'name': 'Admin WIM',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin.set_password('Admin123!')
        admin.save()

    # Instructeurs
    instructors_data = [
        {'email': 'instructor.web@wim.com', 'name': 'Instructeur Web', 'bio': 'Expert en développement web'},
        {'email': 'instructor.python@wim.com', 'name': 'Instructeur Python',
         'bio': 'Spécialiste Python et Data Science'},
        {'email': 'instructor.js@wim.com', 'name': 'Instructeur JavaScript',
         'bio': 'Expert JavaScript et frameworks modernes'},
        {'email': 'instructor.design@wim.com', 'name': 'Instructeur Design', 'bio': 'Designer UI/UX professionnel'},
    ]

    instructors = []
    for inst_data in instructors_data:
        instructor, created = User.objects.get_or_create(
            email=inst_data['email'],
            defaults={
                'name': inst_data['name'],
                'bio': inst_data['bio'],
                'is_instructor': True
            }
        )
        if created:
            instructor.set_password('Instructor123!')
            instructor.save()
        instructors.append(instructor)

    # Étudiants
    students_data = [
        'Alice Johnson', 'Bob Wilson', 'Charlie Brown', 'Diana Prince',
        'Ethan Hunt', 'Fiona Green', 'George Miller', 'Hannah Lee',
        'Ian Chen', 'Julia Roberts', 'Kevin Hart'
    ]

    students = []
    for name in students_data:
        email = f"{name.lower().replace(' ', '.')}@student.com"
        student, created = User.objects.get_or_create(
            email=email,
            defaults={'name': name}
        )
        if created:
            student.set_password('Student123!')
            student.save()
        students.append(student)

    return instructors, students


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

    # 🎯 20+ COURS POUR TOUTES LES CATÉGORIES
    youtube_courses_data = [
        # ==================== PYTHON (5 cours) ====================
        {
            'title': 'Python pour débutants',
            'category_slug': 'python',
            'instructor_index': 1,
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
            'title': 'Python Programmation Orientée Objet',
            'category_slug': 'python',
            'instructor_index': 1,
            'difficulty': 'intermediate',
            'price': Decimal('49.99'),
            'description': 'Maîtrisez la POO en Python',
            'playlist_id': 'PL-osiE80TeTsqhIuOqKhwlXsIBIdSeYtc',
            'learning_objectives': [
                'Classes et objets',
                'Héritage et polymorphisme',
                'Encapsulation',
                'Méthodes spéciales'
            ]
        },
        {
            'title': 'Django Framework Complet',
            'category_slug': 'python',
            'instructor_index': 1,
            'difficulty': 'intermediate',
            'price': Decimal('79.99'),
            'description': 'Créez des applications web professionnelles avec Django',
            'playlist_id': 'PL-osiE80TeTtoQCKZ03TU5fNfx2UY6U4p',
            'learning_objectives': [
                'Architecture MVT de Django',
                'Models et bases de données',
                'Templates et vues',
                'Authentification et sécurité'
            ]
        },
        {
            'title': 'Python Flask pour débutants',
            'category_slug': 'python',
            'instructor_index': 1,
            'difficulty': 'beginner',
            'price': Decimal('39.99'),
            'description': 'Créez des applications web légères avec Flask',
            'playlist_id': 'PL-osiE80TeTs4UjLw5MM6OjgkjFeUxCYH',
            'learning_objectives': [
                'Routing et vues Flask',
                'Templates Jinja2',
                'Formulaires et validation',
                'Déploiement'
            ]
        },
        {
            'title': 'Python pour Data Science',
            'category_slug': 'python',
            'instructor_index': 1,
            'difficulty': 'intermediate',
            'price': Decimal('69.99'),
            'description': 'Analyse de données avec Pandas, NumPy et Matplotlib',
            'playlist_id': 'PL-osiE80TeTsWmV9i9c58mdDCSskIFdDS',
            'learning_objectives': [
                'Manipulation de données avec Pandas',
                'Calculs NumPy',
                'Visualisation avec Matplotlib',
                'Analyse statistique'
            ]
        },

        # ==================== DÉVELOPPEMENT WEB (6 cours) ====================
        {
            'title': 'Développement Web Moderne',
            'category_slug': 'dev-web',
            'instructor_index': 0,
            'difficulty': 'beginner',
            'price': Decimal('0.00'),
            'description': 'HTML, CSS, JavaScript et frameworks modernes',
            'playlist_id': 'PLillGF-RfqbZTASqIqdvm1R5mLrQq79CU',
            'learning_objectives': [
                'Créer des sites web responsives',
                'Maîtriser HTML5 et CSS3',
                'Développer avec JavaScript ES6+',
                'Utiliser les frameworks modernes'
            ]
        },
        {
            'title': 'HTML et CSS pour débutants',
            'category_slug': 'dev-web',
            'instructor_index': 0,
            'difficulty': 'beginner',
            'price': Decimal('0.00'),
            'description': 'Les bases du développement web',
            'playlist_id': 'PL4cUxeGkcC9ivBf_eKCPIAYXWzLlPAm6G',
            'learning_objectives': [
                'Structure HTML sémantique',
                'Styling CSS moderne',
                'Flexbox et Grid',
                'Design responsive'
            ]
        },
        {
            'title': 'CSS Avancé et Animations',
            'category_slug': 'dev-web',
            'instructor_index': 0,
            'difficulty': 'intermediate',
            'price': Decimal('44.99'),
            'description': 'Maîtrisez les animations et transitions CSS',
            'playlist_id': 'PL4cUxeGkcC9iGYgmEd2dm3zAKzyCGDtM5',
            'learning_objectives': [
                'Animations CSS',
                'Transitions',
                'Transform et 3D',
                'Performance'
            ]
        },
        {
            'title': 'Tailwind CSS Framework',
            'category_slug': 'dev-web',
            'instructor_index': 0,
            'difficulty': 'beginner',
            'price': Decimal('34.99'),
            'description': 'Framework CSS utility-first',
            'playlist_id': 'PL4cUxeGkcC9gpXORlEHjc5bgnIi5HEGhw',
            'learning_objectives': [
                'Utility classes Tailwind',
                'Configuration personnalisée',
                'Composants réutilisables',
                'Build production'
            ]
        },
        {
            'title': 'Bootstrap 5 Complet',
            'category_slug': 'dev-web',
            'instructor_index': 0,
            'difficulty': 'beginner',
            'price': Decimal('29.99'),
            'description': 'Framework CSS le plus populaire',
            'playlist_id': 'PL4cUxeGkcC9joIM91nLzd_qaH_AimmdAR',
            'learning_objectives': [
                'Grille Bootstrap',
                'Composants UI',
                'Utilities',
                'Customisation'
            ]
        },
        {
            'title': 'Sass et SCSS Moderne',
            'category_slug': 'dev-web',
            'instructor_index': 0,
            'difficulty': 'intermediate',
            'price': Decimal('39.99'),
            'description': 'Préprocesseur CSS professionnel',
            'playlist_id': 'PL4cUxeGkcC9jxJX7vojNVK-o8ubDZEcNb',
            'learning_objectives': [
                'Variables et mixins',
                'Nesting',
                'Partials et imports',
                'Build workflow'
            ]
        },

        # ==================== JAVASCRIPT (5 cours) ====================
        {
            'title': 'JavaScript Moderne - ES6+',
            'category_slug': 'javascript',
            'instructor_index': 2,
            'difficulty': 'intermediate',
            'price': Decimal('49.99'),
            'description': 'Maîtrisez JavaScript moderne',
            'playlist_id': 'PLillGF-RfqbbnEGy3ROiLWk7JMCuSyQtX',
            'learning_objectives': [
                'Variables let et const',
                'Arrow functions',
                'Promises et Async/Await',
                'Modules ES6'
            ]
        },
        {
            'title': 'React pour débutants',
            'category_slug': 'javascript',
            'instructor_index': 2,
            'difficulty': 'beginner',
            'price': Decimal('59.99'),
            'description': 'Framework JavaScript le plus populaire',
            'playlist_id': 'PL4cUxeGkcC9gZD-Tvwfod2gaISzfRiP9d',
            'learning_objectives': [
                'Composants React',
                'State et Props',
                'Hooks',
                'React Router'
            ]
        },
        {
            'title': 'Vue.js 3 Complet',
            'category_slug': 'javascript',
            'instructor_index': 2,
            'difficulty': 'beginner',
            'price': Decimal('54.99'),
            'description': 'Framework progressif moderne',
            'playlist_id': 'PL4cUxeGkcC9hYYGbV6JDqKwOe5IGUjNFA',  # ✅ PLAYLIST VALIDE
            'learning_objectives': [
                'Composition API',
                'Réactivité Vue 3',
                'Vuex',
                'Vue Router'
            ]
        },
        {
            'title': 'Node.js et Express',
            'category_slug': 'javascript',
            'instructor_index': 2,
            'difficulty': 'intermediate',
            'price': Decimal('64.99'),
            'description': 'Backend JavaScript avec Node.js',
            'playlist_id': 'PL4cUxeGkcC9jsz4LDYc6kv3ymONOKxwBU',
            'learning_objectives': [
                'Serveur Node.js',
                'API REST avec Express',
                'MongoDB',
                'Authentification JWT'
            ]
        },
        {
            'title': 'TypeScript Fondamentaux',
            'category_slug': 'javascript',
            'instructor_index': 2,
            'difficulty': 'intermediate',
            'price': Decimal('44.99'),
            'description': 'JavaScript avec typage statique',
            'playlist_id': 'PL4cUxeGkcC9gUgr39Q_yD6v-bSyMwKPUI',
            'learning_objectives': [
                'Types de base',
                'Interfaces',
                'Classes',
                'Génériques'
            ]
        },

        # ==================== DATA SCIENCE (3 cours) ====================
        {
            'title': 'Machine Learning avec Python',
            'category_slug': 'data-science',
            'instructor_index': 1,
            'difficulty': 'advanced',
            'price': Decimal('89.99'),
            'description': 'Introduction au Machine Learning',
            'playlist_id': 'PLQVvvaa0QuDfKTOs3Keq_kaG2P55YRn5v',
            'learning_objectives': [
                'Algorithmes ML',
                'Scikit-learn',
                'Modèles prédictifs',
                'Évaluation'
            ]
        },
        {
            'title': 'Analyse de Données avec Pandas',
            'category_slug': 'data-science',
            'instructor_index': 1,
            'difficulty': 'intermediate',
            'price': Decimal('54.99'),
            'description': 'Manipulation et analyse de données',
            'playlist_id': 'PL-osiE80TeTsWmV9i9c58mdDCSskIFdDS',
            'learning_objectives': [
                'DataFrames Pandas',
                'Nettoyage de données',
                'Agrégations',
                'Visualisation'
            ]
        },
        {
            'title': 'Deep Learning avec TensorFlow',
            'category_slug': 'data-science',
            'instructor_index': 1,
            'difficulty': 'advanced',
            'price': Decimal('99.99'),
            'description': 'Réseaux de neurones profonds',
            'playlist_id': 'PLQVvvaa0QuDfhTox0AjmQ6tvTgMBZBEXN',
            'learning_objectives': [
                'Réseaux de neurones',
                'CNN',
                'RNN',
                'Transfer Learning'
            ]
        },

        # ==================== DESIGN (3 cours) ====================
        {
            'title': 'UI/UX Design Fondamentaux',
            'category_slug': 'design',
            'instructor_index': 3,
            'difficulty': 'beginner',
            'price': Decimal('44.99'),
            'description': 'Principes du design d\'interface',
            'playlist_id': 'PLDyQo7g0_nsVHmyZtVqoB5xWu_CslvaXl',
            'learning_objectives': [
                'Principes UX',
                'Design thinking',
                'Wireframing',
                'Prototyping'
            ]
        },
        {
            'title': 'Figma pour designers',
            'category_slug': 'design',
            'instructor_index': 3,
            'difficulty': 'beginner',
            'price': Decimal('39.99'),
            'description': 'Outil de design UI moderne',
            'playlist_id': 'PLvnhDG7f9_6cBJvV7EQ2pIDAx3eC9Xcn6',
            'learning_objectives': [
                'Interface Figma',
                'Components',
                'Auto-layout',
                'Prototypes interactifs'
            ]
        },
        {
            'title': 'Adobe XD Design Complet',
            'category_slug': 'design',
            'instructor_index': 3,
            'difficulty': 'beginner',
            'price': Decimal('34.99'),
            'description': 'Design UI/UX avec Adobe XD',
            'playlist_id': 'PLjwm_8O3suyPkIphVrJaebR2qE8jylWBQ',
            'learning_objectives': [
                'Outils XD',
                'Repeat Grid',
                'Animations',
                'Partage et collaboration'
            ]
        },
    ]

    courses = []

    for i, course_data in enumerate(youtube_courses_data):
        try:
            # Trouver la catégorie
            category = next((cat for cat in categories if cat.slug == course_data['category_slug']), None)
            if not category:
                print(f"⚠️ Catégorie {course_data['category_slug']} non trouvée, skip")
                continue

            instructor = instructors[course_data['instructor_index']]

            print(f"\n🔍 Traitement du cours: {course_data['title']}")

            # Créer le cours de base
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
                is_new=(i < 5),
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

            # 🎯 RÉCUPÉRER LES VIDÉOS DEPUIS YOUTUBE
            print(f"📺 Récupération des vidéos depuis la playlist {course_data['playlist_id']}...")

            try:
                videos = youtube_service.get_playlist_videos(course_data['playlist_id'], max_results=10)

                if videos:
                    print(f"✅ {len(videos)} vidéos trouvées sur YouTube")

                    # Créer les leçons avec les vraies vidéos YouTube
                    for order, video in enumerate(videos, 1):
                        lesson = Lesson.objects.create(
                            module=module,
                            title=video['title'][:200],
                            lesson_type='video',
                            order=order,
                            duration=max(1, video['duration_seconds'] // 60),
                            youtube_video_id=video['id'],
                            video_url=f"https://www.youtube.com/watch?v={video['id']}",
                            content=video['description'][:500] if video['description'] else '',
                            is_published=True,
                            is_preview=(order <= 2)
                        )
                        print(f"  ✅ Leçon {order}: {lesson.title[:50]}... (YouTube ID: {video['id']})")
                else:
                    print(f"⚠️ Aucune vidéo trouvée, création de leçons basiques")
                    create_fallback_lessons(module, course_data['title'])

            except Exception as e:
                print(f"❌ Erreur lors de la récupération des vidéos: {e}")
                create_fallback_lessons(module, course_data['title'])

            courses.append(course)

        except Exception as e:
            print(f"❌ Erreur lors de la création du cours {course_data['title']}: {e}")
            continue

    return courses


def create_fallback_lessons(module, course_title):
    """Créer des leçons basiques en cas d'erreur YouTube"""
    for j in range(5):
        Lesson.objects.create(
            module=module,
            title=f'Leçon {j + 1}: {course_title} - Partie {j + 1}',
            lesson_type='video',
            order=j + 1,
            duration=random.randint(15, 45),
            video_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            content=f'Contenu de la leçon {j + 1}',
            is_published=True,
            is_preview=(j < 2)
        )


def create_basic_courses(categories, instructors):
    """Créer des cours basiques sans YouTube"""
    print("⚠️ Création de cours basiques (sans YouTube API)")

    courses_data = [
        {
            'title': 'Python pour débutants',
            'category_slug': 'python',
            'instructor_index': 1,
            'difficulty': 'beginner',
            'price': Decimal('0.00'),
            'description': 'Apprenez Python de zéro'
        },
        {
            'title': 'Développement Web',
            'category_slug': 'dev-web',
            'instructor_index': 0,
            'difficulty': 'beginner',
            'price': Decimal('0.00'),
            'description': 'HTML, CSS, JavaScript'
        },
        {
            'title': 'JavaScript Moderne',
            'category_slug': 'javascript',
            'instructor_index': 2,
            'difficulty': 'intermediate',
            'price': Decimal('49.99'),
            'description': 'ES6+ et frameworks'
        }
    ]

    courses = []
    for course_data in courses_data:
        category = next((cat for cat in categories if cat.slug == course_data['category_slug']), categories[0])
        instructor = instructors[course_data['instructor_index']]

        course = Course.objects.create(
            title=course_data['title'],
            category=category,
            instructor=instructor,
            difficulty=course_data['difficulty'],
            price=course_data['price'],
            description=course_data['description'],
            is_published=True
        )

        module = Module.objects.create(
            course=course,
            title='Contenu principal',
            order=1
        )

        create_fallback_lessons(module, course_data['title'])
        courses.append(course)

    return courses


def create_enrollments(courses, students):
    """Créer des inscriptions d'exemple"""
    print("\n✏️ Création des inscriptions d'exemple...")

    enrollments = []
    for student in students[:8]:
        selected_courses = random.sample(courses, min(2, len(courses)))
        for course in selected_courses:
            enrollment, created = Enrollment.objects.get_or_create(
                user=student,
                course=course,
                defaults={
                    'enrolled_at': datetime.now() - timedelta(days=random.randint(1, 30))
                    # ❌ LIGNE SUPPRIMÉE: 'progress': random.randint(0, 100)
                }
            )
            if created:
                enrollments.append(enrollment)
                print(f"✅ Inscription: {student.name} → {course.title}")

    return enrollments


def create_reviews(enrollments):
    """Créer des avis d'exemple"""
    print("\n⭐ Création des avis...")

    comments = [
        "Excellent cours, très bien expliqué !",
        "J'ai beaucoup appris, merci !",
        "Parfait pour les débutants",
        "Contenu de qualité",
        "Instructeur très pédagogue",
        "Je recommande ce cours"
    ]

    reviews = []
    for enrollment in enrollments[:10]:
        if random.random() > 0.3:
            review, created = Review.objects.get_or_create(
                user=enrollment.user,
                course=enrollment.course,
                defaults={
                    'rating': random.randint(4, 5),
                    'comment': random.choice(comments)
                }
            )
            if created:
                reviews.append(review)
                print(f"✅ Avis créé: {enrollment.user.name} pour {enrollment.course.title}")

    return reviews


def main():
    """Fonction principale"""
    print("\n🚀 Démarrage de la population avec contenu YouTube réel...")

    show_configuration_info()

    # Créer les données
    categories = create_categories()
    instructors, students = create_users()
    courses = create_youtube_courses(categories, instructors)
    enrollments = create_enrollments(courses, students)
    reviews = create_reviews(enrollments)

    # Afficher les statistiques
    print("\n✅ Population terminée avec succès!")
    print(f"\n📊 Statistiques:")
    print(f"   - Catégories: {Category.objects.count()}")
    print(f"   - Utilisateurs: {User.objects.count()}")
    print(f"   - Cours: {Course.objects.count()}")
    print(f"   - Modules: {Module.objects.count()}")
    print(f"   - Leçons: {Lesson.objects.count()}")
    print(f"   - Inscriptions: {Enrollment.objects.count()}")
    print(f"   - Avis: {Review.objects.count()}")

    print(f"\n🎯 Comptes de test créés:")
    print(f"   - Admin: admin@wim.com / Admin123!")
    print(f"   - Étudiant: alice.johnson@student.com / Student123!")

    print(f"\n📝 Prochaines étapes:")
    print(f"1. Configurez votre clé API YouTube")
    print(f"2. Créez l'app YouTube avec les services")
    print(f"3. Ajoutez les champs YouTube aux modèles")
    print(f"4. Testez l'intégration YouTube")

    print("\n🎉 Votre plateforme WIM est prête!")


if __name__ == '__main__':
    main()