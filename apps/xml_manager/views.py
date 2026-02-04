from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

@login_required
def importar_xmls(request):
    return render(request, 'xml_manager/importar.html')

@login_required
def lote(request):
    if request.method == 'POST':
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'Method not allowed'}, status=405)
