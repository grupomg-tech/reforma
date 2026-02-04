from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator

from apps.reforma_tributaria.models import ItemNCM
from apps.empresa.models import Empresa


@login_required
def index(request):
    return render(request, 'reforma_tributaria/index.html')


@login_required
def consulta_gtin(request):
    context = {
        'empresas': Empresa.objects.filter(ativo=True),
    }
    return render(request, 'reforma_tributaria/consulta_gtin.html', context)


@login_required
def consulta(request):
    """View para NCM x cClassTrib"""
    empresa_id = request.GET.get('empresa')
    ncm = request.GET.get('ncm', '').strip()
    cst = request.GET.get('cst', '').strip()
    descricao = request.GET.get('descricao', '').strip()
    
    itens = ItemNCM.objects.all().order_by('cod_ncm', 'cod_item')
    
    if empresa_id:
        itens = itens.filter(empresa_id=empresa_id)
    
    if ncm:
        itens = itens.filter(cod_ncm__icontains=ncm)
    
    if cst:
        itens = itens.filter(
            models.Q(cst_icms__icontains=cst) |
            models.Q(cst_pis__icontains=cst) |
            models.Q(cst_cofins__icontains=cst)
        )
    
    if descricao:
        itens = itens.filter(descricao__icontains=descricao)
    
    paginator = Paginator(itens, 50)
    page = request.GET.get('page', 1)
    itens_page = paginator.get_page(page)
    
    context = {
        'itens': itens_page,
        'empresas': Empresa.objects.filter(ativo=True),
        'filtros': {
            'empresa': empresa_id,
            'ncm': ncm,
            'cst': cst,
            'descricao': descricao,
        }
    }
    return render(request, 'reforma_tributaria/consulta.html', context)


@login_required
def api_processar_xml(request):
    if request.method == 'POST':
        return JsonResponse({'status': 'ok', 'produtos': []})
    return JsonResponse({'error': 'Method not allowed'}, status=405)