from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create default test users for each role so UI states can be previewed quickly."

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            default="SkolaTest123!",
            help="Password to assign to all generated accounts (default: SkolaTest123!)",
        )

    def handle(self, *args, **options):
        User = get_user_model()
        password = options["password"]

        fixtures = [
            {
                "username": "admin",
                "email": "admin@skola.test",
                "role": User.Role.ADMIN,
                "is_staff": True,
                "is_superuser": True,
                "first_name": "Ava",
                "last_name": "Admin",
            },
            {
                "username": "staff",
                "email": "staff@skola.test",
                "role": User.Role.STAFF,
                "is_staff": True,
                "is_superuser": False,
                "first_name": "Sam",
                "last_name": "Staff",
            },
            {
                "username": "teacher",
                "email": "teacher@skola.test",
                "role": User.Role.TEACHER,
                "is_staff": True,
                "is_superuser": False,
                "first_name": "Tia",
                "last_name": "Teacher",
            },
            {
                "username": "student",
                "email": "student@skola.test",
                "role": User.Role.STUDENT,
                "is_staff": False,
                "is_superuser": False,
                "first_name": "Stu",
                "last_name": "Dent",
            },
            {
                "username": "guardian",
                "email": "guardian@skola.test",
                "role": User.Role.GUARDIAN,
                "is_staff": False,
                "is_superuser": False,
                "first_name": "Gia",
                "last_name": "Guardian",
            },
        ]

        for data in fixtures:
            username = data["username"]
            user, _ = User.objects.get_or_create(username=username, defaults=data)

            # Ensure attributes (like role or permissions) stay up to date.
            for field, value in data.items():
                setattr(user, field, value)

            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"User '{username}' ready (role: {user.get_role_display()})."))

        self.stdout.write(self.style.NOTICE(f"All accounts share the password: {password}"))
