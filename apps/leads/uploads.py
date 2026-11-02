"""
Files a visitor attaches on /start (the "Attachment" order question).

Safety rules:
- Stored outside the public folders, in PRIVATE_STORAGE_ROOT/inquiries/<inquiry uuid>/, under a random name.
  The original name is kept only as text, for the admin.
- Only staff can download them (apps.leads.views.inquiry_file_view), always as a download, never shown in the page.
- Only common document and image types, up to MAX_BYTES each, and the file's first bytes must match its type,
  so a renamed program or web page is refused.
- The 24-hour purge (purge_old_uploads) only touches files at the top of private_uploads, not these.
"""
import re
import uuid
from pathlib import Path

from django.conf import settings
from django.core.files.storage import FileSystemStorage

MAX_BYTES = 10 * 1024 * 1024  # 10 MB per file
MAX_LABEL = '10 MB'

# extension -> (content type to send on download, check of the first bytes)
TYPES = {
    'pdf': ('application/pdf', lambda b: b.startswith(b'%PDF-')),
    'png': ('image/png', lambda b: b.startswith(b'\x89PNG\r\n\x1a\n')),
    'jpg': ('image/jpeg', lambda b: b.startswith(b'\xff\xd8\xff')),
    'jpeg': ('image/jpeg', lambda b: b.startswith(b'\xff\xd8\xff')),
    'xlsx': ('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', lambda b: b.startswith(b'PK\x03\x04')),
    'docx': ('application/vnd.openxmlformats-officedocument.wordprocessingml.document', lambda b: b.startswith(b'PK\x03\x04')),
    'xls': ('application/vnd.ms-excel', lambda b: b.startswith(b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1')),
    'csv': ('text/csv', None),
    'txt': ('text/plain', None),
}
ACCEPT = ','.join('.' + ext for ext in TYPES)  # for the <input accept="..."> attribute
ALLOWED_LABEL = 'PDF, CSV, Excel, Word, TXT, PNG or JPG'


class UploadError(ValueError):
    """A visitor-facing reason a file was refused."""


def private_storage():
    return FileSystemStorage(location=Path(settings.PRIVATE_STORAGE_ROOT) / 'inquiries')


def clean_name(name):
    """A safe display name: no folders, no odd characters, at most 120 characters."""
    name = Path(name or 'file').name
    name = re.sub(r'[^A-Za-z0-9._ -]+', '_', name).strip(' .') or 'file'
    return name[:120]


def looks_like_text(head):
    if b'\x00' in head:
        return False
    for encoding in ('utf-8', 'cp1252'):
        try:
            head.decode(encoding)
            return True
        except UnicodeDecodeError:
            continue
    return False


def check(upload):
    """Return (extension, content type) for an allowed file, or raise UploadError."""
    ext = Path(upload.name or '').suffix.lower().lstrip('.')
    if ext not in TYPES:
        raise UploadError(f'Please attach a {ALLOWED_LABEL} file.')
    if upload.size > MAX_BYTES:
        raise UploadError(f'The file is too large. The limit is {MAX_LABEL}.')
    if upload.size == 0:
        raise UploadError('The file is empty.')
    upload.seek(0)
    head = upload.read(4096)
    upload.seek(0)
    content_type, magic = TYPES[ext]
    ok = magic(head) if magic else looks_like_text(head)
    if not ok:
        raise UploadError(f'This file does not look like a real .{ext} file. Please attach the original file.')
    return ext, content_type


def save(upload, inquiry_uuid, ext):
    """Save under a random name in the inquiry's own folder. Returns the stored path (relative)."""
    path = f'{inquiry_uuid}/{uuid.uuid4().hex}.{ext}'
    return private_storage().save(path, upload)
