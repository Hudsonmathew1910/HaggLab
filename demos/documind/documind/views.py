import json
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from .retrieval import query_handbook, HANDBOOK_PAGES

def index_view(request):
    question = request.GET.get('q', '').strip()
    result = None
    if question:
        result = query_handbook(question)

    return render(request, 'index.html', {
        'question': question,
        'result': result,
        'pages': HANDBOOK_PAGES,
    })

def query_api_view(request):
    q = request.GET.get('q', '').strip()
    if not q:
        return JsonResponse({'error': 'Missing query parameter q'}, status=400)
    res = query_handbook(q)
    return JsonResponse(res)

def health_view(request):
    return JsonResponse({'status': 'ok', 'demo': 'documind'})
