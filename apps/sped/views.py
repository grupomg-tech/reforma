from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def importar_sped(request):
    return render(request, 'sped/importar.html')

@login_required
def exportar_sped(request):
    return render(request, 'sped/exportar.html')

@login_required
def excluir_sped(request):
    return render(request, 'sped/excluir.html')
