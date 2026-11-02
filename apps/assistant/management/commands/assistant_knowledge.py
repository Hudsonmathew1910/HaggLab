"""
Show what Haggi knows, straight from the live content.

    python manage.py assistant_knowledge                 # every passage: title, link, size
    python manage.py assistant_knowledge "how much is a chatbot"   # the passages that question would get
"""
from django.core.management.base import BaseCommand

from apps.assistant import knowledge, search


class Command(BaseCommand):
    help = "List Haggi's live knowledge passages, or the passages a question would get."

    def add_arguments(self, parser):
        parser.add_argument('question', nargs='?', default='')
        parser.add_argument('--full', action='store_true', help='Print the full text of each passage.')

    def handle(self, question, full, **options):
        knowledge.clear()
        if question:
            rows = search.search(question)
            self.stdout.write(f'Top passages for: {question}\n')
        else:
            _version, rows = knowledge.get_chunks()
            self.stdout.write(f'{len(rows)} passages\n')
        for c in rows:
            score = f' [{c["score"]}]' if 'score' in c else ''
            self.stdout.write(f'- ({c["kind"]}) {c["title"]}{score}  {c["url"]}  {len(c["text"])} chars')
            if full or question:
                self.stdout.write('    ' + c['text'][:600 if not full else None] + '\n')
