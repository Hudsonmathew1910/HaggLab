"""
Two-factor helpers for admin accounts, from the terminal (works even when you cannot log in).

    python manage.py admin_2fa status  USERNAME   # does this account have an authenticator device?
    python manage.py admin_2fa qr      USERNAME   # show the QR code here, to scan with your authenticator app
    python manage.py admin_2fa reset   USERNAME   # remove the account's devices (back to password-only login)

The QR code is a secret: anyone who scans it can make your login codes. Clear the terminal after scanning.
"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Show, check or reset the two-factor authenticator device of an admin account.'

    def add_arguments(self, parser):
        parser.add_argument('action', choices=['status', 'qr', 'reset'])
        parser.add_argument('username')

    def handle(self, action, username, **options):
        from django_otp.plugins.otp_totp.models import TOTPDevice
        user = get_user_model().objects.filter(username=username).first()
        if not user:
            raise CommandError(f'No account named "{username}".')
        devices = TOTPDevice.objects.filter(user=user)

        if action == 'status':
            if not devices:
                self.stdout.write(f'{username}: no authenticator device (password-only login).')
            for d in devices:
                self.stdout.write(f'{username}: device "{d.name}", confirmed={d.confirmed}, '
                                  f'created {d.created_at:%Y-%m-%d %H:%M}, last used {d.last_used_at or "never"}')
            return

        if action == 'reset':
            count = devices.count()
            devices.delete()
            self.stdout.write(self.style.SUCCESS(
                f'Removed {count} device(s). {username} can now log in with the password only.'))
            return

        device = devices.filter(confirmed=True).order_by('-created_at').first() or devices.order_by('-created_at').first()
        if not device:
            raise CommandError(f'{username} has no device. Add one in the admin first (OTP_TOTP > TOTP devices).')
        try:
            import qrcode
        except ImportError:
            raise CommandError('The qrcode package is missing: run  pip install -r requirements.txt')
        qr = qrcode.QRCode(border=2)
        qr.add_data(device.config_url)
        qr.make(fit=True)
        self.stdout.write(f'Scan this with your authenticator app (device "{device.name}"):\n')
        qr.print_ascii(out=self.stdout, invert=True)
        self.stdout.write(self.style.WARNING(
            '\nKeep this private: clear the terminal (cls) after scanning. Then log in with the 6-digit code.'))
