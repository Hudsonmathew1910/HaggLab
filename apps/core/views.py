from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.http import Http404, HttpResponse, JsonResponse
from django.template.loader import render_to_string
from apps.content.models import Solution, Project, FAQ, SiteSetting, FiverrGig
from apps.core.fiverr import faqs_for_site, fiverr_enabled
from apps.content.gigs import gig_for
from apps.core.built import built_products

def home_view(request):
    solutions = Solution.objects.filter(published=True).order_by('order')[:5]
    featured_projects = Project.objects.public().order_by('order')[:3]
    # Hero shows a project that is not repeated in the featured list below it
    hero_project = (Project.objects.public().filter(slug='supportflow').first()
                    or Project.objects.public().exclude(id__in=[p.id for p in featured_projects]).order_by('order').first())
    faqs = faqs_for_site(FAQ.objects.filter(published=True, page__in=['all', 'home']).order_by('order')[:6])
    stats = {
        'solutions': Solution.objects.filter(published=True).count(),
        'projects': Project.objects.public().count(),
        'live_demos': Project.objects.public().count(),
        'prototypes': 0,
    }
    return render(request, 'pages/home.html', {
        'solutions': solutions,
        'featured_projects': featured_projects,
        'hero_project': hero_project,
        'built': built_products(),
        'faqs': faqs,
        'live_demos': stats['live_demos'],
        'stats': stats,
    })

def solutions_hub_view(request):
    solutions = Solution.objects.filter(published=True).order_by('order')
    return render(request, 'pages/solutions_hub.html', {
        'solutions': solutions,
    })

def solution_detail_view(request, slug):
    solution = get_object_or_404(Solution, slug=slug, published=True)
    matching_projects = solution.projects.public().order_by('order')
    faqs = faqs_for_site(FAQ.objects.filter(published=True, solution_slug=slug).order_by('order'))
    # The service's own Fiverr gig, ticked under Services on the gig (empty = contact form, no Fiverr button)
    gig = FiverrGig.objects.filter(active=True, services=solution).order_by('order', 'id').first()
    solution_gig = gig.url if gig else ''
    return render(request, 'pages/solution_detail.html', {
        'solution': solution,
        'solution_gig': solution_gig,
        'matching_projects': matching_projects,
        'faqs': faqs,
    })

def projects_hub_view(request):
    solution_filter = request.GET.get('solution', '').strip()
    projects = Project.objects.public()
    if solution_filter:
        projects = projects.filter(solutions__slug=solution_filter)
    solutions = Solution.objects.filter(published=True).order_by('order')
    return render(request, 'pages/projects_hub.html', {
        'projects': projects.distinct().order_by('order'),
        'solutions': solutions,
        'current_solution': solution_filter,
    })

def project_detail_view(request, slug):
    project = get_object_or_404(Project.objects.public(), slug=slug)
    others = Project.objects.public().exclude(id=project.id)
    # Prefer projects that solve the same problem, then fill up in normal order
    related_projects = list(others.filter(solutions__in=project.solutions.all()).distinct().order_by('order')[:3])
    if len(related_projects) < 3:
        taken = [p.id for p in related_projects]
        related_projects += list(others.exclude(id__in=taken).order_by('order')[:3 - len(related_projects)])
    return render(request, 'pages/project_detail.html', {
        'project': project,
        'related_projects': related_projects,
        'gig': gig_for(project),
    })

def process_view(request):
    return render(request, 'pages/process.html', {})

def security_view(request):
    return render(request, 'pages/security.html', {})

def about_view(request):
    return render(request, 'pages/about.html', {
        'built': built_products(),
    })

def faq_view(request):
    faqs = faqs_for_site(FAQ.objects.filter(published=True).order_by('order'))
    return render(request, 'pages/faq.html', {
        'faqs': faqs,
    })

def hire_fiverr_view(request):
    if not fiverr_enabled():
        return redirect('start_project')  # Fiverr is switched off: old links still lead somewhere useful
    public = Project.objects.public()
    gigs = [{'title': gig.title, 'url': gig.url, 'projects': list(gig.projects.filter(id__in=public).order_by('order'))}
            for gig in FiverrGig.objects.filter(active=True).order_by('order', 'id')]
    return render(request, 'pages/hire_fiverr.html', {
        'gigs': gigs,
    })

def privacy_view(request):
    return render(request, 'pages/privacy.html', {})

def terms_view(request):
    return render(request, 'pages/terms.html', {})

def styleguide_view(request):
    # Internal design reference: only on this computer (DEBUG), a normal 404 on the live site
    if not settings.DEBUG:
        raise Http404
    return render(request, 'pages/styleguide.html', {})

def rate_limited_view(request, exception=None):
    return render(request, 'pages/429.html', status=429)

def custom_404_view(request, exception=None):
    return render(request, 'pages/404.html', status=404)

def custom_500_view(request):
    # Rendered without the request so no context processor (and no database query) runs
    return HttpResponse(render_to_string('pages/500.html'), status=500)

def health_check(request):
    return JsonResponse({'status': 'ok'})

def robots_txt_view(request):
    content = "User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /private_uploads/\nSitemap: /sitemap.xml\n"
    return HttpResponse(content, content_type="text/plain")

def sitemap_xml_view(request):
    solutions = Solution.objects.filter(published=True)
    projects = Project.objects.public()
    return render(request, 'pages/sitemap.xml', {
        'fiverr_on': fiverr_enabled(),
        'solutions': solutions,
        'projects': projects,
    }, content_type="application/xml")
