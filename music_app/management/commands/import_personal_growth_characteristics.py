# import_personal_growth_characteristics.py
import csv
from django.core.management.base import BaseCommand
from music_app.models import PersonalGrowthCharacteristic

class Command(BaseCommand):
    help = 'Load a list of personal growth characteristics from a CSV file into the database'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **options):
        try:
            with open(options['csv_file'], 'r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=';')
                next(reader)  # Skip the header row
                for row in reader:
                    if len(row) == 4:  # Ensure each row has exactly 4 columns
                        _, created = PersonalGrowthCharacteristic.objects.get_or_create(
                            category=row[1].strip(),
                            name=row[2].strip(),
                            description=row[3].strip()
                        )
                        if created:
                            self.stdout.write(self.style.SUCCESS(f'Successfully added characteristic "{row[2]}"'))
                    else:
                        self.stdout.write(self.style.WARNING(f'Skipping improperly formatted row: {row}'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {options["csv_file"]}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {e}'))
#code to import:
#python manage.py import_personal_growth_characteristics /home/admin_0/django_sounds/music_app/management/db_imports/personal_growth_characteristics.csv
