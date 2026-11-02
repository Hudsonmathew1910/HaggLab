"""
The admin site with two-factor login (django-otp TOTP: Google Authenticator, Authy, 1Password and similar).

Rules
- A staff account that has a confirmed authenticator device must enter its 6-digit code to log in, and is refused
  by the admin until the code is verified.
- A staff account with no device yet logs in with its password only, so nobody is locked out before setting one up.
- ADMIN_REQUIRE_OTP=True (environment) makes the code required for every staff account, with or without a device.
- Login attempts are limited per IP address (ADMIN_LOGIN_RATE), against password guessing.

Add a device: admin > OTP_TOTP > TOTP devices > Add, pick your user, save, open the QR code with your
authenticator app, then enter one code to confirm it (or tick Confirmed after scanning).
"""
from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.forms import AdminAuthenticationForm
from django.utils.decorators import method_decorator
from django_otp import user_has_device
from django_otp.forms import OTPAuthenticationFormMixin
from django_ratelimit.decorators import ratelimit


def otp_required_for(user):
    """True when this user must pass the authenticator code at login."""
    if getattr(settings, 'ADMIN_REQUIRE_OTP', False):
        return True
    return user_has_device(user, confirmed=True)


def device_existed_at_login(user):
    """True if the user had a confirmed device created before (or when) the current session logged in."""
    from django_otp.plugins.otp_totp.models import TOTPDevice
    devices = TOTPDevice.objects.filter(user=user, confirmed=True)
    if user.last_login is None:
        return devices.exists()
    return devices.filter(created_at__lte=user.last_login).exists()


class StudioAdminLoginForm(AdminAuthenticationForm, OTPAuthenticationFormMixin):
    otp_device = forms.CharField(required=False, widget=forms.Select)
    otp_token = forms.CharField(required=False, max_length=12, label='Authenticator code',
                                widget=forms.TextInput(attrs={'autocomplete': 'one-time-code', 'inputmode': 'numeric'}))
    otp_challenge = forms.CharField(required=False)

    def _chosen_device(self, user):
        """The login page has one code box and no device list: use this user's own confirmed authenticator."""
        device = super()._chosen_device(user)
        if device is None:
            from django_otp import devices_for_user
            device = next(iter(devices_for_user(user, confirmed=True, for_verify=True)), None)
        return device

    def clean(self):
        self.cleaned_data = super().clean()  # username, password, active staff
        user = self.get_user()
        if user is not None and otp_required_for(user):
            self.clean_otp(user)  # raises a form error unless the code is right
        return self.cleaned_data


def admin_login_rate(group, request):
    return getattr(settings, 'ADMIN_LOGIN_RATE', '10/m')


class StudioAdminSite(admin.AdminSite):
    login_form = StudioAdminLoginForm

    def has_permission(self, request):
        if not super().has_permission(request):
            return False
        user = request.user
        if getattr(user, 'is_verified', lambda: False)():
            return True
        # Password-only session: refused only if a device already existed when this session logged in.
        # A device added during this session (you are setting it up and still need its QR code) is
        # required from the next login, so adding one never locks you out halfway through.
        if getattr(settings, 'ADMIN_REQUIRE_OTP', False):
            return False
        return not device_existed_at_login(user)

    @method_decorator(ratelimit(key='ip', rate=admin_login_rate, method='POST', block=True))
    def login(self, request, extra_context=None):
        return super().login(request, extra_context)
