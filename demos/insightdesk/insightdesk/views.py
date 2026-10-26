from django.shortcuts import render
from django.http import JsonResponse
from .engine import query_sales_data, get_dataframe

def index_view(request):
    question = request.GET.get('q', '').strip()
    result = None
    if question:
        result = query_sales_data(question)

    df = get_dataframe()
    sample_records = df.head(6).to_dict(orient='records')

    return render(request, 'index.html', {
        'question': question,
        'result': result,
        'sample_records': sample_records,
    })

def query_api_view(request):
    q = request.GET.get('q', '').strip()
    if not q:
        return JsonResponse({'error': 'Missing query parameter q'}, status=400)
    res = query_sales_data(q)
    return JsonResponse(res)

def health_view(request):
    return JsonResponse({'status': 'ok', 'demo': 'insightdesk'})
