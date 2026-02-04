from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from apps.empresa.models import Empresa


@login_required
def index(request):
    return render(request, 'dashboards/index.html')


@login_required
def relatorio_fiscal(request):
    context = {
        'empresas': Empresa.objects.filter(ativo=True),
    }
    return render(request, 'dashboards/relatorio_fiscal.html', context)
