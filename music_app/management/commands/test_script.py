from django.core.management.base import BaseCommand
from django.core.mail import send_mail

class Command(BaseCommand):
    help = 'My custom test command'

    def handle(self, *args, **options):
        subject = 'Test Subject'
        message = 'This is a test message'
        from_email = 'noreply@audifull.de'
        recipient_list = ['pascalmalz@gmail.com']

        send_mail(subject, message, from_email, recipient_list)
        self.stdout.write(self.style.SUCCESS('Email sent successfully'))
