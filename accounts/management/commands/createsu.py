from django.core.management.base import BaseCommand
from accounts.models import User
import os

class Command(BaseCommand):
    help = 'Create superuser automatically'

    def handle(self, *args, **options):
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@truckease.com')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'Admin123!')
        
        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(
                email=email,
                password=password,
                first_name='System',
                last_name='Admin',
                user_type='admin'
            )
            self.stdout.write(self.style.SUCCESS(f'Superuser created: {email}'))
        else:
            self.stdout.write(self.style.WARNING(f'Superuser already exists: {email}'))