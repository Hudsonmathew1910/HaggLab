import time

from django.core.management.base import BaseCommand, CommandError

from apps.tryit import rag


class Command(BaseCommand):
    help = 'Chunk the sample datasets, embed them with Pinecone and upload them, one namespace per project.'

    def add_arguments(self, parser):
        parser.add_argument('projects', nargs='*', help=f"Projects to upload (default: all of {', '.join(rag.SOURCES)})")

    def handle(self, *args, **options):
        projects = options['projects'] or list(rag.SOURCES)
        unknown = [p for p in projects if p not in rag.SOURCES]
        if unknown:
            raise CommandError(f"Unknown project(s): {', '.join(unknown)}. Choose from: {', '.join(rag.SOURCES)}")
        for project in projects:
            started = time.perf_counter()
            try:
                count = rag.ingest(project)
            except rag.RagUnavailable as exc:
                raise CommandError(str(exc))
            self.stdout.write(self.style.SUCCESS(
                f'{project}: {count} chunks uploaded in {time.perf_counter() - started:.1f}s'))
