import json
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from .agent import process_shopper_message, search_products

def index_view(request):
    chat_history = request.session.get('chat_history', [])
    query = request.GET.get('q', '').strip()
    result = None

    if query:
        result = process_shopper_message(query, chat_history)
        request.session['chat_history'] = result['history']
        chat_history = result['history']

    return render(request, 'index.html', {
        'query': query,
        'result': result,
        'chat_history': chat_history[-6:], # Show last 6 messages
    })

def clear_chat_view(request):
    request.session['chat_history'] = []
    return render(request, 'index.html', {'chat_history': []})

def search_api_view(request):
    cat = request.GET.get('category')
    max_p = request.GET.get('max_price')
    vendor = request.GET.get('vendor')
    q = request.GET.get('q')

    items = search_products(category=cat, max_price=max_p, vendor=vendor, query=q)
    return JsonResponse({'count': len(items), 'products': items})

def health_view(request):
    return JsonResponse({'status': 'ok', 'demo': 'shopassist'})
