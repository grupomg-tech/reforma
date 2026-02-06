"""
Serviço de consulta de participantes via APIs externas
- BrasilAPI (gratuita)
- ReceitaWS (gratuita com limite)
"""
import logging
import time
import requests
from datetime import datetime
from django.utils import timezone

logger = logging.getLogger('sped.processamento')

# Configurações
BRASIL_API_URL = "https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
RECEITAWS_URL = "https://www.receitaws.com.br/v1/cnpj/{cnpj}"
TIMEOUT = 30
DELAY_ENTRE_CONSULTAS = 1  # segundos entre consultas BrasilAPI (mínimo seguro)
MAX_RETRIES = 3  # tentativas em caso de rate limit
DELAY_RATE_LIMIT = 10  # segundos de espera extra em caso de rate limit
DELAY_RECEITAWS = 20  # segundos mínimo entre usos do ReceitaWS (fallback)
_ultimo_uso_receitaws = 0  # timestamp do último uso do ReceitaWS


def consultar_cnpj_brasilapi(cnpj):
    """
    Consulta CNPJ na BrasilAPI (gratuita, sem autenticação)
    Retorna dados da empresa incluindo opção pelo Simples
    """
    cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
    
    if len(cnpj_limpo) != 14:
        return {'erro': 'CNPJ inválido', 'sucesso': False}
    
    try:
        url = BRASIL_API_URL.format(cnpj=cnpj_limpo)
        response = requests.get(url, timeout=TIMEOUT)
        
        if response.status_code == 200:
            dados = response.json()
# Garantir que None vira False para campos booleanos
            opt_simples = dados.get('opcao_pelo_simples')
            opt_mei = dados.get('opcao_pelo_mei')
            
            return {
                'sucesso': True,
                'razao_social': dados.get('razao_social', ''),
                'nome_fantasia': dados.get('nome_fantasia', ''),
                'situacao_cadastral': dados.get('descricao_situacao_cadastral', ''),
                'optante_simples': bool(opt_simples) if opt_simples is not None else False,
                'data_opcao_simples': parse_data(dados.get('data_opcao_pelo_simples')),
                'data_exclusao_simples': parse_data(dados.get('data_exclusao_do_simples')),
                'optante_mei': bool(opt_mei) if opt_mei is not None else False,
                'natureza_juridica': dados.get('natureza_juridica', ''),
                'porte': dados.get('porte', ''),
                'cnae_principal': dados.get('cnae_fiscal', ''),
                'descricao_cnae': dados.get('cnae_fiscal_descricao', ''),
                'uf': dados.get('uf', ''),
                'municipio': dados.get('municipio', ''),
            }
        elif response.status_code == 404:
            return {'erro': 'CNPJ não encontrado', 'sucesso': False}
        elif response.status_code == 429:
            return {'erro': 'Rate limit excedido. Aguarde alguns minutos.', 'sucesso': False}
        else:
            return {'erro': f'Erro HTTP {response.status_code}', 'sucesso': False}
            
    except requests.exceptions.Timeout:
        return {'erro': 'Timeout na consulta', 'sucesso': False}
    except requests.exceptions.RequestException as e:
        return {'erro': f'Erro de conexão: {str(e)}', 'sucesso': False}
    except Exception as e:
        return {'erro': f'Erro inesperado: {str(e)}', 'sucesso': False}


def consultar_cnpj_receitaws(cnpj):
    """
    Consulta CNPJ na ReceitaWS (gratuita com limite de 3/minuto)
    Alternativa à BrasilAPI
    """
    cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
    
    if len(cnpj_limpo) != 14:
        return {'erro': 'CNPJ inválido', 'sucesso': False}
    
    try:
        url = RECEITAWS_URL.format(cnpj=cnpj_limpo)
        headers = {'Accept': 'application/json'}
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        
        if response.status_code == 200:
            dados = response.json()
            
            if dados.get('status') == 'ERROR':
                return {'erro': dados.get('message', 'Erro desconhecido'), 'sucesso': False}
            
# Garantir que None vira False para campos booleanos
            simples_data = dados.get('simples') or {}
            opt_simples_rws = simples_data.get('optante')
            opt_mei_rws = simples_data.get('mei')
            
            return {
                'sucesso': True,
                'razao_social': dados.get('nome', ''),
                'nome_fantasia': dados.get('fantasia', ''),
                'situacao_cadastral': dados.get('situacao', ''),
                'optante_simples': bool(opt_simples_rws) if opt_simples_rws is not None else False,
                'data_opcao_simples': parse_data(simples_data.get('data_opcao')) if simples_data else None,
                'data_exclusao_simples': parse_data(simples_data.get('data_exclusao')) if simples_data else None,
                'optante_mei': bool(opt_mei_rws) if opt_mei_rws is not None else False,
                'natureza_juridica': dados.get('natureza_juridica', ''),
                'porte': dados.get('porte', ''),
                'cnae_principal': dados.get('atividade_principal', [{}])[0].get('code', '') if dados.get('atividade_principal') else '',
                'descricao_cnae': dados.get('atividade_principal', [{}])[0].get('text', '') if dados.get('atividade_principal') else '',
                'uf': dados.get('uf', ''),
                'municipio': dados.get('municipio', ''),
            }
        elif response.status_code == 429:
            return {'erro': 'Rate limit excedido (3 consultas/minuto)', 'sucesso': False}
        else:
            return {'erro': f'Erro HTTP {response.status_code}', 'sucesso': False}
            
    except Exception as e:
        return {'erro': f'Erro: {str(e)}', 'sucesso': False}


def parse_data(data_str):
    """Converte string de data para objeto date"""
    if not data_str:
        return None
    
    formatos = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']
    for fmt in formatos:
        try:
            return datetime.strptime(data_str, fmt).date()
        except (ValueError, TypeError):
            continue
    return None


def consultar_participante(participante, usar_receitaws=False):
    """
    Consulta um participante e atualiza seus dados
    """
    from apps.sped.models import Registro0150
    
    if not participante.cnpj or len(participante.cnpj) != 14:
        participante.erro_consulta = 'CNPJ inválido ou não informado'
        participante.consultado = True
        participante.data_consulta = timezone.now()
        participante.save()
        return {'sucesso': False, 'erro': 'CNPJ inválido'}
    
# Sempre tenta BrasilAPI primeiro (prioridade)
    global _ultimo_uso_receitaws
    erro_brasilapi = ''
    api_usada = 'BrasilAPI'
    resultado = consultar_cnpj_brasilapi(participante.cnpj)
    
    # Se BrasilAPI falhou por rate limit, retenta com delay
    if not resultado.get('sucesso') and 'Rate limit' in resultado.get('erro', ''):
        for tentativa in range(1, MAX_RETRIES + 1):
            logger.info(f"    ⏳ BrasilAPI rate limit - aguardando {DELAY_RATE_LIMIT}s (tentativa {tentativa}/{MAX_RETRIES})...")
            time.sleep(DELAY_RATE_LIMIT)
            resultado = consultar_cnpj_brasilapi(participante.cnpj)
            if resultado.get('sucesso') or 'Rate limit' not in resultado.get('erro', ''):
                break
    
    # Se BrasilAPI falhou (qualquer erro), registra e tenta ReceitaWS como fallback
    if not resultado.get('sucesso'):
        erro_brasilapi = resultado.get('erro', 'Erro desconhecido')
        logger.warning(f"    ⚠ BrasilAPI falhou para {participante.cnpj}: {erro_brasilapi}")
        logger.info(f"    🔄 Tentando ReceitaWS como fallback...")
        
        # Garantir delay mínimo de 20s entre usos do ReceitaWS
        agora = time.time()
        tempo_desde_ultimo = agora - _ultimo_uso_receitaws
        if tempo_desde_ultimo < DELAY_RECEITAWS:
            espera = DELAY_RECEITAWS - tempo_desde_ultimo
            logger.info(f"    ⏳ Aguardando {espera:.0f}s para usar ReceitaWS...")
            time.sleep(espera)
        
        api_usada = 'ReceitaWS'
        resultado = consultar_cnpj_receitaws(participante.cnpj)
        _ultimo_uso_receitaws = time.time()
    
    # Adicionar metadados ao resultado
    resultado['api_usada'] = api_usada
    resultado['erro_brasilapi'] = erro_brasilapi
    
    if resultado.get('sucesso'):
        participante.situacao_cadastral = resultado.get('situacao_cadastral', '')
        participante.optante_simples = bool(resultado.get('optante_simples', False))
        participante.data_opcao_simples = resultado.get('data_opcao_simples')
        participante.data_exclusao_simples = resultado.get('data_exclusao_simples')
        participante.optante_mei = bool(resultado.get('optante_mei', False))
        participante.natureza_juridica = resultado.get('natureza_juridica', '')
        participante.porte = resultado.get('porte', '')
        participante.cnae_principal = resultado.get('cnae_principal', '')
        participante.descricao_cnae = resultado.get('descricao_cnae', '')
        participante.uf = resultado.get('uf', '') or participante.uf
        participante.consultado = True
        participante.data_consulta = timezone.now()
        participante.erro_consulta = ''
        participante.save()
        
        logger.info(f"  ✓ {participante.cnpj} - {participante.nome[:30]} - Simples: {participante.optante_simples}")
    else:
        participante.consultado = True
        participante.data_consulta = timezone.now()
        participante.erro_consulta = resultado.get('erro', 'Erro desconhecido')
        participante.save()
        
        logger.warning(f"  ✗ {participante.cnpj} - Erro: {resultado.get('erro')}")
    
    return resultado


def consultar_participantes_lote(registro_0000_id, apenas_nao_consultados=True):
    """
    Consulta todos os participantes de um SPED em lote
    Retorna estatísticas do processamento
    """
    from apps.sped.models import Registro0000, Registro0150
    
    logger.info("=" * 60)
    logger.info(f"CONSULTA DE PARTICIPANTES - Registro 0000 ID: {registro_0000_id}")
    logger.info("=" * 60)
    
    registro_0000 = Registro0000.objects.get(id=registro_0000_id)
    
    # Filtra participantes
    participantes = Registro0150.objects.filter(registro_0000=registro_0000)
    
    if apenas_nao_consultados:
        participantes = participantes.filter(consultado=False)
    
    # Apenas CNPJs (14 dígitos)
    participantes = participantes.exclude(cnpj='').exclude(cnpj__isnull=True)
    participantes = [p for p in participantes if len(p.cnpj) == 14]
    
    total = len(participantes)
    logger.info(f"Total de participantes a consultar: {total}")
    
    stats = {
        'total': total,
        'consultados': 0,
        'atualizados': 0,
        'erros': 0,
        'simples': 0,
        'mei': 0,
        'regime_normal': 0,
    }
    
    for idx, participante in enumerate(participantes, 1):
        logger.info(f"[{idx}/{total}] Consultando {participante.cnpj}...")
        
        resultado = consultar_participante(participante)
        stats['consultados'] += 1
        
        if resultado.get('sucesso'):
            stats['atualizados'] += 1
            if participante.optante_mei:
                stats['mei'] += 1
            elif participante.optante_simples:
                stats['simples'] += 1
            else:
                stats['regime_normal'] += 1
        else:
            stats['erros'] += 1
        
        # Delay para respeitar rate limit das APIs
        if idx < total:
            time.sleep(DELAY_ENTRE_CONSULTAS)
    
    logger.info("=" * 60)
    logger.info("RESUMO DA CONSULTA")
    logger.info("=" * 60)
    logger.info(f"Total: {stats['total']}")
    logger.info(f"Consultados: {stats['consultados']}")
    logger.info(f"Atualizados: {stats['atualizados']}")
    logger.info(f"Erros: {stats['erros']}")
    logger.info(f"Simples Nacional: {stats['simples']}")
    logger.info(f"MEI: {stats['mei']}")
    logger.info(f"Regime Normal: {stats['regime_normal']}")
    logger.info("=" * 60)
    
    return stats