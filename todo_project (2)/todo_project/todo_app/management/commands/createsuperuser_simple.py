from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import getpass


class Command(BaseCommand):
    help = 'Create a superuser with only username and password'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating superuser...'))
        
        # Get username
        while True:
            username = input('Username: ').strip()
            if username:
                if User.objects.filter(username=username).exists():
                    self.stdout.write(self.style.ERROR(f'Username "{username}" already exists. Please choose another.'))
                    continue
                break
            else:
                self.stdout.write(self.style.ERROR('Username cannot be blank.'))
        
        # Get password
        while True:
            password = getpass.getpass('Password: ')
            if password:
                password_confirm = getpass.getpass('Password (again): ')
                if password == password_confirm:
                    break
                else:
                    self.stdout.write(self.style.ERROR('Passwords do not match.'))
            else:
                self.stdout.write(self.style.ERROR('Password cannot be blank.'))
        
        # Create the superuser
        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                is_staff=True,
                is_superuser=True
            )
            self.stdout.write(
                self.style.SUCCESS(f'Superuser "{username}" created successfully!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating superuser: {e}')
            ) 