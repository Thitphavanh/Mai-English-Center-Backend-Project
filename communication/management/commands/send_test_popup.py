from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from communication.models import PopupMessage

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a test popup message for parents'

    def add_arguments(self, parser):
        parser.add_argument('--title', type=str, default='Test Popup', help='Title of the popup')
        parser.add_argument('--message', type=str, default='This is a test notification for parents.', help='Message content')
        parser.add_argument('--user', type=str, help='Username of the target parent (optional, if empty sends to all)')

    def handle(self, *args, **options):
        title = options['title']
        message = options['message']
        username = options['user']

        popup = PopupMessage.objects.create(
            title=title,
            message=message,
            is_active=True
        )

        if username:
            try:
                user = User.objects.get(username=username)
                popup.target_users.add(user)
                self.stdout.write(self.style.SUCCESS(f'Successfully created popup "{title}" for user {username}'))
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User with username "{username}" does not exist.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Successfully created popup "{title}" for ALL users'))
