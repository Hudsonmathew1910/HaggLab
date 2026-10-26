import hmac
import hashlib
import time
import uuid
from pathlib import Path
from django.core.exceptions import ValidationError

def verify_signature(payload_bytes, signature_header, secret_key, tolerance_seconds=300):
    """
    Requirement 16: Verify webhook signatures.
    - Constant-time comparison
    - Timestamp replay protection with tolerance
    - HMAC-SHA256 signature
    Signature header format expected: t=<timestamp>,v1=<signature_hex>
    """
    if not signature_header or not secret_key:
        return False

    parts = dict(item.split('=', 1) for item in signature_header.split(',') if '=' in item)
    timestamp_str = parts.get('t')
    received_sig = parts.get('v1')

    if not timestamp_str or not received_sig:
        return False

    try:
        timestamp = int(timestamp_str)
    except ValueError:
        return False

    current_time = int(time.time())
    if abs(current_time - timestamp) > tolerance_seconds:
        # Replay attack protection: expired or skewed timestamp
        return False

    signed_payload = f"{timestamp}.".encode('utf-8') + payload_bytes
    expected_sig = hmac.new(
        secret_key.encode('utf-8'),
        signed_payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected_sig, received_sig)


def validate_upload_file(file_obj, allowed_extensions, max_bytes=5 * 1024 * 1024):
    """
    Requirement 10: Check file upload types, sizes, and magic bytes.
    - PDF: must begin with %PDF
    - XLSX: must have ZIP header (PK\x03\x04)
    - CSV: valid UTF-8 text
    - Generates a safe random UUID filename
    """
    if file_obj.size > max_bytes:
        raise ValidationError(f"File exceeds maximum allowed size of {max_bytes // (1024 * 1024)} MB.")

    filename = file_obj.name.lower()
    ext = Path(filename).suffix.lstrip('.')
    if ext not in allowed_extensions:
        raise ValidationError(f"File extension '.{ext}' is not permitted. Allowed: {', '.join(allowed_extensions)}.")

    header = file_obj.read(1024)
    file_obj.seek(0)

    if ext == 'pdf':
        if not header.startswith(b'%PDF'):
            raise ValidationError("File failed PDF magic byte verification.")
    elif ext == 'xlsx':
        # ZIP magic bytes PK\x03\x04
        if not header.startswith(b'PK\x03\x04'):
            raise ValidationError("File failed XLSX spreadsheet magic byte verification.")
    elif ext == 'csv':
        try:
            header.decode('utf-8')
        except UnicodeDecodeError:
            raise ValidationError("File failed CSV text verification.")

    safe_name = f"{uuid.uuid4().hex}.{ext}"
    return safe_name
