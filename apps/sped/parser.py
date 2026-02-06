"""
Parser para arquivos SPED Fiscal e Contribuições
"""
from datetime import datetime
from decimal import Decimal, InvalidOperation


def parse_decimal(value, default=0):
    """Converte string para Decimal"""
    if not value or value.strip() == '':
        return Decimal(default)
    try:
        # SPED usa vírgula como separador decimal
        value = value.replace(',', '.')
        return Decimal(value)
    except (InvalidOperation, ValueError):
        return Decimal(default)


def parse_date(value):
    """Converte string DDMMAAAA para date"""
    if not value or len(value) != 8:
        return None
    try:
        return datetime.strptime(value, '%d%m%Y').date()
    except ValueError:
        return None


def parse_sped_line(line):
    """Parse de uma linha do SPED, retorna lista de campos"""
    line = line.strip()
    if not line:
        return None
    # Remove pipe inicial e final
    if line.startswith('|'):
        line = line[1:]
    if line.endswith('|'):
        line = line[:-1]
    return line.split('|')


def parse_sped_file(file_content, encoding='latin-1'):
    """
    Parse completo de um arquivo SPED
    Retorna dicionário com registros organizados por tipo
    """
    registros = {
        '0000': None,
        '0200': [],  # Itens
        '0150': [],  # Participantes
        'C100': [],  # Documentos
        'C110': [],  # Informação Complementar da NF
        'C113': [],  # Documento Fiscal Referenciado
        'C170': [],  # Itens dos documentos
        'C190': [],  # Analítico do documento
        'E111': [],  # Ajustes de Apuração ICMS
    }
    
    if isinstance(file_content, bytes):
        file_content = file_content.decode(encoding)
    
    lines = file_content.split('\n')
    current_c100 = None
    
    for line in lines:
        campos = parse_sped_line(line)
        if not campos:
            continue
        
        registro = campos[0]
        
        if registro == '0000':
            registros['0000'] = {
                'cod_ver': campos[1] if len(campos) > 1 else '',
                'cod_fin': campos[2] if len(campos) > 2 else '',
                'dt_ini': parse_date(campos[3]) if len(campos) > 3 else None,
                'dt_fin': parse_date(campos[4]) if len(campos) > 4 else None,
                'nome': campos[5] if len(campos) > 5 else '',
                'cnpj': campos[6] if len(campos) > 6 else '',
                'cpf': campos[7] if len(campos) > 7 else '',
                'uf': campos[8] if len(campos) > 8 else '',
                'ie': campos[9] if len(campos) > 9 else '',
                'cod_mun': campos[10] if len(campos) > 10 else '',
                'im': campos[11] if len(campos) > 11 else '',
                'suframa': campos[12] if len(campos) > 12 else '',
                'ind_perfil': campos[13] if len(campos) > 13 else '',
                'ind_ativ': campos[14] if len(campos) > 14 else '',
            }     
        elif registro == '0150':
            registros['0150'].append({
                'cod_part': campos[1] if len(campos) > 1 else '',
                'nome': campos[2] if len(campos) > 2 else '',
                'cod_pais': campos[3] if len(campos) > 3 else '',
                'cnpj': campos[4] if len(campos) > 4 else '',
                'cpf': campos[5] if len(campos) > 5 else '',
                'ie': campos[6] if len(campos) > 6 else '',
                'cod_mun': campos[7] if len(campos) > 7 else '',
                'suframa': campos[8] if len(campos) > 8 else '',
                'end': campos[9] if len(campos) > 9 else '',
                'num': campos[10] if len(campos) > 10 else '',
                'compl': campos[11] if len(campos) > 11 else '',
                'bairro': campos[12] if len(campos) > 12 else '',
            })
        
        elif registro == '0200':
            registros['0200'].append({
                'cod_item': campos[1] if len(campos) > 1 else '',
                'descr_item': campos[2] if len(campos) > 2 else '',
                'cod_barra': campos[3] if len(campos) > 3 else '',
                'cod_ant_item': campos[4] if len(campos) > 4 else '',
                'unid_inv': campos[5] if len(campos) > 5 else '',
                'tipo_item': campos[6] if len(campos) > 6 else '',
                'cod_ncm': campos[7] if len(campos) > 7 else '',
                'ex_ipi': campos[8] if len(campos) > 8 else '',
                'cod_gen': campos[9] if len(campos) > 9 else '',
                'cod_lst': campos[10] if len(campos) > 10 else '',
                'aliq_icms': parse_decimal(campos[11]) if len(campos) > 11 else Decimal(0),
                'cest': campos[12] if len(campos) > 12 else '',
            })
        
        elif registro == 'C100':
            current_c100 = {
                'ind_oper': campos[1] if len(campos) > 1 else '',
                'ind_emit': campos[2] if len(campos) > 2 else '',
                'cod_part': campos[3] if len(campos) > 3 else '',
                'cod_mod': campos[4] if len(campos) > 4 else '',
                'cod_sit': campos[5] if len(campos) > 5 else '',
                'ser': campos[6] if len(campos) > 6 else '',
                'num_doc': campos[7] if len(campos) > 7 else '',
                'chv_nfe': campos[8] if len(campos) > 8 else '',
                'dt_doc': parse_date(campos[9]) if len(campos) > 9 else None,
                'dt_e_s': parse_date(campos[10]) if len(campos) > 10 else None,
                'vl_doc': parse_decimal(campos[11]) if len(campos) > 11 else Decimal(0),
                'ind_pgto': campos[12] if len(campos) > 12 else '',
                'vl_desc': parse_decimal(campos[13]) if len(campos) > 13 else Decimal(0),
                'vl_abat_nt': parse_decimal(campos[14]) if len(campos) > 14 else Decimal(0),
                'vl_merc': parse_decimal(campos[15]) if len(campos) > 15 else Decimal(0),
                'ind_frt': campos[16] if len(campos) > 16 else '',
                'vl_frt': parse_decimal(campos[17]) if len(campos) > 17 else Decimal(0),
                'vl_seg': parse_decimal(campos[18]) if len(campos) > 18 else Decimal(0),
                'vl_out_da': parse_decimal(campos[19]) if len(campos) > 19 else Decimal(0),
                'vl_bc_icms': parse_decimal(campos[20]) if len(campos) > 20 else Decimal(0),
                'vl_icms': parse_decimal(campos[21]) if len(campos) > 21 else Decimal(0),
                'vl_bc_icms_st': parse_decimal(campos[22]) if len(campos) > 22 else Decimal(0),
                'vl_icms_st': parse_decimal(campos[23]) if len(campos) > 23 else Decimal(0),
                'vl_ipi': parse_decimal(campos[24]) if len(campos) > 24 else Decimal(0),
                'vl_pis': parse_decimal(campos[25]) if len(campos) > 25 else Decimal(0),
                'vl_cofins': parse_decimal(campos[26]) if len(campos) > 26 else Decimal(0),
                'vl_pis_st': parse_decimal(campos[27]) if len(campos) > 27 else Decimal(0),
                'vl_cofins_st': parse_decimal(campos[28]) if len(campos) > 28 else Decimal(0),
                'itens': [],
            }
            registros['C100'].append(current_c100)
        
        elif registro == 'C170' and current_c100:
            item = {
                'num_item': campos[1] if len(campos) > 1 else '',
                'cod_item': campos[2] if len(campos) > 2 else '',
                'descr_compl': campos[3] if len(campos) > 3 else '',
                'qtd': parse_decimal(campos[4]) if len(campos) > 4 else Decimal(0),
                'unid': campos[5] if len(campos) > 5 else '',
                'vl_item': parse_decimal(campos[6]) if len(campos) > 6 else Decimal(0),
                'vl_desc': parse_decimal(campos[7]) if len(campos) > 7 else Decimal(0),
                'ind_mov': campos[8] if len(campos) > 8 else '',
                'cst_icms': campos[9] if len(campos) > 9 else '',
                'cfop': campos[10] if len(campos) > 10 else '',
                'cod_nat': campos[11] if len(campos) > 11 else '',
                'vl_bc_icms': parse_decimal(campos[12]) if len(campos) > 12 else Decimal(0),
                'aliq_icms': parse_decimal(campos[13]) if len(campos) > 13 else Decimal(0),
                'vl_icms': parse_decimal(campos[14]) if len(campos) > 14 else Decimal(0),
                'vl_bc_icms_st': parse_decimal(campos[15]) if len(campos) > 15 else Decimal(0),
                'aliq_st': parse_decimal(campos[16]) if len(campos) > 16 else Decimal(0),
                'vl_icms_st': parse_decimal(campos[17]) if len(campos) > 17 else Decimal(0),
                'ind_apur': campos[18] if len(campos) > 18 else '',
                'cst_ipi': campos[19] if len(campos) > 19 else '',
                'cod_enq': campos[20] if len(campos) > 20 else '',
                'vl_bc_ipi': parse_decimal(campos[21]) if len(campos) > 21 else Decimal(0),
                'aliq_ipi': parse_decimal(campos[22]) if len(campos) > 22 else Decimal(0),
                'vl_ipi': parse_decimal(campos[23]) if len(campos) > 23 else Decimal(0),
                'cst_pis': campos[24] if len(campos) > 24 else '',
                'vl_bc_pis': parse_decimal(campos[25]) if len(campos) > 25 else Decimal(0),
                'aliq_pis_percent': parse_decimal(campos[26]) if len(campos) > 26 else Decimal(0),
                'quant_bc_pis': parse_decimal(campos[27]) if len(campos) > 27 else Decimal(0),
                'aliq_pis_reais': parse_decimal(campos[28]) if len(campos) > 28 else Decimal(0),
                'vl_pis': parse_decimal(campos[29]) if len(campos) > 29 else Decimal(0),
                'cst_cofins': campos[30] if len(campos) > 30 else '',
                'vl_bc_cofins': parse_decimal(campos[31]) if len(campos) > 31 else Decimal(0),
                'aliq_cofins_percent': parse_decimal(campos[32]) if len(campos) > 32 else Decimal(0),
                'quant_bc_cofins': parse_decimal(campos[33]) if len(campos) > 33 else Decimal(0),
                'aliq_cofins_reais': parse_decimal(campos[34]) if len(campos) > 34 else Decimal(0),
                'vl_cofins': parse_decimal(campos[35]) if len(campos) > 35 else Decimal(0),
                'cod_cta': campos[36] if len(campos) > 36 else '',
            }
            current_c100['itens'].append(item)
            registros['C170'].append(item)
        
        elif registro == 'C110' and current_c100:
            c110_data = {
                'cod_inf': campos[1] if len(campos) > 1 else '',
                'txt_compl': campos[2] if len(campos) > 2 else '',
            }
            if 'complementares' not in current_c100:
                current_c100['complementares'] = []
            current_c100['complementares'].append(c110_data)
            registros['C110'].append(c110_data)

        elif registro == 'C113' and current_c100:
            c113_data = {
                'ind_oper': campos[1] if len(campos) > 1 else '',
                'ind_emit': campos[2] if len(campos) > 2 else '',
                'cod_part': campos[3] if len(campos) > 3 else '',
                'cod_mod': campos[4] if len(campos) > 4 else '',
                'ser': campos[5] if len(campos) > 5 else '',
                'sub': campos[6] if len(campos) > 6 else '',
                'num_doc': campos[7] if len(campos) > 7 else '',
                'dt_doc': parse_date(campos[8]) if len(campos) > 8 else None,
                'chv_nfe': campos[9] if len(campos) > 9 else '',
            }
            if 'referencias' not in current_c100:
                current_c100['referencias'] = []
            current_c100['referencias'].append(c113_data)
            registros['C113'].append(c113_data)

        elif registro == 'E111':
            registros['E111'].append({
                'cod_aj_apur': campos[1] if len(campos) > 1 else '',
                'descr_compl_aj': campos[2] if len(campos) > 2 else '',
                'vl_aj_apur': parse_decimal(campos[3]) if len(campos) > 3 else Decimal(0),
            })
    
    return registros