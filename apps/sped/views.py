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
from apps.sped.services import processar_sped_completo
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
            uf = UF.objects.filter(sigla=reg_0000.get('uf', 'SP')).first()
            if not uf:
                uf = UF.objects.first()
            
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
