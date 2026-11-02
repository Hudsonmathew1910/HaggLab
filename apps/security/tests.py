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
            name="Client A", email="a@a.com", service="ai_chatbots",
            problem="Problem A", data_available="none", timeline="asap", consent=True
        )
        inq2 = Inquiry.objects.create(
            name="Client B", email="b@b.com", service="buy_or_book",
            problem="Problem B", data_available="none", timeline="asap", consent=True
        )
        self.assertIsNotNone(inq1.uuid)
        self.assertIsNotNone(inq2.uuid)
        self.assertNotEqual(inq1.uuid, inq2.uuid)


from django.contrib.auth import get_user_model
from django.core.cache import cache as _cache
from django.test import override_settings as _override
from django.urls import reverse as _reverse


class AdminTwoFactorTest(TestCase):
    """apps/security/admin_site.py: two-factor admin login without locking anyone out."""
    password = 'a-long-test-password-123'

    def setUp(self):
        _cache.clear()
        self.user = get_user_model().objects.create_user('owner', 'owner@example.com', self.password, is_staff=True)
        self.login_url = _reverse('admin:login')
        self.index_url = _reverse('admin:index')

    def login(self, token=''):
        return self.client.post(self.login_url, {'username': 'owner', 'password': self.password,
                                                 'otp_token': token, 'next': self.index_url})

    def add_device(self):
        from django_otp.plugins.otp_totp.models import TOTPDevice
        return TOTPDevice.objects.create(user=self.user, name='phone', confirmed=True)

    def code(self, device):
        from django_otp.oath import totp
        return str(totp(device.bin_key, device.step, device.t0, device.digits, device.drift)).zfill(device.digits)

    def test_account_without_a_device_logs_in_with_the_password(self):
        self.assertRedirects(self.login(), self.index_url)
        self.assertEqual(self.client.get(self.index_url).status_code, 200)

    def test_account_with_a_device_needs_the_code(self):
        device = self.add_device()
        r = self.login()
        self.assertEqual(r.status_code, 200)  # stays on the login page
        self.assertNotEqual(self.client.get(self.index_url).status_code, 200)
        self.assertRedirects(self.login(self.code(device)), self.index_url)
        self.assertEqual(self.client.get(self.index_url).status_code, 200)

    def test_wrong_code_is_refused(self):
        self.add_device()
        self.assertEqual(self.login('000000').status_code, 200)
        self.assertNotEqual(self.client.get(self.index_url).status_code, 200)

    def test_password_only_session_is_refused_when_the_device_existed_at_login(self):
        self.add_device()                   # the account already has an authenticator...
        self.client.force_login(self.user)  # ...but this session skipped the code (e.g. an old session)
        r = self.client.get(self.index_url)
        self.assertEqual(r.status_code, 302)
        self.assertIn(self.login_url, r['Location'])

    @_override(ADMIN_REQUIRE_OTP=True)
    def test_require_for_everyone_switch(self):
        self.assertEqual(self.login().status_code, 200)
        self.assertNotEqual(self.client.get(self.index_url).status_code, 200)

    def test_non_staff_cannot_enter(self):
        get_user_model().objects.create_user('visitor', 'v@example.com', self.password)
        r = self.client.post(self.login_url, {'username': 'visitor', 'password': self.password})
        self.assertEqual(r.status_code, 200)
        self.assertNotEqual(self.client.get(self.index_url).status_code, 200)

    @_override(RATELIMIT_ENABLE=True, ADMIN_LOGIN_RATE='3/h')  # per hour: a test can't straddle the window
    def test_password_guessing_is_rate_limited(self):
        codes = [self.client.post(self.login_url, {'username': 'owner', 'password': 'wrong'}).status_code
                 for _ in range(4)]
        self.assertIn(codes[-1], (403, 429))  # blocked (403 = django-ratelimit's default refusal)
        self.assertEqual(codes[:3], [200, 200, 200])


class RowLevelSecuritySqlTest(TestCase):
    """The session cookie is visitor input: it must reach PostgreSQL as a parameter, never inside the SQL text."""

    def test_malicious_session_cookie_is_passed_as_a_parameter(self):
        from unittest import mock
        from django.http import HttpResponse
        from django.test import RequestFactory
        from django.contrib.auth.models import AnonymousUser
        from django.contrib.sessions.backends.db import SessionStore
        from apps.security.middleware import RowLevelSecurityMiddleware

        evil = "x'; DROP TABLE auth_user; --"
        request = RequestFactory().get('/')
        request.user = AnonymousUser()
        request.session = SessionStore(session_key=evil)
        cursor = mock.MagicMock()
        fake_db = mock.MagicMock(vendor='postgresql')  # pretend to be PostgreSQL, where the middleware runs
        fake_db.cursor.return_value.__enter__.return_value = cursor
        with mock.patch('apps.security.middleware.connection', fake_db):
            RowLevelSecurityMiddleware(lambda r: HttpResponse('ok'))(request)
        self.assertTrue(cursor.execute.called)
        for call in cursor.execute.call_args_list:
            sql = call.args[0]
            self.assertNotIn(evil, sql)
            self.assertNotIn('DROP TABLE', sql)
        params = [p for call in cursor.execute.call_args_list if len(call.args) > 1 for p in call.args[1]]
        self.assertIn(evil, params)  # sent safely, as a parameter


class AdminTwoFactorSetupTest(AdminTwoFactorTest):  # reuses the helpers (and re-runs the base tests)
    """Adding a device must not log you out before you can scan its QR code."""

    def test_adding_a_device_during_the_session_does_not_log_you_out(self):
        from django.utils import timezone
        from datetime import timedelta
        self.assertRedirects(self.login(), self.index_url)
        get_user_model().objects.filter(pk=self.user.pk).update(last_login=timezone.now() - timedelta(minutes=1))
        device = self.add_device()  # created after this session logged in
        self.assertEqual(self.client.get(self.index_url).status_code, 200)
        # ... but the next login needs the code
        self.client.logout()
        self.assertEqual(self.login().status_code, 200)
        self.assertRedirects(self.login(self.code(device)), self.index_url)

    def test_rescue_command_shows_the_qr_and_resets(self):
        from io import StringIO
        from django.core.management import call_command
        self.add_device()
        out = StringIO()
        call_command('admin_2fa', 'qr', 'owner', stdout=out)
        self.assertIn('Scan this', out.getvalue())
        call_command('admin_2fa', 'reset', 'owner', stdout=StringIO())
        self.assertRedirects(self.login(), self.index_url)  # password only again
