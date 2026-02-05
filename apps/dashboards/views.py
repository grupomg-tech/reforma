from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from apps.empresa.models import Empresa


@login_required
def index(request):
    return render(request, 'dashboards/index.html')


@login_required
def relatorio_fiscal(request):
    from django.db.models import Sum
    from decimal import Decimal
    from apps.sped.models import Registro0000, Registro0200, RegistroC100, RegistroC170
    
    empresas = Empresa.objects.filter(ativo=True)
    
    # Parâmetros do filtro
    empresa_id = request.GET.get('empresa')
    periodo_inicial = request.GET.get('periodo_inicial')
    periodo_final = request.GET.get('periodo_final')
    aliquota_ibs = Decimal(request.GET.get('aliquota_ibs', '18.5') or '18.5')
    aliquota_cbs = Decimal(request.GET.get('aliquota_cbs', '8.5') or '8.5')
    aliquota_is = Decimal(request.GET.get('aliquota_is', '0') or '0')
    agrupar_filiais = request.GET.get('filiais') == '1'
    
    # Contexto base
    context = {
        'empresas': empresas,
        'periodos': [],
    }
    
    # Se empresa selecionada, buscar períodos disponíveis
    if empresa_id:
        periodos = Registro0000.objects.filter(
            empresa_id=empresa_id,
            processado=True
        ).values_list('periodo', flat=True).distinct().order_by('periodo')
        context['periodos'] = [p.strftime('%Y-%m') for p in periodos]
    
    # Se filtro completo, buscar dados
    if empresa_id and periodo_inicial and periodo_final:
        # Buscar registros 0000 do período
        registros_0000 = Registro0000.objects.filter(
            empresa_id=empresa_id,
            processado=True,
            periodo__gte=periodo_inicial + '-01',
            periodo__lte=periodo_final + '-28'
        )
        
        if agrupar_filiais:
            empresa = Empresa.objects.get(id=empresa_id)
            cnpj_base = empresa.cnpj_cpf[:8] if empresa.cnpj_cpf else ''
            empresas_grupo = Empresa.objects.filter(cnpj_cpf__startswith=cnpj_base)
            registros_0000 = Registro0000.objects.filter(
                empresa__in=empresas_grupo,
                processado=True,
                periodo__gte=periodo_inicial + '-01',
                periodo__lte=periodo_final + '-28'
            )
        
        # Buscar documentos C100 (0=Entrada, 1=Saída)
        documentos_entrada = RegistroC100.objects.filter(registro_0000__in=registros_0000, ind_oper='0')
        documentos_saida = RegistroC100.objects.filter(registro_0000__in=registros_0000, ind_oper='1')
        
        # Buscar itens C170
        itens_entrada = RegistroC170.objects.filter(registro_c100__in=documentos_entrada).select_related('registro_c100')
        itens_saida = RegistroC170.objects.filter(registro_c100__in=documentos_saida).select_related('registro_c100')
        
        # Buscar dados dos itens (0200) para NCM e descrição
        itens_0200 = {}
        for reg in registros_0000:
            for item in Registro0200.objects.filter(registro_0000=reg):
                itens_0200[item.cod_item] = {
                    'descricao': item.descr_item,
                    'ncm': item.cod_ncm,
                }
        
        # Agregar produtos de ENTRADA
        produtos_entradas_dict = {}
        for item in itens_entrada:
            cod = item.cod_item
            if cod not in produtos_entradas_dict:
                info_item = itens_0200.get(cod, {})
                produtos_entradas_dict[cod] = {
                    'codigo': cod,
                    'descricao': info_item.get('descricao', item.descr_compl or cod),
                    'ncm': item.cod_ncm or info_item.get('ncm', ''),
                    'cfop': item.cfop,
                    'quantidade': Decimal('0'),
                    'valor_total': Decimal('0'),
                    'icms': Decimal('0'),
                    'pis': Decimal('0'),
                    'cofins': Decimal('0'),
                }
            produtos_entradas_dict[cod]['quantidade'] += item.qtd or Decimal('0')
            produtos_entradas_dict[cod]['valor_total'] += item.vl_item or Decimal('0')
            produtos_entradas_dict[cod]['icms'] += item.vl_icms or Decimal('0')
            produtos_entradas_dict[cod]['pis'] += item.vl_pis or Decimal('0')
            produtos_entradas_dict[cod]['cofins'] += item.vl_cofins or Decimal('0')
        
        # Calcular IBS/CBS para entradas
        for cod, prod in produtos_entradas_dict.items():
            valor_liquido = prod['valor_total'] - prod['icms'] - prod['pis'] - prod['cofins']
            prod['ibs_cbs'] = (valor_liquido * (aliquota_ibs + aliquota_cbs + aliquota_is) / Decimal('100')).quantize(Decimal('0.01'))
        
        produtos_entradas = sorted(produtos_entradas_dict.values(), key=lambda x: x['valor_total'], reverse=True)
        
        # Agregar produtos de SAÍDA
        produtos_saidas_dict = {}
        for item in itens_saida:
            cod = item.cod_item
            if cod not in produtos_saidas_dict:
                info_item = itens_0200.get(cod, {})
                produtos_saidas_dict[cod] = {
                    'codigo': cod,
                    'descricao': info_item.get('descricao', item.descr_compl or cod),
                    'ncm': item.cod_ncm or info_item.get('ncm', ''),
                    'cfop': item.cfop,
                    'quantidade': Decimal('0'),
                    'valor_total': Decimal('0'),
                    'icms': Decimal('0'),
                    'pis': Decimal('0'),
                    'cofins': Decimal('0'),
                }
            produtos_saidas_dict[cod]['quantidade'] += item.qtd or Decimal('0')
            produtos_saidas_dict[cod]['valor_total'] += item.vl_item or Decimal('0')
            produtos_saidas_dict[cod]['icms'] += item.vl_icms or Decimal('0')
            produtos_saidas_dict[cod]['pis'] += item.vl_pis or Decimal('0')
            produtos_saidas_dict[cod]['cofins'] += item.vl_cofins or Decimal('0')
        
        # Calcular IBS/CBS para saídas
        for cod, prod in produtos_saidas_dict.items():
            valor_liquido = prod['valor_total'] - prod['icms'] - prod['pis'] - prod['cofins']
            prod['ibs_cbs'] = (valor_liquido * (aliquota_ibs + aliquota_cbs + aliquota_is) / Decimal('100')).quantize(Decimal('0.01'))
        
        produtos_saidas = sorted(produtos_saidas_dict.values(), key=lambda x: x['valor_total'], reverse=True)
        
        # Totais ENTRADAS
        total_valor_entradas = sum(p['valor_total'] for p in produtos_entradas)
        total_icms_entradas = sum(p['icms'] for p in produtos_entradas)
        total_pis_entradas = sum(p['pis'] for p in produtos_entradas)
        total_cofins_entradas = sum(p['cofins'] for p in produtos_entradas)
        total_ibs_cbs_entradas = sum(p['ibs_cbs'] for p in produtos_entradas)
        creditos_entradas = total_icms_entradas + total_pis_entradas + total_cofins_entradas
        compra_liquida = total_valor_entradas - creditos_entradas
        carga_entradas = (creditos_entradas / total_valor_entradas * 100) if total_valor_entradas else Decimal('0')
        carga_entradas_reforma = (total_ibs_cbs_entradas / compra_liquida * 100) if compra_liquida else Decimal('0')
        
        # Totais SAÍDAS
        total_valor_saidas = sum(p['valor_total'] for p in produtos_saidas)
        total_icms_saidas = sum(p['icms'] for p in produtos_saidas)
        total_pis_saidas = sum(p['pis'] for p in produtos_saidas)
        total_cofins_saidas = sum(p['cofins'] for p in produtos_saidas)
        total_ibs_cbs_saidas = sum(p['ibs_cbs'] for p in produtos_saidas)
        debitos_saidas = total_icms_saidas + total_pis_saidas + total_cofins_saidas
        venda_liquida = total_valor_saidas - debitos_saidas
        carga_saidas = (debitos_saidas / total_valor_saidas * 100) if total_valor_saidas else Decimal('0')
        carga_saidas_reforma = (total_ibs_cbs_saidas / venda_liquida * 100) if venda_liquida else Decimal('0')
        
        # Apuração geral
        resultado_atual = debitos_saidas - creditos_entradas
        resultado_reforma = total_ibs_cbs_saidas - total_ibs_cbs_entradas
        carga_atual = (resultado_atual / total_valor_saidas * 100) if total_valor_saidas else Decimal('0')
        carga_reforma = (resultado_reforma / venda_liquida * 100) if venda_liquida else Decimal('0')
        
        # Atualizar contexto
        context.update({
            # Produtos
            'produtos_entradas': produtos_entradas,
            'produtos_saidas': produtos_saidas,
            
            # Totais Entradas
            'total_valor_entradas': total_valor_entradas,
            'total_icms_entradas': total_icms_entradas,
            'total_pis_entradas': total_pis_entradas,
            'total_cofins_entradas': total_cofins_entradas,
            'total_ibs_cbs_entradas': total_ibs_cbs_entradas,
            'compra_bruta': total_valor_entradas,
            'creditos_entradas': creditos_entradas,
            'compra_liquida': compra_liquida,
            'carga_entradas': f"{carga_entradas:.2f}".replace('.', ','),
            'compra_liquida_reforma': compra_liquida,
            'creditos_ibs_cbs': total_ibs_cbs_entradas,
            'compra_total_reforma': compra_liquida + total_ibs_cbs_entradas,
            'carga_entradas_reforma': f"{carga_entradas_reforma:.2f}".replace('.', ','),
            
            # Totais Saídas
            'total_valor_saidas': total_valor_saidas,
            'total_icms_saidas': total_icms_saidas,
            'total_pis_saidas': total_pis_saidas,
            'total_cofins_saidas': total_cofins_saidas,
            'total_ibs_cbs_saidas': total_ibs_cbs_saidas,
            'venda_bruta': total_valor_saidas,
            'debitos_saidas': debitos_saidas,
            'venda_liquida': venda_liquida,
            'carga_saidas': f"{carga_saidas:.2f}".replace('.', ','),
            'venda_liquida_reforma': venda_liquida,
            'debitos_ibs_cbs': total_ibs_cbs_saidas,
            'venda_total_reforma': venda_liquida + total_ibs_cbs_saidas,
            'carga_saidas_reforma': f"{carga_saidas_reforma:.2f}".replace('.', ','),
            
            # Apuração Resumo
            'debitos_atual': debitos_saidas,
            'creditos_atual': creditos_entradas,
            'resultado_atual': resultado_atual,
            'carga_atual': f"{carga_atual:.2f}".replace('.', ','),
            'debitos_reforma': total_ibs_cbs_saidas,
            'creditos_reforma': total_ibs_cbs_entradas,
            'resultado_reforma': resultado_reforma,
            'carga_reforma': f"{carga_reforma:.2f}".replace('.', ','),
            
            # Dados para gráficos
            'icms_entradas': float(total_icms_entradas),
            'pis_entradas': float(total_pis_entradas),
            'cofins_entradas': float(total_cofins_entradas),
            'ibs_cbs_entradas': float(total_ibs_cbs_entradas),
            'icms_saidas': float(total_icms_saidas),
            'pis_saidas': float(total_pis_saidas),
            'cofins_saidas': float(total_cofins_saidas),
            'ibs_cbs_saidas': float(total_ibs_cbs_saidas),
            'carga_atual_compras': float(carga_entradas),
            'carga_reforma_compras': float(carga_entradas_reforma),
            'carga_atual_vendas': float(carga_saidas),
            'carga_reforma_vendas': float(carga_saidas_reforma),
        })
    
    return render(request, 'dashboards/relatorio_fiscal.html', context)
@login_required
def api_periodos(request):
    from django.http import JsonResponse
    from apps.sped.models import Registro0000
    
    empresa_id = request.GET.get('empresa')
    if not empresa_id:
        return JsonResponse({'periodos': []})
    
    periodos = Registro0000.objects.filter(
        empresa_id=empresa_id,
        processado=True
    ).values_list('periodo', flat=True).distinct().order_by('periodo')
    
    periodos_formatados = [p.strftime('%Y-%m') for p in periodos]
    
    return JsonResponse({'periodos': periodos_formatados})
@login_required
def debug_sped(request):
    from django.http import JsonResponse
    from apps.sped.models import Registro0000
    from apps.empresa.models import Empresa
    
    # Todas as empresas
    empresas = list(Empresa.objects.all().values('id', 'cnpj_cpf', 'razao_social', 'ativo'))
    
    # Todos os registros SPED
    registros = list(Registro0000.objects.all().values(
        'id', 'empresa_id', 'empresa__cnpj_cpf', 'tipo', 'periodo', 'processado', 'created_at'
    ))
    
    return JsonResponse({
        'empresas': empresas,
        'registros_sped': registros
    }, json_dumps_params={'default': str})