"""
Script de population de la base de données - WIM Platform
Génère des données de test complètes
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
from apps.progress.models import LessonProgress
from apps.certificates.models import Certificate


def create_categories():
    """Créer les catégories de cours"""
    categories_data = [
        {
            'name': 'Développement Web',
            'slug': 'dev-web',
            'description': 'Apprenez les langages et frameworks web modernes',
            'icon': '💻',
            'color': '#4A90E2',
            'order': 1
        },
        {
            'name': 'Design',
            'slug': 'design',
            'description': 'UI/UX, graphisme et design thinking',
            'icon': '🎨',
            'color': '#9B59B6',
            'order': 2
        },
        {
            'name': 'Data Science',
            'slug': 'data-science',
            'description': 'Analyse de données et machine learning',
            'icon': '📊',
            'color': '#E74C3C',
            'order': 3
        },
        {
            'name': 'Backend',
            'slug': 'backend',
            'description': 'Serveurs, APIs et bases de données',
            'icon': '⚙️',
            'color': '#27AE60',
            'order': 4
        },
        {
            'name': 'Mobile',
            'slug': 'mobile',
            'description': 'Développement iOS et Android',
            'icon': '📱',
            'color': '#F39C12',
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

    # Instructeurs
    instructors = []
    instructors_data = [
        ('Marie Dupont', 'marie@wim.com'),
        ('Jean Martin', 'jean@wim.com'),
        ('Sophie Bernard', 'sophie@wim.com'),
        ('Pierre Dubois', 'pierre@wim.com'),
        ('Lucas Robert', 'lucas@wim.com'),
    ]

    for name, email in instructors_data:
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'name': name,
                'is_instructor': True,
                'bio': f"Instructeur expérimenté en {name.split()[0]}"
            }
        )
        if created:
            user.set_password('Instructor123!')
            user.save()
            print(f"✅ Instructeur créé: {email}")
        instructors.append(user)

    # Étudiants
    students = []
    students_data = [
        'Alice Johnson', 'Bob Wilson', 'Charlie Brown', 'Diana Prince',
        'Ethan Hunt', 'Fiona Green', 'George White', 'Hannah Black',
        'Ivan Grey', 'Julia Red'
    ]

    for i, name in enumerate(students_data, 1):
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


def create_courses(categories, instructors):
    """Créer des cours avec modules et leçons"""

    courses_data = [
        {
            'title': 'Python pour débutants',
            'category': 'dev-web',
            'difficulty': 'beginner',
            'price': Decimal('0.00'),
            'description': 'Apprenez Python de zéro',
            'modules': [
                {
                    'title': 'Introduction',
                    'lessons': [
                        {'title': 'Présentation du cours', 'type': 'video', 'duration': 10},
                        {'title': 'Installation Python', 'type': 'text', 'duration': 15},
                        {'title': 'Premier programme', 'type': 'video', 'duration': 20}
                    ]
                },
                {
                    'title': 'Les bases',
                    'lessons': [
                        {'title': 'Variables et types', 'type': 'video', 'duration': 25},
                        {'title': 'Quiz variables', 'type': 'quiz', 'duration': 10},
                        {'title': 'Structures conditionnelles', 'type': 'video', 'duration': 30}
                    ]
                }
            ]
        },
        {
            'title': 'React JS Complet',
            'category': 'dev-web',
            'difficulty': 'intermediate',
            'price': Decimal('49.99'),
            'description': 'Maîtrisez React et ses hooks',
            'modules': [
                {
                    'title': 'Fondamentaux React',
                    'lessons': [
                        {'title': 'JSX et composants', 'type': 'video', 'duration': 30},
                        {'title': 'Props et State', 'type': 'video', 'duration': 35},
                    ]
                }
            ]
        },
        {
            'title': 'UI/UX Design Masterclass',
            'category': 'design',
            'difficulty': 'intermediate',
            'price': Decimal('59.99'),
            'description': 'Créez des interfaces utilisateur exceptionnelles',
            'modules': [
                {
                    'title': 'Principes de design',
                    'lessons': [
                        {'title': 'Théorie des couleurs', 'type': 'video', 'duration': 40},
                        {'title': 'Typographie', 'type': 'text', 'duration': 25},
                    ]
                }
            ]
        },
        {
            'title': 'Machine Learning avec Python',
            'category': 'data-science',
            'difficulty': 'advanced',
            'price': Decimal('89.99'),
            'description': 'Intelligence artificielle et ML',
            'modules': [
                {
                    'title': 'Introduction au ML',
                    'lessons': [
                        {'title': 'Qu\'est-ce que le ML?', 'type': 'video', 'duration': 20},
                        {'title': 'Algorithmes supervisés', 'type': 'video', 'duration': 45},
                    ]
                }
            ]
        },
        {
            'title': 'Django REST API',
            'category': 'backend',
            'difficulty': 'advanced',
            'price': Decimal('69.99'),
            'description': 'Créez des APIs RESTful avec Django',
            'modules': [
                {
                    'title': 'Setup Django',
                    'lessons': [
                        {'title': 'Installation Django', 'type': 'video', 'duration': 15},
                        {'title': 'Première API', 'type': 'video', 'duration': 30},
                    ]
                }
            ]
        }
    ]

    courses = []
    for i, course_data in enumerate(courses_data):
        category = Category.objects.get(slug=course_data['category'])
        instructor = random.choice(instructors)

        course, created = Course.objects.get_or_create(
            title=course_data['title'],
            defaults={
                'category': category,
                'instructor': instructor,
                'difficulty': course_data['difficulty'],
                'price': course_data['price'],
                'description': course_data['description'],
                'full_description': f"# {course_data['title']}\n\n{course_data['description']}\n\nCe cours complet vous permettra de maîtriser tous les concepts essentiels.",
                'rating': Decimal(random.uniform(3.5, 5.0)),
                'total_students': random.randint(50, 500),
                'is_published': True,
                'is_new': i < 2
            }
        )

        if created:
            print(f"✅ Cours créé: {course.title}")

            # Créer modules et leçons
            for mod_idx, module_data in enumerate(course_data['modules'], 1):
                module = Module.objects.create(
                    course=course,
                    title=module_data['title'],
                    description=f"Module {mod_idx}",
                    order=mod_idx
                )

                for les_idx, lesson_data in enumerate(module_data['lessons'], 1):
                    Lesson.objects.create(
                        module=module,
                        title=lesson_data['title'],
                        lesson_type=lesson_data['type'],
                        content=f"Contenu de la leçon {lesson_data['title']}",
                        video_url='https://www.youtube.com/watch?v=example' if lesson_data['type'] == 'video' else '',
                        duration=lesson_data['duration'],
                        order=les_idx
                    )

        courses.append(course)

    return courses


def create_enrollments(students, courses):
    """Créer des inscriptions et progressions"""

    enrollments = []

    for student in students[:5]:  # 5 premiers étudiants
        # Inscrire à 2-4 cours aléatoires
        selected_courses = random.sample(courses, random.randint(2, 4))

        for course in selected_courses:
            enrollment, created = Enrollment.objects.get_or_create(
                user=student,
                course=course,
                defaults={
                    'progress_percentage': Decimal(random.uniform(0, 100)),
                    'is_active': True,
                    'enrolled_at': timezone.now() - timedelta(days=random.randint(1, 30))
                }
            )

            if created:
                # Ajouter des progressions de leçons
                lessons = Lesson.objects.filter(module__course=course)[:3]
                for lesson in lessons:
                    if random.choice([True, False]):
                        LessonProgress.objects.create(
                            enrollment=enrollment,
                            lesson=lesson,
                            is_completed=True,
                            time_spent=random.randint(300, 1800),
                            completed_at=timezone.now() - timedelta(days=random.randint(0, 10))
                        )

                enrollment.calculate_progress()
                enrollments.append(enrollment)
                print(f"✅ Inscription: {student.name} → {course.title}")

    return enrollments


def create_reviews(students, courses):
    """Créer des avis"""

    for student in students[:3]:
        for course in random.sample(courses, 2):
            if Enrollment.objects.filter(user=student, course=course).exists():
                Review.objects.get_or_create(
                    user=student,
                    course=course,
                    defaults={
                        'rating': random.randint(3, 5),
                        'comment': f"Excellent cours ! Je recommande vivement pour apprendre {course.title}.",
                        'content_quality': random.randint(3, 5),
                        'instructor_quality': random.randint(4, 5)
                    }
                )
                print(f"✅ Avis créé: {student.name} pour {course.title}")


def main():
    """Fonction principale"""
    print("\n🚀 Démarrage de la population de la base de données...\n")

    print("📁 Création des catégories...")
    categories = create_categories()

    print("\n👥 Création des utilisateurs...")
    admin, instructors, students = create_users()

    print("\n📚 Création des cours, modules et leçons...")
    courses = create_courses(categories, instructors)

    print("\n✏️ Création des inscriptions et progressions...")
    enrollments = create_enrollments(students, courses)

    print("\n⭐ Création des avis...")
    create_reviews(students, courses)

    print("\n✅ Population terminée avec succès!")
    print(f"\n📊 Statistiques:")
    print(f"   - Catégories: {Category.objects.count()}")
    print(f"   - Utilisateurs: {User.objects.count()}")
    print(f"   - Cours: {Course.objects.count()}")
    print(f"   - Modules: {Module.objects.count()}")
    print(f"   - Leçons: {Lesson.objects.count()}")
    print(f"   - Inscriptions: {Enrollment.objects.count()}")
    print(f"   - Avis: {Review.objects.count()}")
    print("\n🎉 Vous pouvez maintenant utiliser la plateforme!")


if __name__ == '__main__':
    main()