from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

@login_required
def index(request):
    return render(request, 'reforma_tributaria/index.html')

@login_required
def consulta_gtin(request):
    return render(request, 'reforma_tributaria/consulta_gtin.html')

@login_required
def consulta(request):
    return render(request, 'reforma_tributaria/consulta.html')

@login_required
def api_processar_xml(request):
    if request.method == 'POST':
        return JsonResponse({'status': 'ok', 'produtos': []})
    return JsonResponse({'error': 'Method not allowed'}, status=405)
