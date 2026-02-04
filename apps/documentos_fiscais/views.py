from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

@login_required
def api_documentos(request):
    return render(request, 'documentos_fiscais/index.html')

@login_required
def exportar(request):
    return JsonResponse({'status': 'ok'})
