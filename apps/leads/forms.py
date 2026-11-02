import logging
import re
import urllib.request
import urllib.parse
import json
from django import forms
from django.conf import settings
from .models import Inquiry
from .offers import offers, inr_rate, money
from . import uploads

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

    # A package (required for a service that has packages) and extras of that service (apps/leads/offers.py)
    package_choice = forms.ChoiceField(required=False)
    extra_choices = forms.MultipleChoiceField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.offers = offers()
        self.package_labels = {p['value']: p['label'] for o in self.offers for p in o['packages']}
        self.extra_labels = {e['value']: e['label'] for o in self.offers for e in o['extras']}
        self.package_prices = {p['value']: p.get('price', 0) for o in self.offers for p in o['packages']}
        self.extra_prices = {e['value']: e.get('price', 0) for o in self.offers for e in o['extras']}
        self.fields['package_choice'].choices = [('', 'No package yet')] + list(self.package_labels.items())
        self.fields['extra_choices'].choices = list(self.extra_labels.items())
        # Which fields are required depends on the service, so they are checked in clean():
        # a service with packages needs a package and its order questions; a custom project needs
        # the problem, the data question and "When do you need it?".
        for name in ('timeline', 'problem', 'data_available'):
            self.fields[name].required = False
        # Length limits on free text (the database column has none): stops oversized spam submissions
        from django.core.validators import MaxLengthValidator
        self.fields['problem'].validators.append(MaxLengthValidator(5000))
        self.fields['problem'].widget.attrs['maxlength'] = 5000
        self.fields['timeline'].choices = [c for c in self.fields['timeline'].choices if c[0] != 'package']
        self.fields['data_available'].choices = [c for c in self.fields['data_available'].choices
                                                 if c[0] != 'see_answers']
        self.offer_codes = {o['code'] for o in self.offers}
        self.question_errors = {}
        self.pending_files = []  # (question, upload, extension, content type), saved by save_files()

    def ask_name(self, code, i):
        return f'ask_{code}_{i}'

    @property
    def questions(self):
        """The order questions of every service, with the visitor's answers, for the template."""
        groups = []
        for o in self.offers:
            items = []
            for i, q in enumerate(o.get('requirements') or []):
                name = self.ask_name(o['code'], i)
                items.append({'name': name, 'question': q.get('question', ''), 'kind': q.get('kind', 'Free text'),
                              'options': q.get('options') or [], 'value': self.data.get(name, '') if self.is_bound else '',
                              'error': self.question_errors.get(name, '')})
            if items:
                groups.append({'code': o['code'], 'items': items})
        return groups

    def clean_answers(self, code):
        """Check and collect the answers to one service's order questions."""
        answers = []
        offer = next(o for o in self.offers if o['code'] == code)
        for i, q in enumerate(offer.get('requirements') or []):
            name = self.ask_name(code, i)
            value = (self.data.get(name) or '').strip()[:1000]
            kind = q.get('kind', 'Free text')
            if kind == 'Multiple choice' and value and value not in (q.get('options') or []):
                value = ''
            if kind == 'Attachment':
                # Optional file upload, checked for type, size and content (apps/leads/uploads.py)
                value = ''
                upload = self.files.get(name) if self.files else None
                if upload:
                    try:
                        ext, content_type = uploads.check(upload)
                    except uploads.UploadError as exc:
                        self.question_errors[name] = str(exc)
                    else:
                        value = uploads.clean_name(upload.name)
                        self.pending_files.append((q.get('question', ''), upload, ext, content_type))
            elif not value:
                self.question_errors[name] = 'Please answer this question.'
            answers.append({'question': q.get('question', ''), 'answer': value})
        return answers

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
        # Packages and extras belong to one service: drop any picked for a different service
        prefix = f"{cleaned_data.get('service', '')}|"
        if not (cleaned_data.get('package_choice') or '').startswith(prefix):
            cleaned_data['package_choice'] = ''
        cleaned_data['extra_choices'] = [v for v in cleaned_data.get('extra_choices') or [] if v.startswith(prefix)]
        service = cleaned_data.get('service', '')
        cleaned_data['answers'] = []
        if service in self.offer_codes:
            # A service with packages: the package, extras and order questions say what is needed and when
            package = cleaned_data['package_choice']
            if not package:
                self.add_error('package_choice', 'Please choose a package.')
            answers = self.clean_answers(service)
            if self.question_errors:
                self.add_error(None, 'Please answer the order questions marked below.')
            cleaned_data['answers'] = answers
            total = self.package_prices.get(package, 0) + sum(
                self.extra_prices.get(v, 0) for v in cleaned_data['extra_choices'])
            cleaned_data['timeline'] = 'package'
            cleaned_data['budget_band'] = f'Package total: {money(total, inr_rate())}'
            cleaned_data['data_available'] = 'see_answers'
            cleaned_data['problem'] = (answers[0]['answer'] if answers and answers[0]['answer']
                                       else cleaned_data.get('problem') or '')
        elif service:
            # A custom project ("Not sure yet") or a service with no packages
            cleaned_data['package_choice'] = ''
            cleaned_data['extra_choices'] = []
            if not (cleaned_data.get('problem') or '').strip():
                self.add_error('problem', 'Please describe the problem.')
            if not cleaned_data.get('data_available'):
                self.add_error('data_available', 'Please choose an answer.')
            if not cleaned_data.get('timeline'):
                self.add_error('timeline', 'Please choose when you need it.')
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

    def save_files(self, inquiry):
        """Store the attached files privately, once the inquiry has been saved."""
        from .models import InquiryFile
        for question, upload, ext, content_type in self.pending_files:
            path = uploads.save(upload, inquiry.uuid, ext)
            InquiryFile.objects.create(inquiry=inquiry, question=question[:300], path=path,
                                       original_name=uploads.clean_name(upload.name), content_type=content_type,
                                       size=upload.size)

    def save(self, commit=True):
        inquiry = super().save(commit=False)
        inquiry.package = self.package_labels.get(self.cleaned_data.get('package_choice'), '')
        inquiry.extras = '\n'.join(self.extra_labels[v] for v in self.cleaned_data.get('extra_choices', []))
        inquiry.answers = self.cleaned_data.get('answers', [])
        if commit:
            inquiry.save()
        return inquiry


def verify_turnstile(secret_key, token):
    """Ask Cloudflare to verify a Turnstile token. Returns the JSON reply, or None if unreachable."""
    data = urllib.parse.urlencode({'secret': secret_key, 'response': token}).encode('utf-8')
    req = urllib.request.Request('https://challenges.cloudflare.com/turnstile/v0/siteverify', data=data)
    try:
        with urllib.request.urlopen(req, timeout=5) as res:
            return json.loads(res.read().decode('utf-8'))
    except (OSError, ValueError):
        return None
