import logging
import re
import urllib.request
import urllib.parse
import json
from django import forms
from django.conf import settings
from .models import Inquiry

logger = logging.getLogger(__name__)

class InquiryForm(forms.ModelForm):
    # Honeypot field - must stay empty
    website_url = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'autocomplete': 'off',
            'tabindex': '-1',
        })
    )

    class Meta:
        model = Inquiry
        fields = [
            'name', 'email', 'service', 'problem',
            'data_available', 'timeline', 'consent',
            'budget_band', 'business', 'source'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Jane Doe'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'jane@company.com'}),
            'service': forms.Select(attrs={'class': 'form-control'}),
            'problem': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'aria-describedby': 'problem-hint',
            }),
            'data_available': forms.Select(attrs={'class': 'form-control'}),
            'timeline': forms.Select(attrs={'class': 'form-control'}),
            'budget_band': forms.TextInput(attrs={'class': 'form-control'}),
            'business': forms.TextInput(attrs={'class': 'form-control'}),
            'source': forms.TextInput(attrs={'class': 'form-control'}),
            'consent': forms.CheckboxInput(),
        }

    def clean_website_url(self):
        # Honeypot validation
        value = self.cleaned_data.get('website_url')
        if value:
            raise forms.ValidationError("Spam detected.")
        return value

    def clean_consent(self):
        consent = self.cleaned_data.get('consent')
        if not consent:
            raise forms.ValidationError("You must agree to be contacted about this project.")
        return consent

    def clean(self):
        cleaned_data = super().clean()
        secret_key = getattr(settings, 'TURNSTILE_SECRET_KEY', '')
        if not secret_key:
            # Turnstile is off (local development and tests). Production requires the keys.
            return cleaned_data

        # The Cloudflare widget posts its token under this name
        token = self.data.get('cf-turnstile-response', '')
        if not token:
            raise forms.ValidationError("Please complete the security check and send again.")

        outcome = verify_turnstile(secret_key, token)
        if outcome is None:
            # Cloudflare could not be reached: accept the message rather than lose a real lead
            logger.warning("Turnstile verification unavailable; inquiry accepted without it.")
        elif not outcome.get('success', False):
            raise forms.ValidationError("Security verification failed. Please try again.")
        return cleaned_data


def verify_turnstile(secret_key, token):
    """Ask Cloudflare to verify a Turnstile token. Returns the JSON reply, or None if unreachable."""
    data = urllib.parse.urlencode({'secret': secret_key, 'response': token}).encode('utf-8')
    req = urllib.request.Request('https://challenges.cloudflare.com/turnstile/v0/siteverify', data=data)
    try:
        with urllib.request.urlopen(req, timeout=5) as res:
            return json.loads(res.read().decode('utf-8'))
    except (OSError, ValueError):
        return None
