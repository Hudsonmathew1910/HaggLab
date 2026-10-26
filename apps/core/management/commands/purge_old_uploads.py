import os
import time
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Requirement 10: Delete demo uploads older than 24 hours (86400 seconds)'

    def handle(self, *args, **options):
        upload_dir = Path(getattr(settings, 'PRIVATE_STORAGE_ROOT', settings.BASE_DIR / 'private_uploads'))
        if not upload_dir.exists():
            self.stdout.write("Upload directory does not exist. Nothing to purge.")
            return

        now = time.time()
        cutoff = now - (24 * 3600)
        purged = 0

        for file_path in upload_dir.glob('*'):
            if file_path.is_file():
                if file_path.stat().st_mtime < cutoff:
                    try:
                        file_path.unlink()
                        purged += 1
                    except Exception as e:
                        self.stderr.write(f"Failed to delete {file_path}: {e}")

        self.stdout.write(self.style.SUCCESS(f"Purge complete: deleted {purged} file(s) older than 24 hours."))
