from django.db import models
from apps.empresa.models import Empresa


class ProdutoSaidaAPI(models.Model):
    """Produtos de saída buscados via API MeuDanfe"""
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='produtos_saida_api')
    periodo_inicial = models.CharField('Período Inicial', max_length=7)  # YYYY-MM
    periodo_final = models.CharField('Período Final', max_length=7)  # YYYY-MM
    chave_nfe = models.CharField('Chave NF-e', max_length=44)
    
    # Dados do produto
    codigo = models.CharField('Código', max_length=60)
    descricao = models.TextField('Descrição')
    ncm = models.CharField('NCM', max_length=8, blank=True)
    cfop = models.CharField('CFOP', max_length=4, blank=True)
    unidade = models.CharField('Unidade', max_length=6, blank=True)
    quantidade = models.DecimalField('Quantidade', max_digits=15, decimal_places=5, default=0)
    valor_unitario = models.DecimalField('Valor Unitário', max_digits=15, decimal_places=4, default=0)
    valor_total = models.DecimalField('Valor Total', max_digits=15, decimal_places=2, default=0)
    
    # Impostos
    icms_cst = models.CharField('CST ICMS', max_length=3, blank=True)
    icms_aliq = models.DecimalField('Alíquota ICMS', max_digits=6, decimal_places=2, default=0)
    icms_valor = models.DecimalField('Valor ICMS', max_digits=15, decimal_places=2, default=0)
    icms_st_valor = models.DecimalField('Valor ICMS ST', max_digits=15, decimal_places=2, default=0)
    ipi_cst = models.CharField('CST IPI', max_length=2, blank=True)
    ipi_aliq = models.DecimalField('Alíquota IPI', max_digits=6, decimal_places=2, default=0)
    ipi_valor = models.DecimalField('Valor IPI', max_digits=15, decimal_places=2, default=0)
    pis_cst = models.CharField('CST PIS', max_length=2, blank=True)
    pis_aliq = models.DecimalField('Alíquota PIS', max_digits=8, decimal_places=4, default=0)
    pis_valor = models.DecimalField('Valor PIS', max_digits=15, decimal_places=2, default=0)
    cofins_cst = models.CharField('CST COFINS', max_length=2, blank=True)
    cofins_aliq = models.DecimalField('Alíquota COFINS', max_digits=8, decimal_places=4, default=0)
    cofins_valor = models.DecimalField('Valor COFINS', max_digits=15, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Produto Saída API'
        verbose_name_plural = 'Produtos Saída API'
        indexes = [
            models.Index(fields=['empresa', 'periodo_inicial', 'periodo_final']),
            models.Index(fields=['chave_nfe']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.descricao[:30]}"


class ProdutoEntradaAPI(models.Model):
    """Produtos de entrada buscados via API MeuDanfe (docs sem C170)"""
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='produtos_entrada_api')
    periodo_inicial = models.CharField('Período Inicial', max_length=7)
    periodo_final = models.CharField('Período Final', max_length=7)
    chave_nfe = models.CharField('Chave NF-e', max_length=44)

    # Dados do produto
    codigo = models.CharField('Código', max_length=60)
    descricao = models.TextField('Descrição')
    ncm = models.CharField('NCM', max_length=8, blank=True)
    cfop = models.CharField('CFOP', max_length=4, blank=True)
    unidade = models.CharField('Unidade', max_length=6, blank=True)
    quantidade = models.DecimalField('Quantidade', max_digits=15, decimal_places=5, default=0)
    valor_unitario = models.DecimalField('Valor Unitário', max_digits=15, decimal_places=4, default=0)
    valor_total = models.DecimalField('Valor Total', max_digits=15, decimal_places=2, default=0)

    # Impostos
    icms_cst = models.CharField('CST ICMS', max_length=3, blank=True)
    icms_aliq = models.DecimalField('Alíquota ICMS', max_digits=6, decimal_places=2, default=0)
    icms_valor = models.DecimalField('Valor ICMS', max_digits=15, decimal_places=2, default=0)
    icms_st_valor = models.DecimalField('Valor ICMS ST', max_digits=15, decimal_places=2, default=0)
    ipi_cst = models.CharField('CST IPI', max_length=2, blank=True)
    ipi_aliq = models.DecimalField('Alíquota IPI', max_digits=6, decimal_places=2, default=0)
    ipi_valor = models.DecimalField('Valor IPI', max_digits=15, decimal_places=2, default=0)
    pis_cst = models.CharField('CST PIS', max_length=2, blank=True)
    pis_aliq = models.DecimalField('Alíquota PIS', max_digits=8, decimal_places=4, default=0)
    pis_valor = models.DecimalField('Valor PIS', max_digits=15, decimal_places=2, default=0)
    cofins_cst = models.CharField('CST COFINS', max_length=2, blank=True)
    cofins_aliq = models.DecimalField('Alíquota COFINS', max_digits=8, decimal_places=4, default=0)
    cofins_valor = models.DecimalField('Valor COFINS', max_digits=15, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Produto Entrada API'
        verbose_name_plural = 'Produtos Entrada API'
        indexes = [
            models.Index(fields=['empresa', 'periodo_inicial', 'periodo_final']),
            models.Index(fields=['chave_nfe']),
        ]

    def __str__(self):
        return f"{self.codigo} - {self.descricao[:30]}"


class AjusteManualICMS(models.Model):
    """Ajustes manuais de apuração ICMS importados via planilha"""
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='ajustes_manuais_icms')
    periodo_inicial = models.CharField('Período Inicial', max_length=7)
    periodo_final = models.CharField('Período Final', max_length=7)
    codigo = models.CharField('Código de Ajuste', max_length=20)
    descricao = models.CharField('Tipo de Ajuste', max_length=200)
    valor = models.DecimalField('Valor do Ajuste', max_digits=15, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Ajuste Manual ICMS'
        verbose_name_plural = 'Ajustes Manuais ICMS'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - R$ {self.valor}"