from django.core.management.base import BaseCommand

from common.models import TranslationEntry


class Command(BaseCommand):
    help = 'Dumps all TranslationEntry objects into a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('outfile', type=str, help='Path to output file')
        parser.add_argument('--lang', type=str, help='If set, dump only entries of this language')

    def handle(self, *args, **options):
        filter_args = {'lang': options['lang']} if options['lang'] else {}
        count = 0
        with open(options['outfile'], 'w') as fh:
            fh.write('name;lang;text\n')
            for te in TranslationEntry.objects.filter(**filter_args).order_by('name'):
                fh.write(f'{te.name};{te.lang};{te.text}\n')
                count += 1
        print(f"Dumped {count} entries into {options['outfile']}")
