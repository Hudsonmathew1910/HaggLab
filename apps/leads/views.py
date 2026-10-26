from django.shortcuts import render, redirect
from django.conf import settings
from django_ratelimit.decorators import ratelimit
from .forms import InquiryForm
from .notify import notify_owner
from apps.core.fiverr import fiverr_enabled
from apps.security.models import AuditEvent

@ratelimit(key='ip', rate='5/m', block=True)
def start_project_view(request):
    """
    Handles Path A (Fiverr visitors) and Path B (Direct visitors).
    Fiverr visitors are never shown email, phone, or form.
    Direct visitors submit a 6-field required form with Turnstile & honeypot.
    """
    fiverr_on = fiverr_enabled()
    is_fiverr = fiverr_on and (getattr(request, 'is_fiverr', False) or request.session.get('is_fiverr', False))

    # If visitor selected "I found you on Fiverr" option on page
    if fiverr_on and request.GET.get('origin') == 'fiverr':
        request.session['is_fiverr'] = True
        is_fiverr = True

    if is_fiverr:
        return render(request, 'pages/start_fiverr.html', {
            'IS_FIVERR': True,
        })

    if request.method == 'POST':
        form = InquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save(commit=False)
            # Store sanitized client IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0].strip()
            else:
                ip = request.META.get('REMOTE_ADDR', '')
            inquiry.ip_address = ip
            inquiry.save()

            # Audit event
            AuditEvent.objects.create(
                actor=inquiry.email,
                action='INQUIRY_CREATED',
                object_repr=f"Inquiry #{inquiry.id}",
                ip_address=ip,
                details=f"New project request for {inquiry.get_service_display()}"
            )

            # Email the owner (the inquiry is already saved, so a failed email loses nothing)
            notify_owner(inquiry)

            request.session['inquiry_submitted_email'] = inquiry.email
            return redirect('thank_you')
    else:
        form = InquiryForm()

    return render(request, 'pages/start.html', {
        'form': form,
        'IS_FIVERR': False,
    })

def thank_you_view(request):
    submitted_email = request.session.get('inquiry_submitted_email', '')
    return render(request, 'pages/thank_you.html', {
        'submitted_email': submitted_email,
    })
