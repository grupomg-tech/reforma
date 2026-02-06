"""
Validador de Operações de Devolução - SPED EFD ICMS/IPI
Regras R1 a R6 conforme especificação do PVA

Classifica e valida devoluções de compra e venda com base em:
- CFOP (Código Fiscal de Operações e Prestações)
- ind_oper (0=Entrada, 1=Saída)
- Nota referenciada (C113)
- finNFe do XML (quando disponível)
- Consistência C170 x C190
"""
import logging
from decimal import Decimal

logger = logging.getLogger('sped.validador_devolucao')

# ============================================================
# TABELAS DE CFOP DE DEVOLUÇÃO (parametrizáveis)
# ============================================================

# Devolução de VENDA: mercadoria retornando ao vendedor original
# Escriturada como ENTRADA (ind_oper=0) com CFOP 1.xxx/2.xxx
CFOPS_DEVOLUCAO_VENDA = {
    '1201': 'Devolução de venda de produção do estabelecimento',
    '1202': 'Devolução de venda de mercadoria adquirida ou recebida de terceiros',
    '1203': 'Devolução de venda de produção do estabelecimento destinada à ZFM/ALC',
    '1204': 'Devolução de venda de mercadoria adquirida ou recebida de terceiros destinada à ZFM/ALC',
    '1208': 'Devolução de produção do estabelecimento remetida em transferência',
    '1209': 'Devolução de mercadoria adquirida ou recebida de terceiros remetida em transferência',
    '1410': 'Devolução de venda de produção do estabelecimento com ST',
    '1411': 'Devolução de venda de mercadoria adquirida ou recebida de terceiros com ST',
    '1553': 'Devolução de venda de bem do ativo imobilizado',
    '1660': 'Devolução de venda de combustível ou lubrificante destinado a industrialização',
    '1661': 'Devolução de venda de combustível ou lubrificante destinado a comercialização',
    '1662': 'Devolução de venda de combustível ou lubrificante destinado a consumidor ou usuário final',
    '2201': 'Devolução de venda de produção do estabelecimento (interestadual)',
    '2202': 'Devolução de venda de mercadoria adquirida ou recebida de terceiros (interestadual)',
    '2203': 'Devolução de venda de produção do estabelecimento destinada à ZFM/ALC (interestadual)',
    '2204': 'Devolução de venda de mercadoria adquirida ou recebida de terceiros destinada à ZFM/ALC (interestadual)',
    '2208': 'Devolução de produção do estabelecimento remetida em transferência (interestadual)',
    '2209': 'Devolução de mercadoria adquirida ou recebida de terceiros remetida em transferência (interestadual)',
    '2410': 'Devolução de venda de produção do estabelecimento com ST (interestadual)',
    '2411': 'Devolução de venda de mercadoria adquirida ou recebida de terceiros com ST (interestadual)',
    '2553': 'Devolução de venda de bem do ativo imobilizado (interestadual)',
    '2660': 'Devolução de venda de combustível ou lubrificante destinado a industrialização (interestadual)',
    '2661': 'Devolução de venda de combustível ou lubrificante destinado a comercialização (interestadual)',
    '2662': 'Devolução de venda de combustível ou lubrificante destinado a consumidor ou usuário final (interestadual)',
}

# Devolução de COMPRA: mercadoria sendo devolvida ao fornecedor
# Escriturada como SAÍDA (ind_oper=1) com CFOP 5.xxx/6.xxx
CFOPS_DEVOLUCAO_COMPRA = {
    '5201': 'Devolução de compra para industrialização ou produção rural',
    '5202': 'Devolução de compra para comercialização ou prestação de serviços',
    '5208': 'Devolução de mercadoria recebida em transferência para industrialização ou produção rural',
    '5209': 'Devolução de mercadoria recebida em transferência para comercialização',
    '5210': 'Devolução de compra para utilização na prestação de serviço',
    '5410': 'Devolução de compra para industrialização ou produção rural com ST',
    '5411': 'Devolução de compra para comercialização com ST',
    '5412': 'Devolução de bem do ativo imobilizado em operação com ST',
    '5413': 'Devolução de mercadoria destinada ao uso ou consumo em operação com ST',
    '5503': 'Devolução de mercadoria recebida com fim específico de exportação',
    '5553': 'Devolução de compra de bem para o ativo imobilizado',
    '5556': 'Devolução de compra de material de uso ou consumo',
    '5660': 'Devolução de compra de combustível ou lubrificante adquirido para industrialização',
    '5661': 'Devolução de compra de combustível ou lubrificante adquirido para comercialização',
    '5662': 'Devolução de compra de combustível ou lubrificante adquirido por consumidor ou usuário final',
    '6201': 'Devolução de compra para industrialização ou produção rural (interestadual)',
    '6202': 'Devolução de compra para comercialização ou prestação de serviços (interestadual)',
    '6208': 'Devolução de mercadoria recebida em transferência para industrialização ou produção rural (interestadual)',
    '6209': 'Devolução de mercadoria recebida em transferência para comercialização (interestadual)',
    '6210': 'Devolução de compra para utilização na prestação de serviço (interestadual)',
    '6410': 'Devolução de compra para industrialização ou produção rural com ST (interestadual)',
    '6411': 'Devolução de compra para comercialização com ST (interestadual)',
    '6412': 'Devolução de bem do ativo imobilizado em operação com ST (interestadual)',
    '6413': 'Devolução de mercadoria destinada ao uso ou consumo em operação com ST (interestadual)',
    '6503': 'Devolução de mercadoria recebida com fim específico de exportação (interestadual)',
    '6553': 'Devolução de compra de bem para o ativo imobilizado (interestadual)',
    '6556': 'Devolução de compra de material de uso ou consumo (interestadual)',
    '6660': 'Devolução de compra de combustível ou lubrificante adquirido para industrialização (interestadual)',
    '6661': 'Devolução de compra de combustível ou lubrificante adquirido para comercialização (interestadual)',
    '6662': 'Devolução de compra de combustível ou lubrificante adquirido por consumidor ou usuário final (interestadual)',
}

# Todos os CFOPs de devolução (união dos dois dicionários)
CFOPS_DEVOLUCAO_TODOS = {}
CFOPS_DEVOLUCAO_TODOS.update(CFOPS_DEVOLUCAO_VENDA)
CFOPS_DEVOLUCAO_TODOS.update(CFOPS_DEVOLUCAO_COMPRA)

# Tolerância para comparação de somatórios (centavos)
TOLERANCIA_CENTAVOS = Decimal('0.05')


# ============================================================
# TIPOS DE RESULTADO
# ============================================================

TIPO_DEVOLUCAO_VENDA = 'DEVOLUCAO_VENDA'
TIPO_DEVOLUCAO_COMPRA = 'DEVOLUCAO_COMPRA'
TIPO_NAO_DEFINIDO = 'NAO_DEFINIDO'
TIPO_MISTO = 'MISTO'
TIPO_NAO_DEVOLUCAO = 'NAO_DEVOLUCAO'

NIVEL_ERRO = 'ERRO'
NIVEL_ALERTA = 'ALERTA'
NIVEL_INFO = 'INFO'


def criar_inconsistencia(regra, nivel, mensagem, campos=None):
    """Cria um registro de inconsistência padronizado"""
    resultado = {
        'regra': regra,
        'nivel': nivel,
        'mensagem': f"[{regra}] {mensagem}",
    }
    if campos:
        resultado['campos'] = campos
    return resultado


def classificar_cfop_devolucao(cfop):
    """
    Classifica um CFOP como devolução de venda, compra ou não-devolução.
    Retorna: (é_devolução: bool, tipo: str, descrição: str)
    """
    cfop_limpo = cfop.replace('.', '').strip()

    if cfop_limpo in CFOPS_DEVOLUCAO_VENDA:
        return True, TIPO_DEVOLUCAO_VENDA, CFOPS_DEVOLUCAO_VENDA[cfop_limpo]
    elif cfop_limpo in CFOPS_DEVOLUCAO_COMPRA:
        return True, TIPO_DEVOLUCAO_COMPRA, CFOPS_DEVOLUCAO_COMPRA[cfop_limpo]
    else:
        return False, TIPO_NAO_DEVOLUCAO, ''


def validar_regra_r1(ind_oper, cfop):
    """
    R1 - Coerência ind_oper × 1º dígito do CFOP
    - ind_oper=0 (Entrada) → CFOP deve começar com 1 ou 2
    - ind_oper=1 (Saída) → CFOP deve começar com 5 ou 6
    """
    cfop_limpo = cfop.replace('.', '').strip()
    if not cfop_limpo:
        return None  # Sem CFOP para validar

    primeiro_digito = cfop_limpo[0]

    if ind_oper == '0':  # Entrada
        if primeiro_digito not in ('1', '2'):
            return criar_inconsistencia(
                'R1', NIVEL_ERRO,
                f"CFOP {cfop} incompatível com Entrada (ind_oper=0). "
                f"Esperado CFOP iniciando com 1 ou 2, encontrado {primeiro_digito}.",
                {'ind_oper': ind_oper, 'cfop': cfop}
            )
    elif ind_oper == '1':  # Saída
        if primeiro_digito not in ('5', '6'):
            return criar_inconsistencia(
                'R1', NIVEL_ERRO,
                f"CFOP {cfop} incompatível com Saída (ind_oper=1). "
                f"Esperado CFOP iniciando com 5 ou 6, encontrado {primeiro_digito}.",
                {'ind_oper': ind_oper, 'cfop': cfop}
            )

    return None  # OK


def validar_regra_r2(cfops_documento):
    """
    R2 - Classificação do documento por CFOPs de devolução
    Retorna: (tipo_devolucao, evidencias)
    """
    tipos_encontrados = set()
    evidencias = []

    for cfop in cfops_documento:
        eh_devolucao, tipo, descricao = classificar_cfop_devolucao(cfop)
        if eh_devolucao:
            tipos_encontrados.add(tipo)
            evidencias.append(f"CFOP={cfop} ({descricao})")

    if not tipos_encontrados:
        return TIPO_NAO_DEVOLUCAO, evidencias

    if len(tipos_encontrados) == 1:
        return tipos_encontrados.pop(), evidencias

    # Múltiplos tipos — situação mista
    return TIPO_MISTO, evidencias


def validar_regra_r3(tem_ref_nfe, tipo_devolucao):
    """
    R3 - Nota referenciada como evidência
    Se classificada como devolução, verifica existência de nota referenciada.
    """
    if tipo_devolucao in (TIPO_NAO_DEVOLUCAO, TIPO_NAO_DEFINIDO):
        return None

    if tem_ref_nfe:
        return criar_inconsistencia(
            'R3', NIVEL_INFO,
            "Devolução com documento original referenciado (C113/refNFe presente).",
        )
    else:
        return criar_inconsistencia(
            'R3', NIVEL_ALERTA,
            "Devolução sem nota referenciada — revisar se a referência é obrigatória para esta UF/operação.",
        )


def validar_regra_r4(cfops_documento):
    """
    R4 - Conflitos: itens com CFOP de devolução e outros sem devolução na mesma NF
    """
    cfops_devolucao = []
    cfops_normal = []

    for cfop in cfops_documento:
        cfop_limpo = cfop.replace('.', '').strip()
        if cfop_limpo in CFOPS_DEVOLUCAO_TODOS:
            cfops_devolucao.append(cfop)
        else:
            cfops_normal.append(cfop)

    if cfops_devolucao and cfops_normal:
        return criar_inconsistencia(
            'R4', NIVEL_ERRO,
            f"NF com CFOPs mistos: devolução ({', '.join(set(cfops_devolucao))}) "
            f"e não-devolução ({', '.join(set(cfops_normal))}). "
            f"O SPED espera consistência documental.",
            {'cfops_devolucao': list(set(cfops_devolucao)), 'cfops_normal': list(set(cfops_normal))}
        )

    return None  # OK


def validar_regra_r5(itens_c170, analiticos_c190):
    """
    R5 - Consistência C170 × C190
    - Para cada CFOP no C190, deve existir pelo menos um item C170 com aquele CFOP
    - Somatórios devem bater (dentro de tolerância)
    """
    inconsistencias = []

    if not analiticos_c190:
        return inconsistencias  # Sem C190 para validar

    if not itens_c170:
        # Se há C190 mas não há C170, é esperado em NFC-e ou documentos sem itens detalhados
        return inconsistencias

    # Agrupa valores C170 por CFOP
    soma_c170_por_cfop = {}
    for item in itens_c170:
        cfop = item.get('cfop', '').replace('.', '').strip()
        if not cfop:
            continue
        if cfop not in soma_c170_por_cfop:
            soma_c170_por_cfop[cfop] = Decimal('0')
        soma_c170_por_cfop[cfop] += item.get('vl_item', Decimal('0'))

    # Valida C190 vs C170
    for c190 in analiticos_c190:
        cfop_c190 = c190.get('cfop', '').replace('.', '').strip()
        vl_opr_c190 = c190.get('vl_opr', Decimal('0'))

        if not cfop_c190:
            continue

        # Verifica existência de item C170 com esse CFOP
        if cfop_c190 not in soma_c170_por_cfop:
            inconsistencias.append(criar_inconsistencia(
                'R5', NIVEL_ALERTA,
                f"CFOP {cfop_c190} presente no C190 mas sem itens correspondentes no C170.",
                {'cfop': cfop_c190, 'vl_opr_c190': str(vl_opr_c190)}
            ))
            continue

        # Verifica somatório
        soma_c170 = soma_c170_por_cfop[cfop_c190]
        diferenca = abs(vl_opr_c190 - soma_c170)
        if diferenca > TOLERANCIA_CENTAVOS:
            inconsistencias.append(criar_inconsistencia(
                'R5', NIVEL_ERRO,
                f"CFOP {cfop_c190}: valor C190 (R$ {vl_opr_c190}) difere do somatório C170 "
                f"(R$ {soma_c170}). Diferença: R$ {diferenca}.",
                {'cfop': cfop_c190, 'vl_opr_c190': str(vl_opr_c190),
                 'soma_c170': str(soma_c170), 'diferenca': str(diferenca)}
            ))

    return inconsistencias


def validar_regra_r6(fin_nfe, tipo_devolucao_cfop):
    """
    R6 - Validação reforçada com finNFe do XML
    - finNFe=4 → devolução oficial no XML
    """
    if fin_nfe is None or fin_nfe == '':
        return None  # finNFe não disponível

    fin_nfe_str = str(fin_nfe).strip()

    if fin_nfe_str == '4':
        # XML marca como devolução
        if tipo_devolucao_cfop == TIPO_NAO_DEVOLUCAO:
            return criar_inconsistencia(
                'R6', NIVEL_ERRO,
                f"finNFe=4 (devolução no XML), mas CFOP não é de devolução — divergência.",
                {'fin_nfe': fin_nfe_str, 'tipo_cfop': tipo_devolucao_cfop}
            )
        else:
            return criar_inconsistencia(
                'R6', NIVEL_INFO,
                "Devolução confirmada: finNFe=4 e CFOP de devolução.",
                {'fin_nfe': fin_nfe_str}
            )
    else:
        # XML NÃO marca como devolução
        if tipo_devolucao_cfop in (TIPO_DEVOLUCAO_VENDA, TIPO_DEVOLUCAO_COMPRA, TIPO_MISTO):
            return criar_inconsistencia(
                'R6', NIVEL_ALERTA,
                f"CFOP indica devolução, mas finNFe={fin_nfe_str} (não é devolução) — verificar emissão/cadastro.",
                {'fin_nfe': fin_nfe_str, 'tipo_cfop': tipo_devolucao_cfop}
            )

    return None  # OK


def validar_intra_inter(cfop, uf_emitente, uf_destinatario):
    """
    Validação auxiliar: coerência intra/interestadual do CFOP
    CFOP 1.xxx/5.xxx = operação interna (mesma UF)
    CFOP 2.xxx/6.xxx = operação interestadual (UFs diferentes)
    """
    cfop_limpo = cfop.replace('.', '').strip()
    if not cfop_limpo or not uf_emitente or not uf_destinatario:
        return None

    primeiro_digito = cfop_limpo[0]
    mesma_uf = uf_emitente.upper().strip() == uf_destinatario.upper().strip()

    if primeiro_digito in ('1', '5'):
        # CFOP interno — deve ser mesma UF
        if not mesma_uf:
            return criar_inconsistencia(
                'R1-UF', NIVEL_ERRO,
                f"CFOP {cfop} é de operação interna, mas UF emitente ({uf_emitente}) "
                f"difere da UF destinatário ({uf_destinatario}).",
                {'cfop': cfop, 'uf_emitente': uf_emitente, 'uf_destinatario': uf_destinatario}
            )
    elif primeiro_digito in ('2', '6'):
        # CFOP interestadual — deve ser UFs diferentes
        if mesma_uf:
            return criar_inconsistencia(
                'R1-UF', NIVEL_ERRO,
                f"CFOP {cfop} é de operação interestadual, mas UF emitente ({uf_emitente}) "
                f"é igual à UF destinatário ({uf_destinatario}).",
                {'cfop': cfop, 'uf_emitente': uf_emitente, 'uf_destinatario': uf_destinatario}
            )

    return None  # OK


def validar_documento_c100(doc_data, uf_empresa=None, fin_nfe=None,
                           cfops_devolucao_venda_extra=None,
                           cfops_devolucao_compra_extra=None,
                           permitir_misto=False):
    """
    Validador principal para um documento C100.

    Parâmetros:
        doc_data (dict): Dados do documento com chaves:
            - ind_oper: '0' (Entrada) ou '1' (Saída)
            - num_doc: número do documento
            - chv_nfe: chave da NF-e
            - cod_part: código do participante
            - itens: lista de dicts com dados C170 (cada um com 'cfop', 'vl_item', etc.)
            - analiticos: lista de dicts com dados C190
            - referencias: lista de dicts com dados C113 (cada um com 'chv_nfe')
        uf_empresa (str): UF da empresa declarante
        fin_nfe (str): Finalidade da NF-e do XML (1=Normal, 2=Complementar, 3=Ajuste, 4=Devolução)
        cfops_devolucao_venda_extra (dict): CFOPs adicionais de devolução de venda
        cfops_devolucao_compra_extra (dict): CFOPs adicionais de devolução de compra
        permitir_misto (bool): Se True, permite NF com CFOPs mistos (devolução + normal)

    Retorna:
        dict com:
            - is_devolucao (bool)
            - tipo_devolucao (str)
            - evidencias (list)
            - inconsistencias (list)
            - num_doc (str)
            - chv_nfe (str)
    """
    # Estende tabelas de CFOP se necessário
    if cfops_devolucao_venda_extra:
        CFOPS_DEVOLUCAO_VENDA.update(cfops_devolucao_venda_extra)
        CFOPS_DEVOLUCAO_TODOS.update(cfops_devolucao_venda_extra)
    if cfops_devolucao_compra_extra:
        CFOPS_DEVOLUCAO_COMPRA.update(cfops_devolucao_compra_extra)
        CFOPS_DEVOLUCAO_TODOS.update(cfops_devolucao_compra_extra)

    resultado = {
        'is_devolucao': False,
        'tipo_devolucao': TIPO_NAO_DEFINIDO,
        'evidencias': [],
        'inconsistencias': [],
        'num_doc': doc_data.get('num_doc', ''),
        'chv_nfe': doc_data.get('chv_nfe', ''),
    }

    ind_oper = doc_data.get('ind_oper', '')
    itens = doc_data.get('itens', [])
    analiticos = doc_data.get('analiticos', [])
    referencias = doc_data.get('referencias', [])

    # Coleta todos os CFOPs do documento (de itens C170 e/ou C190)
    cfops_documento = []
    for item in itens:
        cfop = (item.get('cfop', '') or '').replace('.', '').strip()
        if cfop:
            cfops_documento.append(cfop)

    # Se não há itens C170, usa CFOPs do C190
    if not cfops_documento:
        for c190 in analiticos:
            cfop = (c190.get('cfop', '') or '').replace('.', '').strip()
            if cfop:
                cfops_documento.append(cfop)

    if not cfops_documento:
        resultado['tipo_devolucao'] = TIPO_NAO_DEFINIDO
        resultado['inconsistencias'].append(criar_inconsistencia(
            'R2', NIVEL_ALERTA,
            f"Documento {doc_data.get('num_doc', '?')} sem CFOP nos itens (C170) nem nos analíticos (C190).",
        ))
        return resultado

    # ---- R1: Coerência ind_oper × CFOP ----
    for cfop in set(cfops_documento):
        r1 = validar_regra_r1(ind_oper, cfop)
        if r1:
            resultado['inconsistencias'].append(r1)

    # ---- R1-UF: Coerência intra/interestadual ----
    if uf_empresa:
        # Tenta obter UF do participante via cod_part
        uf_participante = doc_data.get('uf_participante', '')
        if uf_participante:
            for cfop in set(cfops_documento):
                r1_uf = validar_intra_inter(cfop, uf_empresa, uf_participante)
                if r1_uf:
                    resultado['inconsistencias'].append(r1_uf)

    # ---- R2: Classificação por CFOP ----
    tipo_devolucao, evidencias_r2 = validar_regra_r2(cfops_documento)
    resultado['tipo_devolucao'] = tipo_devolucao
    resultado['evidencias'].extend(evidencias_r2)

    if tipo_devolucao in (TIPO_DEVOLUCAO_VENDA, TIPO_DEVOLUCAO_COMPRA, TIPO_MISTO):
        resultado['is_devolucao'] = True

    # ---- R3: Nota referenciada ----
    tem_ref = False
    for ref in referencias:
        chv_ref = ref.get('chv_nfe', '')
        if chv_ref and len(chv_ref) >= 44:
            tem_ref = True
            resultado['evidencias'].append(f"refNFe={chv_ref[:20]}...")
            break

    r3 = validar_regra_r3(tem_ref, tipo_devolucao)
    if r3:
        resultado['inconsistencias'].append(r3)

    # ---- R4: CFOPs mistos ----
    r4 = validar_regra_r4(cfops_documento)
    if r4:
        if permitir_misto:
            r4['nivel'] = NIVEL_ALERTA
            r4['mensagem'] = r4['mensagem'].replace('[R4]', '[R4] (modo permissivo)')
        resultado['inconsistencias'].append(r4)

    # ---- R5: Consistência C170 × C190 ----
    r5_list = validar_regra_r5(itens, analiticos)
    resultado['inconsistencias'].extend(r5_list)

    # ---- R6: finNFe do XML ----
    r6 = validar_regra_r6(fin_nfe, tipo_devolucao)
    if r6:
        resultado['inconsistencias'].append(r6)
        if fin_nfe == '4':
            resultado['evidencias'].append('finNFe=4 (devolução no XML)')

    # Evidência de coerência intra/inter
    if uf_empresa and not any(i['regra'] == 'R1-UF' for i in resultado['inconsistencias']):
        resultado['evidencias'].append('intra/inter coerente')

    return resultado


def validar_documentos_sped(dados_parseados, uf_empresa=None, fin_nfe_map=None,
                            permitir_misto=False):
    """
    Valida todos os documentos C100 de um arquivo SPED parseado.

    Parâmetros:
        dados_parseados (dict): Resultado de parse_sped_file()
        uf_empresa (str): UF da empresa declarante
        fin_nfe_map (dict): Mapa {chv_nfe: fin_nfe} com dados do XML quando disponível
        permitir_misto (bool): Se True, permite NF com CFOPs mistos

    Retorna:
        dict com:
            - total_documentos (int)
            - total_devolucoes (int)
            - devolucoes_venda (int)
            - devolucoes_compra (int)
            - documentos_misto (int)
            - total_erros (int)
            - total_alertas (int)
            - resultados (list): Lista de resultados por documento
    """
    if fin_nfe_map is None:
        fin_nfe_map = {}

    docs = dados_parseados.get('C100', [])
    resultados = []

    contadores = {
        'total_documentos': 0,
        'total_devolucoes': 0,
        'devolucoes_venda': 0,
        'devolucoes_compra': 0,
        'documentos_misto': 0,
        'total_erros': 0,
        'total_alertas': 0,
    }

    for doc in docs:
        contadores['total_documentos'] += 1

        # Obtém finNFe do mapa (se disponível via XML)
        chv_nfe = doc.get('chv_nfe', '')
        fin_nfe = fin_nfe_map.get(chv_nfe)

        # UF do participante (se disponível nos dados parseados)
        # Pode ser enriquecido cruzando com Registro 0150
        doc['uf_participante'] = doc.get('uf_participante', '')

        resultado = validar_documento_c100(
            doc_data=doc,
            uf_empresa=uf_empresa,
            fin_nfe=fin_nfe,
            permitir_misto=permitir_misto,
        )

        # Atualiza contadores
        if resultado['is_devolucao']:
            contadores['total_devolucoes'] += 1
            if resultado['tipo_devolucao'] == TIPO_DEVOLUCAO_VENDA:
                contadores['devolucoes_venda'] += 1
            elif resultado['tipo_devolucao'] == TIPO_DEVOLUCAO_COMPRA:
                contadores['devolucoes_compra'] += 1
            elif resultado['tipo_devolucao'] == TIPO_MISTO:
                contadores['documentos_misto'] += 1

        for inc in resultado['inconsistencias']:
            if inc['nivel'] == NIVEL_ERRO:
                contadores['total_erros'] += 1
            elif inc['nivel'] == NIVEL_ALERTA:
                contadores['total_alertas'] += 1

        resultados.append(resultado)

    contadores['resultados'] = resultados

    logger.info(f"Validação de devoluções concluída:")
    logger.info(f"  Total documentos: {contadores['total_documentos']}")
    logger.info(f"  Devoluções encontradas: {contadores['total_devolucoes']}")
    logger.info(f"    - Devolução de venda: {contadores['devolucoes_venda']}")
    logger.info(f"    - Devolução de compra: {contadores['devolucoes_compra']}")
    logger.info(f"    - Mistos: {contadores['documentos_misto']}")
    logger.info(f"  Erros: {contadores['total_erros']}")
    logger.info(f"  Alertas: {contadores['total_alertas']}")

    return contadores


def validar_documentos_banco(registro_0000_id, uf_empresa=None, permitir_misto=False):
    """
    Valida documentos C100 já importados no banco de dados.
    Usa os models Django diretamente.

    Parâmetros:
        registro_0000_id (int): ID do Registro0000
        uf_empresa (str): UF da empresa (se None, busca do cadastro)
        permitir_misto (bool): Permite CFOPs mistos

    Retorna:
        dict com contadores e resultados (mesmo formato de validar_documentos_sped)
    """
    from apps.sped.models import Registro0000, RegistroC100, RegistroC170, RegistroC113

    registro_0000 = Registro0000.objects.get(id=registro_0000_id)

    if not uf_empresa:
        empresa = registro_0000.empresa
        uf_empresa = getattr(empresa, 'uf', None)
        if uf_empresa and hasattr(uf_empresa, 'sigla'):
            uf_empresa = uf_empresa.sigla

    documentos = RegistroC100.objects.filter(registro_0000=registro_0000)

    contadores = {
        'total_documentos': 0,
        'total_devolucoes': 0,
        'devolucoes_venda': 0,
        'devolucoes_compra': 0,
        'documentos_misto': 0,
        'total_erros': 0,
        'total_alertas': 0,
    }
    resultados = []

    for doc in documentos:
        contadores['total_documentos'] += 1

        # Monta estrutura de dados do documento
        itens_c170 = RegistroC170.objects.filter(registro_c100=doc)
        refs_c113 = RegistroC113.objects.filter(registro_c100=doc)

        itens_list = []
        for item in itens_c170:
            itens_list.append({
                'cfop': item.cfop or '',
                'vl_item': item.vl_item or Decimal('0'),
                'cst_icms': item.cst_icms or '',
            })

        refs_list = []
        for ref in refs_c113:
            refs_list.append({
                'chv_nfe': ref.chv_nfe or '',
            })

        # Busca UF do participante via Registro0150
        uf_participante = ''
        if doc.cod_part:
            from apps.sped.models import Registro0150
            part = Registro0150.objects.filter(
                registro_0000=registro_0000,
                cod_part=doc.cod_part
            ).first()
            if part:
                uf_participante = part.uf or ''

        doc_data = {
            'ind_oper': doc.ind_oper,
            'num_doc': doc.num_doc,
            'chv_nfe': doc.chv_nfe or '',
            'cod_part': doc.cod_part or '',
            'uf_participante': uf_participante,
            'itens': itens_list,
            'analiticos': [],  # C190 não está salvo como model separado
            'referencias': refs_list,
        }

        resultado = validar_documento_c100(
            doc_data=doc_data,
            uf_empresa=uf_empresa,
            permitir_misto=permitir_misto,
        )

        if resultado['is_devolucao']:
            contadores['total_devolucoes'] += 1
            if resultado['tipo_devolucao'] == TIPO_DEVOLUCAO_VENDA:
                contadores['devolucoes_venda'] += 1
            elif resultado['tipo_devolucao'] == TIPO_DEVOLUCAO_COMPRA:
                contadores['devolucoes_compra'] += 1
            elif resultado['tipo_devolucao'] == TIPO_MISTO:
                contadores['documentos_misto'] += 1

        for inc in resultado['inconsistencias']:
            if inc['nivel'] == NIVEL_ERRO:
                contadores['total_erros'] += 1
            elif inc['nivel'] == NIVEL_ALERTA:
                contadores['total_alertas'] += 1

        resultados.append(resultado)

    contadores['resultados'] = resultados

    logger.info(f"Validação de devoluções (banco) concluída - Reg0000 ID {registro_0000_id}:")
    logger.info(f"  Total documentos: {contadores['total_documentos']}")
    logger.info(f"  Devoluções: {contadores['total_devolucoes']}")
    logger.info(f"  Erros: {contadores['total_erros']} | Alertas: {contadores['total_alertas']}")

    return contadores