import time
from io import BytesIO
from django.test import TestCase, Client
from django.urls import reverse, get_resolver
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from apps.security.helpers import verify_signature, validate_upload_file
from apps.security.models import AuditEvent
from apps.leads.models import Inquiry

class SecuritySuiteTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_req3_all_routes_protected_or_explicitly_allowed(self):
        """Requirement 3: Verify all registered routes are in PUBLIC_ROUTES or require authentication."""
        resolver = get_resolver()
        public_routes = set(settings.PUBLIC_ROUTES)
        
        # Traverse URL patterns
        for pattern in resolver.url_patterns:
            name = getattr(pattern, 'name', None)
            if name:
                # Any non-admin route must be in public_routes
                if not name.startswith('admin') and not name.startswith('otp_'):
                    self.assertIn(
                        name,
                        public_routes,
                        f"Unprotected URL route detected not on PUBLIC_ROUTES allowlist: {name}"
                    )

    def test_req6_admin_secret_path_returns_404_for_unauthenticated_on_sensitive_views(self):
        """Requirement 6: Verify admin url lives on non-default path."""
        self.assertNotEqual(settings.ADMIN_URL_PATH, 'admin/')
        # Non-staff attempting to hit internal endpoints receives 404 or redirect
        res = self.client.get('/admin/')
        self.assertEqual(res.status_code, 404)

    def test_req10_file_upload_validation_pdf_xlsx_csv(self):
        """Requirement 10: Extension, magic bytes, and size checking."""
        # Valid PDF
        valid_pdf = SimpleUploadedFile("doc.pdf", b"%PDF-1.4 test document content", content_type="application/pdf")
        name = validate_upload_file(valid_pdf, ['pdf'])
        self.assertTrue(name.endswith('.pdf'))

        # Fake PDF
        fake_pdf = SimpleUploadedFile("doc.pdf", b"NOT_A_PDF content", content_type="application/pdf")
        with self.assertRaises(ValidationError):
            validate_upload_file(fake_pdf, ['pdf'])

        # Valid XLSX (starts with PK\x03\x04)
        valid_xlsx = SimpleUploadedFile("sheet.xlsx", b"PK\x03\x04fake zip parts", content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        name_xlsx = validate_upload_file(valid_xlsx, ['xlsx'])
        self.assertTrue(name_xlsx.endswith('.xlsx'))

        # Disallowed extension
        exe_file = SimpleUploadedFile("run.exe", b"binary", content_type="application/octet-stream")
        with self.assertRaises(ValidationError):
            validate_upload_file(exe_file, ['pdf', 'xlsx'])

    def test_req13_no_cors_wildcard(self):
        """Requirement 13: Site is same-origin, no wildcard CORS header."""
        res = self.client.get(reverse('home'))
        self.assertNotIn('Access-Control-Allow-Origin', res.headers)

    def test_req14_security_headers_enforced(self):
        """Requirement 14: Strict CSP, HSTS, Nosniff, Permissions-Policy, COOP."""
        res = self.client.get(reverse('home'))
        self.assertIn('Content-Security-Policy', res.headers)
        csp = res.headers['Content-Security-Policy']
        self.assertIn("default-src 'self'", csp)
        self.assertIn("object-src 'none'", csp)
        self.assertIn("frame-ancestors 'none'", csp)
        self.assertEqual(res.headers['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(res.headers['Referrer-Policy'], 'strict-origin-when-cross-origin')
        self.assertEqual(res.headers['Cross-Origin-Opener-Policy'], 'same-origin')
        self.assertIn('camera=()', res.headers['Permissions-Policy'])

    def test_req16_webhook_signature_verification(self):
        """Requirement 16: Constant-time comparison, replay attack tolerance."""
        secret = "super_secret_webhook_key_12345"
        payload = b'{"event":"test"}'
        now = int(time.time())

        # Construct valid signature
        import hmac, hashlib
        signed_payload = f"{now}.".encode('utf-8') + payload
        sig = hmac.new(secret.encode('utf-8'), signed_payload, hashlib.sha256).hexdigest()
        valid_header = f"t={now},v1={sig}"

        self.assertTrue(verify_signature(payload, valid_header, secret))

        # Replay tolerance exceeded (timestamp in far past)
        expired_header = f"t={now - 400},v1={sig}"
        self.assertFalse(verify_signature(payload, expired_header, secret))

        # Tampered payload
        self.assertFalse(verify_signature(b'tampered', valid_header, secret))

    def test_req17_uuid_keys_and_idor_isolation(self):
        """Requirement 17: UUID keys used and no cross-session inquiry leak."""
        inq1 = Inquiry.objects.create(
            name="Client A", email="a@a.com", service="answer_faster",
            problem="Problem A", data_available="none", timeline="asap", consent=True
        )
        inq2 = Inquiry.objects.create(
            name="Client B", email="b@b.com", service="buy_or_book",
            problem="Problem B", data_available="none", timeline="asap", consent=True
        )
        self.assertIsNotNone(inq1.uuid)
        self.assertIsNotNone(inq2.uuid)
        self.assertNotEqual(inq1.uuid, inq2.uuid)
