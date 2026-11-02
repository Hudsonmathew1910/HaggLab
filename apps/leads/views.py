from django.contrib.admin.views.decorators import staff_member_required
from django.http import FileResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django_ratelimit.decorators import ratelimit
from .forms import InquiryForm
from .offers import inr_rate
from . import uploads
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

    # "I found you on Fiverr" on the form shows the Fiverr page once; it does not switch the whole site
    if fiverr_on and request.GET.get('origin') == 'fiverr':
        is_fiverr = True

    if is_fiverr:
        return render(request, 'pages/start_fiverr.html', {
            'IS_FIVERR': True,
        })

    if request.method == 'POST':
        form = InquiryForm(request.POST, request.FILES)
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
            form.save_files(inquiry)

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
        # A service page's "Choose this package" link fills in the service and package
        initial = {k: request.GET[k] for k in ('service', 'package_choice') if request.GET.get(k)}
        form = InquiryForm(initial=initial)

    return render(request, 'pages/start.html', {
        'form': form,
        'offers': form.offers,
        'inr_rate': inr_rate() or '',
        'upload_accept': uploads.ACCEPT, 'upload_types': uploads.ALLOWED_LABEL, 'upload_max': uploads.MAX_LABEL,
        'IS_FIVERR': False,
    })

def thank_you_view(request):
    submitted_email = request.session.get('inquiry_submitted_email', '')
    return render(request, 'pages/thank_you.html', {
        'submitted_email': submitted_email,
    })


@staff_member_required
def inquiry_file_view(request, pk):
    """Download a file attached to an inquiry. Staff only, always as a download, never shown inline."""
    from .models import InquiryFile
    from .uploads import private_storage
    item = get_object_or_404(InquiryFile, pk=pk)
    storage = private_storage()
    if not storage.exists(item.path):
        raise Http404('File not found')
    response = FileResponse(storage.open(item.path, 'rb'), as_attachment=True, filename=item.original_name,
                            content_type=item.content_type)
    response['X-Content-Type-Options'] = 'nosniff'
    response['Content-Security-Policy'] = "default-src 'none'; sandbox"
    response['Cache-Control'] = 'private, no-store'
    AuditEvent.objects.create(actor=request.user.get_username(), action='INQUIRY_FILE_DOWNLOADED',
                              object_repr=f'Inquiry file #{item.pk}', ip_address=request.META.get('REMOTE_ADDR', ''),
                              details=item.original_name)
    return response
