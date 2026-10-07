from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = 'Seeds exactly the three development/demo users: Admin, Student A, and Student B'

    def handle(self, *args, **options):
        # 1. Clean up old demo users from development seed data
        old_emails = ['student@mmcoe.edu.in', 'admin@mmcoe.edu.in']
        deleted_count, _ = User.objects.filter(email__in=old_emails).delete()
        if deleted_count:
            self.stdout.write(self.style.WARNING(f"Removed {deleted_count} old demo user(s)."))

        # 2. Seed Admin
        admin_email = 'admin@gmail.com'
        admin_user, created = User.objects.get_or_create(
            email=admin_email,
            defaults={
                'username': 'admin',
                'full_name': 'Admin',
                'role': User.Role.ADMIN,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin_user.username = 'admin'
        admin_user.full_name = 'Admin'
        admin_user.role = User.Role.ADMIN
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.set_password('Admin@123')
        admin_user.save()
        status_admin = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{status_admin} Admin: {admin_email} | Password: Admin@123 | Role: ADMIN"))

        # 3. Seed Student A
        student_a_email = 'student.a@gmail.com'
        student_a, created_a = User.objects.get_or_create(
            email=student_a_email,
            defaults={
                'username': 'student_a',
                'full_name': 'Student A',
                'role': User.Role.STUDENT,
                'is_staff': False,
                'is_superuser': False,
            }
        )
        student_a.username = 'student_a'
        student_a.full_name = 'Student A'
        student_a.role = User.Role.STUDENT
        student_a.set_password('Studenta@123')
        student_a.save()
        status_a = "Created" if created_a else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{status_a} Student A: {student_a_email} | Password: Studenta@123 | Role: STUDENT"))

        # 4. Seed Student B
        student_b_email = 'student.b@gmail.com'
        student_b, created_b = User.objects.get_or_create(
            email=student_b_email,
            defaults={
                'username': 'student_b',
                'full_name': 'Student B',
                'role': User.Role.STUDENT,
                'is_staff': False,
                'is_superuser': False,
            }
        )
        student_b.username = 'student_b'
        student_b.full_name = 'Student B'
        student_b.role = User.Role.STUDENT
        student_b.set_password('Studentb@123')
        student_b.save()
        status_b = "Created" if created_b else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{status_b} Student B: {student_b_email} | Password: Studentb@123 | Role: STUDENT"))
