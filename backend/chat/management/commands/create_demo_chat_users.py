from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import UserProfile, UserCourseProgress
from course.models import Course, CourseDay


class Command(BaseCommand):
    help = 'Create demo chat users for testing'

    def handle(self, *args, **options):
        User = get_user_model()

        demo_users = [
            {
                'username': 'Li_Mei',
                'email': 'li.mei@example.com',
                'password': 'DemoUser123',
                'bio': 'Преподаватель китайского языка из Пекина 🇨🇳',
                'hsk_level': 3
            },
            {
                'username': 'Wang_Wei',
                'email': 'wang.wei@example.com',
                'password': 'DemoUser123',
                'bio': 'Изучает русский язык, любит общаться 📚',
                'hsk_level': 2
            },
            {
                'username': 'Chen_Yu',
                'email': 'chen.yu@example.com',
                'password': 'DemoUser123',
                'bio': 'Студент университета, помогает с практикой 🎓',
                'hsk_level': 1
            }
        ]

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for user_data in demo_users:
            username = user_data['username']
            email = user_data['email']
            password = user_data['password']
            bio = user_data['bio']
            hsk_level = user_data['hsk_level']

            # Check if user exists
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                # Update password to make sure it works
                user.set_password(password)
                user.save()
                self.stdout.write(self.style.WARNING(f'✓ User {username} already exists, updated password...'))
                updated_count += 1
            else:
                # Create user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                self.stdout.write(self.style.SUCCESS(f'✓ Created user: {username}'))
                created_count += 1

            # Create or update profile
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'bio': bio,
                    'learning_language': 'RU',
                    'current_hsk_level': hsk_level
                }
            )
            if not created:
                profile.bio = bio
                profile.learning_language = 'RU'
                profile.current_hsk_level = hsk_level
                profile.save()

            # Create or update progress
            progress, created = UserCourseProgress.objects.get_or_create(
                user=user,
                defaults={
                    'current_day': 1,
                    'total_xp': 100,
                    'streak_days': 5
                }
            )
            if not created:
                progress.current_day = 1
                progress.total_xp = 100
                progress.streak_days = 5
                progress.save()

            # Ensure course exists for this HSK level
            course, course_created = Course.objects.get_or_create(
                hsk_level=hsk_level,
                is_active=True,
                defaults={
                    'title': f'HSK {hsk_level} - {"Уровень 1" if hsk_level == 1 else "Начальный" if hsk_level == 2 else "Средний"}',
                    'description': f'Курс китайского языка HSK {hsk_level}',
                    'total_days': 5
                }
            )

            # Create course days if they don't exist
            if course_created:
                for day_num in range(1, 6):
                    CourseDay.objects.get_or_create(
                        course=course,
                        day_number=day_num,
                        defaults={
                            'title': f'Урок {day_num}',
                            'description': f'Описание урока {day_num}',
                            'estimated_minutes': 15
                        }
                    )
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created course for HSK {hsk_level}'))

        self.stdout.write(self.style.SUCCESS(f'\n✅ Created: {created_count} users'))
        self.stdout.write(self.style.SUCCESS(f'✅ Updated: {updated_count} users'))

        self.stdout.write('\n📚 All users now have:')
        self.stdout.write('  - User profiles with HSK levels')
        self.stdout.write('  - Course progress (Day 1, XP: 100, Streak: 5)')
        self.stdout.write('  - Active courses for learning')

        self.stdout.write('\n🔑 Login credentials:')
        self.stdout.write('  Username: Li_Mei, Wang_Wei, or Chen_Yu')
        self.stdout.write('  Password: DemoUser123')
