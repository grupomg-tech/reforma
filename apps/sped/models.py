from django.db import models
from apps.empresa.models import Empresa


class Registro0000(models.Model):
    TIPO_CHOICES = [
        ('fiscal', 'SPED Fiscal'),
        ('registro', 'SPED Contribuições'),
    ]
    
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    periodo = models.DateField()
    arquivo_original = models.FileField(upload_to='sped/')
    processado = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Registro 0000'
        verbose_name_plural = 'Registros 0000'
        unique_together = ['empresa', 'tipo', 'periodo']
    
    def __str__(self):
        return f"{self.empresa.cnpj_cpf} - {self.tipo} - {self.periodo}"


class Registro0200(models.Model):
    """Tabela de Identificação do Item (Produtos e Serviços)"""
    registro_0000 = models.ForeignKey(Registro0000, on_delete=models.CASCADE, related_name='itens')
    cod_item = models.CharField('Código do Item', max_length=60)
    descr_item = models.TextField('Descrição do Item')
    cod_barra = models.CharField('Código de Barras', max_length=14, blank=True)
    unid_inv = models.CharField('Unidade de Inventário', max_length=6, blank=True)
    tipo_item = models.CharField('Tipo do Item', max_length=2, blank=True)
    cod_ncm = models.CharField('NCM', max_length=8, blank=True)
    cest = models.CharField('CEST', max_length=7, blank=True)
    aliq_icms = models.DecimalField('Alíquota ICMS', max_digits=6, decimal_places=2, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Item (Registro 0200)'
        verbose_name_plural = 'Itens (Registros 0200)'
        unique_together = ['registro_0000', 'cod_item']
    
    def __str__(self):
        return f"{self.cod_item} - {self.descr_item[:50]}"


class RegistroC100(models.Model):
    """Documento - Nota Fiscal (Código 01, 1B, 04, 55 e 65)"""
    registro_0000 = models.ForeignKey(Registro0000, on_delete=models.CASCADE, related_name='documentos_c100')
    ind_oper = models.CharField('Indicador de Operação', max_length=1)  # 0=Entrada, 1=Saída
    ind_emit = models.CharField('Indicador do Emitente', max_length=1)  # 0=Próprio, 1=Terceiros
    cod_part = models.CharField('Código do Participante', max_length=60, blank=True)
    cod_mod = models.CharField('Código do Modelo', max_length=2)
    cod_sit = models.CharField('Código da Situação', max_length=2)
    ser = models.CharField('Série', max_length=3, blank=True)
    num_doc = models.CharField('Número do Documento', max_length=9)
    chv_nfe = models.CharField('Chave NF-e', max_length=44, blank=True)
    dt_doc = models.DateField('Data do Documento', null=True, blank=True)
    dt_e_s = models.DateField('Data Entrada/Saída', null=True, blank=True)
    vl_doc = models.DecimalField('Valor do Documento', max_digits=15, decimal_places=2, default=0)
    vl_merc = models.DecimalField('Valor das Mercadorias', max_digits=15, decimal_places=2, default=0)
    vl_icms = models.DecimalField('Valor do ICMS', max_digits=15, decimal_places=2, default=0)
    vl_pis = models.DecimalField('Valor do PIS', max_digits=15, decimal_places=2, default=0)
    vl_cofins = models.DecimalField('Valor do COFINS', max_digits=15, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = 'Documento C100'
        verbose_name_plural = 'Documentos C100'
    
    def __str__(self):
        return f"{self.cod_mod} {self.ser}/{self.num_doc}"


class Registro0150(models.Model):
    """Tabela de Cadastro do Participante"""
    registro_0000 = models.ForeignKey(Registro0000, on_delete=models.CASCADE, related_name='participantes')
    cod_part = models.CharField('Código do Participante', max_length=60)
    nome = models.CharField('Nome/Razão Social', max_length=200)
    cnpj = models.CharField('CNPJ', max_length=14, blank=True)
    cpf = models.CharField('CPF', max_length=11, blank=True)
    ie = models.CharField('Inscrição Estadual', max_length=20, blank=True)
    cod_mun = models.CharField('Código Município', max_length=7, blank=True)
    uf = models.CharField('UF', max_length=2, blank=True)
    endereco = models.CharField('Endereço', max_length=200, blank=True)
    
    # Campos de consulta (preenchidos pela API)
    situacao_cadastral = models.CharField('Situação Cadastral', max_length=50, blank=True)
    optante_simples = models.BooleanField('Optante Simples Nacional', null=True, blank=True)
    data_opcao_simples = models.DateField('Data Opção Simples', null=True, blank=True)
    data_exclusao_simples = models.DateField('Data Exclusão Simples', null=True, blank=True)
    optante_mei = models.BooleanField('Optante MEI', null=True, blank=True)
    natureza_juridica = models.CharField('Natureza Jurídica', max_length=100, blank=True)
    porte = models.CharField('Porte', max_length=50, blank=True)
    cnae_principal = models.CharField('CNAE Principal', max_length=10, blank=True)
    descricao_cnae = models.CharField('Descrição CNAE', max_length=200, blank=True)
    
    # Controle de consulta
    consultado = models.BooleanField('Consultado', default=False)
    data_consulta = models.DateTimeField('Data da Consulta', null=True, blank=True)
    erro_consulta = models.TextField('Erro na Consulta', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Participante (Registro 0150)'
        verbose_name_plural = 'Participantes (Registros 0150)'
        unique_together = ['registro_0000', 'cod_part']
    
    def __str__(self):
        doc = self.cnpj or self.cpf or 'S/N'
        return f"{self.cod_part} - {self.nome[:30]} ({doc})"
    
    @property
    def regime_tributario(self):
        """Retorna o regime tributário baseado nos dados consultados"""
        if self.optante_mei is True:
            return 'MEI'
        elif self.optante_simples is True:
            return 'Simples Nacional'
        elif self.cnpj:
            return 'Regime Normal'
        else:
            return 'Pessoa Física' if self.cpf else 'Não Identificado'
    
    @property
    def is_contribuinte(self):
        """Verifica se é contribuinte de ICMS"""
        if self.ie and self.ie.upper() not in ['ISENTO', 'ISENTA', '']:
            return True
        return False


class RegistroC170(models.Model):
    """Itens do Documento (Código 01, 1B, 04 e 55)"""
    registro_c100 = models.ForeignKey(RegistroC100, on_delete=models.CASCADE, related_name='itens')
    num_item = models.CharField('Número do Item', max_length=3)
    cod_item = models.CharField('Código do Item', max_length=60)
    descr_compl = models.TextField('Descrição Complementar', blank=True)
    qtd = models.DecimalField('Quantidade', max_digits=15, decimal_places=5, default=0)
    unid = models.CharField('Unidade', max_length=6, blank=True)
    vl_item = models.DecimalField('Valor do Item', max_digits=15, decimal_places=2, default=0)
    vl_desc = models.DecimalField('Valor do Desconto', max_digits=15, decimal_places=2, default=0)
    cst_icms = models.CharField('CST ICMS', max_length=3, blank=True)
    cfop = models.CharField('CFOP', max_length=4, blank=True)
    cod_nat = models.CharField('Código Natureza', max_length=10, blank=True)
    vl_bc_icms = models.DecimalField('Base ICMS', max_digits=15, decimal_places=2, default=0)
    aliq_icms = models.DecimalField('Alíquota ICMS', max_digits=6, decimal_places=2, default=0)
    vl_icms = models.DecimalField('Valor ICMS', max_digits=15, decimal_places=2, default=0)
    cst_pis = models.CharField('CST PIS', max_length=2, blank=True)
    vl_bc_pis = models.DecimalField('Base PIS', max_digits=15, decimal_places=2, default=0)
    aliq_pis = models.DecimalField('Alíquota PIS', max_digits=8, decimal_places=4, default=0)
    vl_pis = models.DecimalField('Valor PIS', max_digits=15, decimal_places=2, default=0)
    cst_cofins = models.CharField('CST COFINS', max_length=2, blank=True)
    vl_bc_cofins = models.DecimalField('Base COFINS', max_digits=15, decimal_places=2, default=0)
    aliq_cofins = models.DecimalField('Alíquota COFINS', max_digits=8, decimal_places=4, default=0)
    vl_cofins = models.DecimalField('Valor COFINS', max_digits=15, decimal_places=2, default=0)
    cod_ncm = models.CharField('NCM', max_length=8, blank=True)
    
    class Meta:
        verbose_name = 'Item C170'
        verbose_name_plural = 'Itens C170'
    
    def __str__(self):
        return f"Item {self.num_item} - {self.cod_item}"
