import os
import zipfile
import logging
from io import BytesIO
from datetime import datetime

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages

from apps.sped.models import Registro0000
from apps.sped.parser import parse_sped_file
from apps.sped.services import processar_sped_completo, processar_participantes_0150
from apps.empresa.models import Empresa

# Logger para importação
logger = logging.getLogger('sped.importacao')


@login_required
def importar_sped(request):
    if request.method == 'POST':
        return processar_importacao_sped(request)
    
    context = {
        'empresas': Empresa.objects.filter(ativo=True),
        'registros': Registro0000.objects.order_by('-created_at')[:10],
    }
    return render(request, 'sped/importar.html', context)


@login_required
def processar_importacao_sped(request):
    """Processa o upload e importação do arquivo SPED"""
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    tipo = request.POST.get('tipo')
    arquivo = request.FILES.get('arquivo_sped')
    sobrescrever = request.POST.get('sobrescrever') == 'on'
    
    logger.info("=" * 60)
    logger.info("INÍCIO DA IMPORTAÇÃO SPED")
    logger.info("=" * 60)
    logger.info(f"Usuário: {request.user.email}")
    logger.info(f"Tipo SPED: {tipo}")
    logger.info(f"Arquivo: {arquivo.name if arquivo else 'Nenhum'}")
    logger.info(f"Sobrescrever: {sobrescrever}")
    
    if not tipo or not arquivo:
        logger.error("Erro: Tipo ou arquivo não informado")
        if is_ajax:
            return JsonResponse({
                'success': False,
                'message': 'Selecione o tipo de SPED e o arquivo.'
            }, status=400)
        messages.error(request, 'Selecione o tipo de SPED e o arquivo.')
        return render(request, 'sped/importar.html')
    
    relatorio = {
        'total_arquivos': 0,
        'sucesso': 0,
        'pulados': 0,
        'erros': 0,
        'detalhes': []
    }
    
    registros_ids = []
    
    try:
        # Verifica se é ZIP
        if arquivo.name.endswith('.zip'):
            logger.info(f"Extraindo arquivos do ZIP: {arquivo.name}")
            arquivos_processar = extrair_arquivos_zip(arquivo)
            logger.info(f"Encontrados {len(arquivos_processar)} arquivos no ZIP")
        else:
            arquivos_processar = [(arquivo.name, arquivo.read())]
        
        relatorio['total_arquivos'] = len(arquivos_processar)
        logger.info(f"Total de arquivos a processar: {relatorio['total_arquivos']}")
        
        for idx, (nome_arquivo, conteudo) in enumerate(arquivos_processar, 1):
            logger.info("-" * 40)
            logger.info(f"Processando arquivo {idx}/{len(arquivos_processar)}: {nome_arquivo}")
            
            resultado = processar_arquivo_sped(
                nome_arquivo, 
                conteudo, 
                tipo, 
                sobrescrever
            )
            
            relatorio['detalhes'].append(resultado)
            
            if resultado['status'] == 'sucesso':
                relatorio['sucesso'] += 1
                logger.info(f"✓ SUCESSO - CNPJ: {resultado['cnpj']} | Período: {resultado['periodo']}")
                if resultado.get('registro_id'):
                    registros_ids.append(resultado['registro_id'])
                    logger.info(f"  Registro ID: {resultado['registro_id']}")
            elif resultado['status'] == 'pulado':
                relatorio['pulados'] += 1
                logger.warning(f"⚠ PULADO - {resultado['mensagem']}")
            else:
                relatorio['erros'] += 1
                logger.error(f"✗ ERRO - {resultado['mensagem']}")
        
        logger.info("-" * 40)
        logger.info("PROCESSAMENTO DOS REGISTROS IMPORTADOS")
        logger.info("-" * 40)
        
# Processa os registros importados (popula módulos relacionados)
        for reg_id in registros_ids:
            try:
                logger.info(f"Processando registro {reg_id} (Documentos Fiscais e NCM)...")
                resultado_proc = processar_sped_completo(reg_id)
                logger.info(f"  → Itens 0200: {resultado_proc.get('itens', 0)}")
                logger.info(f"  → Documentos C100: {resultado_proc.get('documentos', 0)}")
                logger.info(f"  → Participantes 0150: {resultado_proc.get('participantes', 0)}")
            except Exception as e:
                logger.error(f"Erro ao processar SPED {reg_id}: {e}")
        
        logger.info("=" * 60)
        logger.info("RESUMO DA IMPORTAÇÃO")
        logger.info("=" * 60)
        logger.info(f"Total de arquivos: {relatorio['total_arquivos']}")
        logger.info(f"Sucesso: {relatorio['sucesso']}")
        logger.info(f"Pulados: {relatorio['pulados']}")
        logger.info(f"Erros: {relatorio['erros']}")
        logger.info(f"Registros criados: {registros_ids}")
        logger.info("=" * 60)
        
        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': f'Importação concluída! {relatorio["sucesso"]} arquivo(s) processado(s).',
                'relatorio': relatorio,
                'registros_0000_ids': registros_ids,
            })
        
        messages.success(request, f'Importação concluída! {relatorio["sucesso"]} arquivo(s) processado(s).')
        
    except Exception as e:
        logger.error(f"ERRO CRÍTICO na importação: {str(e)}", exc_info=True)
        if is_ajax:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao processar arquivo: {str(e)}'
            }, status=500)
        messages.error(request, f'Erro ao processar arquivo: {str(e)}')
    
    return render(request, 'sped/importar.html', {
        'empresas': Empresa.objects.filter(ativo=True),
        'registros': Registro0000.objects.order_by('-created_at')[:10],
    })


def extrair_arquivos_zip(arquivo_zip):
    """Extrai arquivos .txt de um ZIP"""
    arquivos = []
    with zipfile.ZipFile(BytesIO(arquivo_zip.read()), 'r') as zf:
        for nome in zf.namelist():
            if nome.endswith('.txt') and not nome.startswith('__MACOSX'):
                conteudo = zf.read(nome)
                arquivos.append((os.path.basename(nome), conteudo))
    return arquivos


def processar_arquivo_sped(nome_arquivo, conteudo, tipo, sobrescrever):
    """Processa um único arquivo SPED"""
    resultado = {
        'arquivo': nome_arquivo,
        'status': 'erro',
        'cnpj': '',
        'periodo': '',
        'mensagem': '',
        'registro_id': None,
    }
    
    try:
        logger.debug(f"Iniciando parse do arquivo: {nome_arquivo}")
        logger.debug(f"Tamanho do conteúdo: {len(conteudo)} bytes")
        
        # Parse do arquivo
        dados = parse_sped_file(conteudo)
        
        if not dados.get('0000'):
            resultado['mensagem'] = 'Registro 0000 não encontrado'
            logger.error(f"Registro 0000 não encontrado em {nome_arquivo}")
            return resultado
        
        logger.debug(f"Parse concluído - Registros encontrados:")
        logger.debug(f"  0150 (Participantes): {len(dados.get('0150', []))}")
        logger.debug(f"  0200 (Itens): {len(dados.get('0200', []))}")
        logger.debug(f"  C100 (Documentos): {len(dados.get('C100', []))}")
        logger.debug(f"  C170 (Itens Doc): {len(dados.get('C170', []))}")
        
        reg_0000 = dados['0000']
        cnpj = reg_0000.get('cnpj', '').strip()
        dt_ini = reg_0000.get('dt_ini')
        
        resultado['cnpj'] = cnpj
        resultado['periodo'] = dt_ini.strftime('%m/%Y') if dt_ini else ''
        
        # Busca empresa pelo CNPJ
        cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
        empresa = Empresa.objects.filter(
            cnpj_cpf__contains=cnpj_limpo[-8:-2]
        ).first()
        
        if not empresa:
            # Tenta criar empresa
            from apps.empresa.models import UF
            sigla_uf = reg_0000.get('uf', 'SP').upper().strip()
            uf = UF.objects.filter(sigla=sigla_uf).first()
            
            if not uf:
                # Cria a UF se não existir
                codigos_uf = {
                    'AC': 12, 'AL': 27, 'AP': 16, 'AM': 13, 'BA': 29, 'CE': 23,
                    'DF': 53, 'ES': 32, 'GO': 52, 'MA': 21, 'MT': 51, 'MS': 50,
                    'MG': 31, 'PA': 15, 'PB': 25, 'PR': 41, 'PE': 26, 'PI': 22,
                    'RJ': 33, 'RN': 24, 'RS': 43, 'RO': 11, 'RR': 14, 'SC': 42,
                    'SP': 35, 'SE': 28, 'TO': 17
                }
                nomes_uf = {
                    'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas',
                    'BA': 'Bahia', 'CE': 'Ceará', 'DF': 'Distrito Federal', 'ES': 'Espírito Santo',
                    'GO': 'Goiás', 'MA': 'Maranhão', 'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul',
                    'MG': 'Minas Gerais', 'PA': 'Pará', 'PB': 'Paraíba', 'PR': 'Paraná',
                    'PE': 'Pernambuco', 'PI': 'Piauí', 'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte',
                    'RS': 'Rio Grande do Sul', 'RO': 'Rondônia', 'RR': 'Roraima', 'SC': 'Santa Catarina',
                    'SP': 'São Paulo', 'SE': 'Sergipe', 'TO': 'Tocantins'
                }
                codigo = codigos_uf.get(sigla_uf, 35)
                nome = nomes_uf.get(sigla_uf, 'São Paulo')
                if sigla_uf not in codigos_uf:
                    sigla_uf = 'SP'
                
                uf, _ = UF.objects.get_or_create(
                    codigo=codigo,
                    defaults={'sigla': sigla_uf, 'nome': nome}
                )
            
            empresa = Empresa.objects.create(
                cnpj_cpf=formatar_cnpj(cnpj_limpo),
                razao_social=reg_0000.get('nome', 'Empresa Importada'),
                uf=uf,
            )
        
        # Verifica se já existe
        registro_existente = Registro0000.objects.filter(
            empresa=empresa,
            tipo=tipo,
            periodo=dt_ini
        ).first()
        
        if registro_existente and not sobrescrever:
            resultado['status'] = 'pulado'
            resultado['mensagem'] = 'Arquivo já importado anteriormente'
            return resultado
        
        # Salva o arquivo
        from django.core.files.base import ContentFile
        
        if registro_existente and sobrescrever:
            registro = registro_existente
            registro.arquivo_original.save(nome_arquivo, ContentFile(conteudo))
            registro.processado = False
            registro.save()
        else:
            registro = Registro0000.objects.create(
                empresa=empresa,
                tipo=tipo,
                periodo=dt_ini,
                arquivo_original=ContentFile(conteudo, name=nome_arquivo),
                processado=False,
            )
        
        resultado['status'] = 'sucesso'
        resultado['mensagem'] = 'Importado com sucesso'
        resultado['registro_id'] = registro.id
        
    except Exception as e:
        resultado['mensagem'] = str(e)
    
    return resultado


def formatar_cnpj(cnpj):
    """Formata CNPJ para padrão XX.XXX.XXX/XXXX-XX"""
    cnpj = ''.join(filter(str.isdigit, cnpj)).zfill(14)
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:14]}"


@login_required
def exportar_sped(request):
    context = {
        'empresas': Empresa.objects.filter(ativo=True),
    }
    return render(request, 'sped/exportar.html', context)


@login_required
def excluir_sped(request):
    context = {
        'empresas': Empresa.objects.filter(ativo=True),
    }
    return render(request, 'sped/excluir.html', context)


@login_required
def consultar_participantes(request, registro_id):
    """API para iniciar consulta de participantes"""
    from apps.sped.consulta_participantes import consultar_participantes_lote
    
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    try:
        registro = Registro0000.objects.get(id=registro_id)
        
        # Executa consulta
        stats = consultar_participantes_lote(registro_id, apenas_nao_consultados=True)
        
        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': f'Consulta concluída! {stats["atualizados"]} participantes atualizados.',
                'stats': stats,
            })
        
        messages.success(request, f'Consulta concluída! {stats["atualizados"]} participantes atualizados.')
        
    except Registro0000.DoesNotExist:
        if is_ajax:
            return JsonResponse({'success': False, 'message': 'Registro não encontrado.'}, status=404)
        messages.error(request, 'Registro não encontrado.')
    except Exception as e:
        logger.error(f"Erro na consulta de participantes: {e}", exc_info=True)
        if is_ajax:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
        messages.error(request, f'Erro: {str(e)}')
    
    return render(request, 'sped/importar.html', {
        'empresas': Empresa.objects.filter(ativo=True),
        'registros': Registro0000.objects.order_by('-created_at')[:10],
    })


@login_required
def status_participantes(request, registro_id):
    """API para verificar status dos participantes de um SPED"""
    from apps.sped.models import Registro0150
    
    try:
        registro = Registro0000.objects.get(id=registro_id)
        participantes = Registro0150.objects.filter(registro_0000=registro)
        
        total = participantes.count()
        consultados = participantes.filter(consultado=True).count()
        com_cnpj = participantes.exclude(cnpj='').exclude(cnpj__isnull=True).count()
        simples = participantes.filter(optante_simples=True).count()
        mei = participantes.filter(optante_mei=True).count()
        erros = participantes.filter(consultado=True).exclude(erro_consulta='').count()
        
        return JsonResponse({
            'success': True,
            'total': total,
            'com_cnpj': com_cnpj,
            'consultados': consultados,
            'pendentes': com_cnpj - consultados,
            'simples': simples,
            'mei': mei,
            'regime_normal': consultados - simples - mei - erros,
            'erros': erros,
        })
    except Registro0000.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Registro não encontrado.'}, status=404)
