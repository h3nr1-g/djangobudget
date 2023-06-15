import csv

from django.core.management.base import BaseCommand

from common.models import TranslationEntry


class Command(BaseCommand):
    help = 'Loads TranslationEntry objects from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('infile', type=str, help='Path to output file')

    def handle(self, *args, **options):
        created = 0
        updated = 0
        with open(options['infile']) as fh:
            reader = csv.DictReader(fh, delimiter=';')
            for row in reader:
                try:
                    te = TranslationEntry.objects.get(name=row['name'], lang=row['lang'])
                    updated += 1
                except TranslationEntry.DoesNotExist:
                    te = TranslationEntry.objects.create(name=row['name'], lang=row['lang'])
                    created += 1
                finally:
                    te.text = row['text']
                    te.save()

        print(f"Created {created} entries from {options['infile']}")
        print(f"Updated {updated} entries from {options['infile']}")
