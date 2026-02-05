"""
Serviços para processamento de SPED
"""
import logging
from django.db import transaction
from apps.sped.models import Registro0000, Registro0200, RegistroC100, RegistroC170
from apps.sped.parser import parse_sped_file
from apps.documentos_fiscais.models import NFe
from apps.reforma_tributaria.models import ItemNCM
from apps.empresa.models import Empresa

# Logger para processamento
logger = logging.getLogger('sped.processamento')


def processar_sped_completo(registro_0000_id):
    """
    Processa um arquivo SPED já importado e popula os módulos relacionados
    """
    logger.info("=" * 60)
    logger.info(f"PROCESSAMENTO COMPLETO - Registro 0000 ID: {registro_0000_id}")
    logger.info("=" * 60)
    
    registro_0000 = Registro0000.objects.get(id=registro_0000_id)
    logger.info(f"Empresa: {registro_0000.empresa.razao_social}")
    logger.info(f"CNPJ: {registro_0000.empresa.cnpj_cpf}")
    logger.info(f"Tipo: {registro_0000.tipo}")
    logger.info(f"Período: {registro_0000.periodo}")
    
    # Lê o arquivo
    arquivo = registro_0000.arquivo_original
    arquivo.open('rb')
    conteudo = arquivo.read()
    arquivo.close()
    logger.info(f"Arquivo lido: {arquivo.name} ({len(conteudo)} bytes)")
    
    # Parse do arquivo
    logger.info("Iniciando parse do arquivo...")
    dados = parse_sped_file(conteudo)
    
    qtd_0200 = len(dados.get('0200', []))
    qtd_c100 = len(dados.get('C100', []))
    qtd_c170 = len(dados.get('C170', []))
    
    logger.info(f"Parse concluído:")
    logger.info(f"  - Itens (0200): {qtd_0200}")
    logger.info(f"  - Documentos (C100): {qtd_c100}")
    logger.info(f"  - Itens de Doc (C170): {qtd_c170}")
    
    resultado = {
        'itens': 0,
        'documentos': 0,
        'nfes_criadas': 0,
        'itens_ncm': 0,
    }
    
    with transaction.atomic():
        # Processa itens (0200)
        logger.info("-" * 40)
        logger.info("Processando Itens (Registro 0200)...")
        resultado['itens'] = processar_itens_0200(registro_0000, dados.get('0200', []))
        logger.info(f"  → {resultado['itens']} itens processados")
        
        # Processa documentos (C100)
        logger.info("-" * 40)
        logger.info("Processando Documentos (Registro C100)...")
        resultado['documentos'] = processar_documentos_c100(registro_0000, dados.get('C100', []))
        logger.info(f"  → {resultado['documentos']} documentos processados")
        
        # Popula documentos fiscais (NF-e)
        logger.info("-" * 40)
        logger.info("Populando Documentos Fiscais (NF-e)...")
        resultado['nfes_criadas'] = popular_documentos_fiscais(registro_0000, dados.get('C100', []))
        logger.info(f"  → {resultado['nfes_criadas']} NF-es criadas/atualizadas")
        
        # Popula NCM x cClassTrib
        logger.info("-" * 40)
        logger.info("Populando NCM x cClassTrib...")
        resultado['itens_ncm'] = popular_ncm_classtrib(registro_0000, dados)
        logger.info(f"  → {resultado['itens_ncm']} itens NCM criados/atualizados")
        
        # Marca como processado
        registro_0000.processado = True
        registro_0000.save()
    
    logger.info("=" * 60)
    logger.info("RESUMO DO PROCESSAMENTO")
    logger.info("=" * 60)
    logger.info(f"Itens 0200: {resultado['itens']}")
    logger.info(f"Documentos C100: {resultado['documentos']}")
    logger.info(f"NF-es: {resultado['nfes_criadas']}")
    logger.info(f"Itens NCM: {resultado['itens_ncm']}")
    logger.info(f"Status: PROCESSADO COM SUCESSO")
    logger.info("=" * 60)
    
    return resultado


def processar_itens_0200(registro_0000, itens_data):
    """Processa e salva os registros 0200 (Itens)"""
    count = 0
    for item in itens_data:
        obj, created = Registro0200.objects.update_or_create(
            registro_0000=registro_0000,
            cod_item=item['cod_item'],
            defaults={
                'descr_item': item['descr_item'],
                'cod_barra': item.get('cod_barra', ''),
                'unid_inv': item.get('unid_inv', ''),
                'tipo_item': item.get('tipo_item', ''),
                'cod_ncm': item.get('cod_ncm', ''),
                'cest': item.get('cest', ''),
                'aliq_icms': item.get('aliq_icms', 0),
            }
        )
        count += 1
        if count <= 5 or count % 100 == 0:
            logger.debug(f"  Item {count}: {item['cod_item']} - NCM: {item.get('cod_ncm', 'N/A')} - {'CRIADO' if created else 'ATUALIZADO'}")
    
    return count


"""
Serviços para processamento de SPED
"""
import logging
from django.db import transaction
from apps.sped.models import Registro0000, Registro0200, RegistroC100, RegistroC170
from apps.sped.parser import parse_sped_file
from apps.documentos_fiscais.models import NFe
from apps.reforma_tributaria.models import ItemNCM
from apps.empresa.models import Empresa

# Logger para processamento
logger = logging.getLogger('sped.processamento')


def processar_sped_completo(registro_0000_id):
    """
    Processa um arquivo SPED já importado e popula os módulos relacionados
    """
    logger.info("=" * 60)
    logger.info(f"PROCESSAMENTO COMPLETO - Registro 0000 ID: {registro_0000_id}")
    logger.info("=" * 60)
    
    registro_0000 = Registro0000.objects.get(id=registro_0000_id)
    logger.info(f"Empresa: {registro_0000.empresa.razao_social}")
    logger.info(f"CNPJ: {registro_0000.empresa.cnpj_cpf}")
    logger.info(f"Tipo: {registro_0000.tipo}")
    logger.info(f"Período: {registro_0000.periodo}")
    
    # Lê o arquivo
    arquivo = registro_0000.arquivo_original
    arquivo.open('rb')
    conteudo = arquivo.read()
    arquivo.close()
    logger.info(f"Arquivo lido: {arquivo.name} ({len(conteudo)} bytes)")
    
    # Parse do arquivo
    logger.info("Iniciando parse do arquivo...")
    dados = parse_sped_file(conteudo)
    
    qtd_0200 = len(dados.get('0200', []))
    qtd_c100 = len(dados.get('C100', []))
    qtd_c170 = len(dados.get('C170', []))
    
    logger.info(f"Parse concluído:")
    logger.info(f"  - Itens (0200): {qtd_0200}")
    logger.info(f"  - Documentos (C100): {qtd_c100}")
    logger.info(f"  - Itens de Doc (C170): {qtd_c170}")
    
    resultado = {
        'participantes': 0,
        'itens': 0,
        'documentos': 0,
        'nfes_criadas': 0,
        'itens_ncm': 0,
    }
    
    with transaction.atomic():
        # Processa participantes (0150)
        logger.info("-" * 40)
        logger.info("Processando Participantes (Registro 0150)...")
        resultado['participantes'] = processar_participantes_0150(registro_0000, dados.get('0150', []))
        logger.info(f"  → {resultado['participantes']} participantes processados")
        
        # Processa itens (0200)
        logger.info("-" * 40)
        logger.info("Processando Itens (Registro 0200)...")
        resultado['itens'] = processar_itens_0200(registro_0000, dados.get('0200', []))
        logger.info(f"  → {resultado['itens']} itens processados")
        
        # Processa documentos (C100)
        logger.info("-" * 40)
        logger.info("Processando Documentos (Registro C100)...")
        resultado['documentos'] = processar_documentos_c100(registro_0000, dados.get('C100', []))
        logger.info(f"  → {resultado['documentos']} documentos processados")
        
        # Popula documentos fiscais (NF-e)
        logger.info("-" * 40)
        logger.info("Populando Documentos Fiscais (NF-e)...")
        resultado['nfes_criadas'] = popular_documentos_fiscais(registro_0000, dados.get('C100', []))
        logger.info(f"  → {resultado['nfes_criadas']} NF-es criadas/atualizadas")
        
        # Popula NCM x cClassTrib
        logger.info("-" * 40)
        logger.info("Populando NCM x cClassTrib...")
        resultado['itens_ncm'] = popular_ncm_classtrib(registro_0000, dados)
        logger.info(f"  → {resultado['itens_ncm']} itens NCM criados/atualizados")
        
        # Marca como processado
        registro_0000.processado = True
        registro_0000.save()
    
    logger.info("=" * 60)
    logger.info("RESUMO DO PROCESSAMENTO")
    logger.info("=" * 60)
    logger.info(f"Itens 0200: {resultado['itens']}")
    logger.info(f"Documentos C100: {resultado['documentos']}")
    logger.info(f"NF-es: {resultado['nfes_criadas']}")
    logger.info(f"Itens NCM: {resultado['itens_ncm']}")
    logger.info(f"Status: PROCESSADO COM SUCESSO")
    logger.info("=" * 60)
    
    return resultado


def processar_itens_0200(registro_0000, itens_data):
    """Processa e salva os registros 0200 (Itens)"""
    count = 0
    for item in itens_data:
        obj, created = Registro0200.objects.update_or_create(
            registro_0000=registro_0000,
            cod_item=item['cod_item'],
            defaults={
                'descr_item': item['descr_item'],
                'cod_barra': item.get('cod_barra', ''),
                'unid_inv': item.get('unid_inv', ''),
                'tipo_item': item.get('tipo_item', ''),
                'cod_ncm': item.get('cod_ncm', ''),
                'cest': item.get('cest', ''),
                'aliq_icms': item.get('aliq_icms', 0),
            }
        )
        count += 1
        if count <= 5 or count % 100 == 0:
            logger.debug(f"  Item {count}: {item['cod_item']} - NCM: {item.get('cod_ncm', 'N/A')} - {'CRIADO' if created else 'ATUALIZADO'}")
    
    return count


def processar_documentos_c100(registro_0000, docs_data):
    """Processa e salva os registros C100 e C170"""
    count_docs = 0
    count_itens = 0
    
    for doc in docs_data:
        c100, created = RegistroC100.objects.update_or_create(
            registro_0000=registro_0000,
            num_doc=doc['num_doc'],
            ser=doc.get('ser', ''),
            cod_mod=doc['cod_mod'],
            ind_oper=doc['ind_oper'],
            defaults={
                'ind_emit': doc['ind_emit'],
                'cod_part': doc.get('cod_part', ''),
                'cod_sit': doc.get('cod_sit', ''),
                'chv_nfe': doc.get('chv_nfe', ''),
                'dt_doc': doc.get('dt_doc'),
                'dt_e_s': doc.get('dt_e_s'),
                'vl_doc': doc.get('vl_doc', 0),
                'vl_merc': doc.get('vl_merc', 0),
                'vl_icms': doc.get('vl_icms', 0),
                'vl_pis': doc.get('vl_pis', 0),
                'vl_cofins': doc.get('vl_cofins', 0),
            }
        )
        count_docs += 1
        
        # Processa itens do documento
        for item in doc.get('itens', []):
            # Busca NCM do item no registro 0200
            item_0200 = Registro0200.objects.filter(
                registro_0000=registro_0000,
                cod_item=item['cod_item']
            ).first()
            
            cod_ncm = item_0200.cod_ncm if item_0200 else ''
            
            RegistroC170.objects.update_or_create(
                registro_c100=c100,
                num_item=item['num_item'],
                defaults={
                    'cod_item': item['cod_item'],
                    'descr_compl': item.get('descr_compl', ''),
                    'qtd': item.get('qtd', 0),
                    'unid': item.get('unid', ''),
                    'vl_item': item.get('vl_item', 0),
                    'vl_desc': item.get('vl_desc', 0),
                    'cst_icms': item.get('cst_icms', ''),
                    'cfop': item.get('cfop', ''),
                    'cod_nat': item.get('cod_nat', ''),
                    'vl_bc_icms': item.get('vl_bc_icms', 0),
                    'aliq_icms': item.get('aliq_icms', 0),
                    'vl_icms': item.get('vl_icms', 0),
                    'cst_pis': item.get('cst_pis', ''),
                    'vl_bc_pis': item.get('vl_bc_pis', 0),
                    'aliq_pis': item.get('aliq_pis_percent', 0),
                    'vl_pis': item.get('vl_pis', 0),
                    'cst_cofins': item.get('cst_cofins', ''),
                    'vl_bc_cofins': item.get('vl_bc_cofins', 0),
                    'aliq_cofins': item.get('aliq_cofins_percent', 0),
                    'vl_cofins': item.get('vl_cofins', 0),
                    'cod_ncm': cod_ncm,
                }
            )
            count_itens += 1
    
    logger.debug(f"  Documentos C100: {count_docs} | Itens C170: {count_itens}")
    return count_docs


def popular_documentos_fiscais(registro_0000, docs_data):
    """Popula o módulo de Documentos Fiscais (NF-e) a partir do SPED"""
    empresa = registro_0000.empresa
    count = 0
    
    for doc in docs_data:
        # Apenas NF-e (modelo 55) e NFC-e (modelo 65)
        if doc['cod_mod'] not in ['55', '65']:
            logger.debug(f"  Ignorando documento modelo {doc['cod_mod']} (não é NF-e/NFC-e)")
            continue
        
        # Ignora documentos cancelados (cod_sit != 00)
        if doc.get('cod_sit', '00') != '00':
            logger.debug(f"  Ignorando documento {doc['num_doc']} - Situação: {doc.get('cod_sit')}")
            continue
        
        chave = doc.get('chv_nfe', '')
        if not chave or len(chave) != 44:
            # Gera chave fictícia se não tiver
            cnpj_limpo = ''.join(filter(str.isdigit, empresa.cnpj_cpf))
            chave = f"{cnpj_limpo[:14]}{doc.get('ser','001').zfill(3)}{doc['num_doc'].zfill(9)}".ljust(44, '0')[:44]
            logger.debug(f"  Chave gerada para doc {doc['num_doc']}: {chave[:20]}...")
        
        obj, created = NFe.objects.update_or_create(
            chave_acesso=chave,
            defaults={
                'empresa': empresa,
                'numero': int(doc['num_doc']) if doc['num_doc'].isdigit() else 0,
                'serie': doc.get('ser', '1'),
                'data_emissao': doc.get('dt_doc') or registro_0000.periodo,
                'valor_total': doc.get('vl_doc', 0),
                'modelo': doc['cod_mod'],
            }
        )
        count += 1
        logger.debug(f"  NF-e {doc['num_doc']}: R$ {doc.get('vl_doc', 0)} - {'CRIADA' if created else 'ATUALIZADA'}")
    
    return count


def popular_ncm_classtrib(registro_0000, dados):
    """Popula o módulo NCM x cClassTrib a partir do SPED"""
    empresa = registro_0000.empresa
    itens_0200 = dados.get('0200', [])
    docs_c100 = dados.get('C100', [])
    count = 0
    
    logger.debug(f"  Mapeando CST de {len(docs_c100)} documentos...")
    
    # Mapeia CST por item
    cst_por_item = {}
    for doc in docs_c100:
        for item in doc.get('itens', []):
            cod_item = item.get('cod_item', '')
            if cod_item and cod_item not in cst_por_item:
                cst_por_item[cod_item] = {
                    'cst_icms': item.get('cst_icms', ''),
                    'cst_pis': item.get('cst_pis', ''),
                    'cst_cofins': item.get('cst_cofins', ''),
                    'cfop': item.get('cfop', ''),
                    'aliq_icms': item.get('aliq_icms', 0),
                    'aliq_pis': item.get('aliq_pis_percent', 0),
                    'aliq_cofins': item.get('aliq_cofins_percent', 0),
                }
    
    logger.debug(f"  CST mapeado para {len(cst_por_item)} itens")
    
    # Cria registros de NCM
    itens_sem_ncm = 0
    for item in itens_0200:
        cod_item = item.get('cod_item', '')
        cod_ncm = item.get('cod_ncm', '')
        
        if not cod_ncm:
            itens_sem_ncm += 1
            continue
        
        cst_info = cst_por_item.get(cod_item, {})
        
        obj, created = ItemNCM.objects.update_or_create(
            empresa=empresa,
            cod_item=cod_item,
            defaults={
                'descricao': item.get('descr_item', ''),
                'cod_ncm': cod_ncm,
                'cest': item.get('cest', ''),
                'cod_barra': item.get('cod_barra', ''),
                'unidade': item.get('unid_inv', ''),
                'cst_icms': cst_info.get('cst_icms', ''),
                'cst_pis': cst_info.get('cst_pis', ''),
                'cst_cofins': cst_info.get('cst_cofins', ''),
                'cfop': cst_info.get('cfop', ''),
                'aliq_icms': cst_info.get('aliq_icms', 0),
                'aliq_pis': cst_info.get('aliq_pis', 0),
                'aliq_cofins': cst_info.get('aliq_cofins', 0),
                'origem': 'SPED',
                'registro_0000': registro_0000,
            }
        )
        count += 1
        if count <= 3 or count % 50 == 0:
            logger.debug(f"  NCM {cod_ncm} - Item {cod_item}: CST ICMS={cst_info.get('cst_icms', 'N/A')} - {'CRIADO' if created else 'ATUALIZADO'}")
    
    if itens_sem_ncm > 0:
        logger.warning(f"  ⚠ {itens_sem_ncm} itens ignorados (sem NCM)")
    
    return count


def processar_participantes_0150(registro_0000, participantes_data):
    """Processa e salva os registros 0150 (Participantes)"""
    from apps.sped.models import Registro0150
    
    count = 0
    for part in participantes_data:
        obj, created = Registro0150.objects.update_or_create(
            registro_0000=registro_0000,
            cod_part=part['cod_part'],
            defaults={
                'nome': part.get('nome', ''),
                'cnpj': part.get('cnpj', '').replace('.', '').replace('/', '').replace('-', ''),
                'cpf': part.get('cpf', '').replace('.', '').replace('-', ''),
                'ie': part.get('ie', ''),
                'cod_mun': part.get('cod_mun', ''),
                'endereco': part.get('end', ''),
            }
        )
        count += 1
        if count <= 5 or count % 100 == 0:
            logger.debug(f"  Participante {count}: {part['cod_part']} - {part.get('nome', 'N/A')[:30]} - {'CRIADO' if created else 'ATUALIZADO'}")
    
    return count


def popular_documentos_fiscais(registro_0000, docs_data):
    """Popula o módulo de Documentos Fiscais (NF-e) a partir do SPED"""
    empresa = registro_0000.empresa
    count = 0
    
    for doc in docs_data:
        # Apenas NF-e (modelo 55) e NFC-e (modelo 65)
        if doc['cod_mod'] not in ['55', '65']:
            logger.debug(f"  Ignorando documento modelo {doc['cod_mod']} (não é NF-e/NFC-e)")
            continue
        
        # Ignora documentos cancelados (cod_sit != 00)
        if doc.get('cod_sit', '00') != '00':
            logger.debug(f"  Ignorando documento {doc['num_doc']} - Situação: {doc.get('cod_sit')}")
            continue
        
        chave = doc.get('chv_nfe', '')
        if not chave or len(chave) != 44:
            # Gera chave fictícia se não tiver
            chave = f"{empresa.cnpj_cpf[:14].replace('.','').replace('/','').replace('-','')}{doc.get('ser','001').zfill(3)}{doc['num_doc'].zfill(9)}".ljust(44, '0')[:44]
            logger.debug(f"  Chave gerada para doc {doc['num_doc']}: {chave[:20]}...")
        
        obj, created = NFe.objects.update_or_create(
            chave_acesso=chave,
            defaults={
                'empresa': empresa,
                'numero': int(doc['num_doc']) if doc['num_doc'].isdigit() else 0,
                'serie': doc.get('ser', '1'),
                'data_emissao': doc.get('dt_doc') or registro_0000.periodo,
                'valor_total': doc.get('vl_doc', 0),
                'modelo': doc['cod_mod'],
            }
        )
        count += 1
        logger.debug(f"  NF-e {doc['num_doc']}: R$ {doc.get('vl_doc', 0)} - {'CRIADA' if created else 'ATUALIZADA'}")
    
    return count


def popular_ncm_classtrib(registro_0000, dados):
    """Popula o módulo NCM x cClassTrib a partir do SPED"""
    empresa = registro_0000.empresa
    itens_0200 = dados.get('0200', [])
    docs_c100 = dados.get('C100', [])
    count = 0
    
    logger.debug(f"  Mapeando CST de {len(docs_c100)} documentos...")
    
    # Mapeia CST por item
    cst_por_item = {}
    for doc in docs_c100:
        for item in doc.get('itens', []):
            cod_item = item.get('cod_item', '')
            if cod_item and cod_item not in cst_por_item:
                cst_por_item[cod_item] = {
                    'cst_icms': item.get('cst_icms', ''),
                    'cst_pis': item.get('cst_pis', ''),
                    'cst_cofins': item.get('cst_cofins', ''),
                    'cfop': item.get('cfop', ''),
                    'aliq_icms': item.get('aliq_icms', 0),
                    'aliq_pis': item.get('aliq_pis_percent', 0),
                    'aliq_cofins': item.get('aliq_cofins_percent', 0),
                }
    
    logger.debug(f"  CST mapeado para {len(cst_por_item)} itens")
    
    # Cria registros de NCM
    itens_sem_ncm = 0
    for item in itens_0200:
        cod_item = item.get('cod_item', '')
        cod_ncm = item.get('cod_ncm', '')
        
        if not cod_ncm:
            itens_sem_ncm += 1
            continue
        
        cst_info = cst_por_item.get(cod_item, {})
        
        obj, created = ItemNCM.objects.update_or_create(
            empresa=empresa,
            cod_item=cod_item,
            defaults={
                'descricao': item.get('descr_item', ''),
                'cod_ncm': cod_ncm,
                'cest': item.get('cest', ''),
                'cod_barra': item.get('cod_barra', ''),
                'unidade': item.get('unid_inv', ''),
                'cst_icms': cst_info.get('cst_icms', ''),
                'cst_pis': cst_info.get('cst_pis', ''),
                'cst_cofins': cst_info.get('cst_cofins', ''),
                'cfop': cst_info.get('cfop', ''),
                'aliq_icms': cst_info.get('aliq_icms', 0),
                'aliq_pis': cst_info.get('aliq_pis', 0),
                'aliq_cofins': cst_info.get('aliq_cofins', 0),
                'origem': 'SPED',
                'registro_0000': registro_0000,
            }
        )
        count += 1
        if count <= 3 or count % 50 == 0:
            logger.debug(f"  NCM {cod_ncm} - Item {cod_item}: CST ICMS={cst_info.get('cst_icms', 'N/A')} - {'CRIADO' if created else 'ATUALIZADO'}")
    
    if itens_sem_ncm > 0:
        logger.warning(f"  ⚠ {itens_sem_ncm} itens ignorados (sem NCM)")
    
    return count