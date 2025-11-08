from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

class Command(BaseCommand):
    help = 'Create JWT token for a user'
    
    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to create token for')
    
    def handle(self, *args, **options):
        User = get_user_model()
        username = options['username']
        
        try:
            user = User.objects.get(username=username)
            refresh = RefreshToken.for_user(user)
            
            self.stdout.write(
                self.style.SUCCESS(f'Token created for user: {username}')
            )
            self.stdout.write(f'Access Token: {refresh.access_token}')
            self.stdout.write(f'Refresh Token: {refresh}')
            
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User "{username}" does not exist')
            )