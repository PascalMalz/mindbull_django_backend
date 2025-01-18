from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Your custom command help text'

    def handle(self, *args, **options):
        # Your command logic here
        self.stdout.write(self.style.SUCCESS('Command executed successfully'))
