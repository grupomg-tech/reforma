from django.db import models
from apps.empresa.models import Empresa


class ConsultaGTIN(models.Model):
    gtin = models.CharField(max_length=14)
    ncm = models.CharField(max_length=8)
    descricao = models.TextField()
    retorno_sefaz = models.TextField(blank=True)
    consultado_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Consulta GTIN'
        verbose_name_plural = 'Consultas GTIN'


class ItemNCM(models.Model):
    """Itens com NCM e classificação tributária extraídos do SPED"""
    ORIGEM_CHOICES = [
        ('SPED', 'SPED Fiscal/Contribuições'),
        ('XML', 'XML de NF-e'),
        ('MANUAL', 'Cadastro Manual'),
    ]
    
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='itens_ncm')
    cod_item = models.CharField('Código do Item', max_length=60)
    descricao = models.TextField('Descrição')
    cod_ncm = models.CharField('NCM', max_length=8)
    cest = models.CharField('CEST', max_length=7, blank=True)
    cod_barra = models.CharField('Código de Barras', max_length=14, blank=True)
    unidade = models.CharField('Unidade', max_length=6, blank=True)
    
    # Classificação Tributária
    cst_icms = models.CharField('CST ICMS', max_length=3, blank=True)
    cst_pis = models.CharField('CST PIS', max_length=2, blank=True)
    cst_cofins = models.CharField('CST COFINS', max_length=2, blank=True)
    cfop = models.CharField('CFOP', max_length=4, blank=True)
    
    # Alíquotas
    aliq_icms = models.DecimalField('Alíquota ICMS', max_digits=6, decimal_places=2, default=0)
    aliq_pis = models.DecimalField('Alíquota PIS', max_digits=8, decimal_places=4, default=0)
    aliq_cofins = models.DecimalField('Alíquota COFINS', max_digits=8, decimal_places=4, default=0)
    
    # Reforma Tributária (campos futuros)
    cbs_aliquota = models.DecimalField('CBS Alíquota', max_digits=6, decimal_places=2, null=True, blank=True)
    ibs_aliquota = models.DecimalField('IBS Alíquota', max_digits=6, decimal_places=2, null=True, blank=True)
    
    # Metadados
    origem = models.CharField('Origem', max_length=10, choices=ORIGEM_CHOICES, default='SPED')
    registro_0000 = models.ForeignKey(
        'sped.Registro0000', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='itens_ncm'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Item NCM'
        verbose_name_plural = 'Itens NCM'
        unique_together = ['empresa', 'cod_item']
        ordering = ['cod_ncm', 'cod_item']
    
    def __str__(self):
        return f"{self.cod_ncm} - {self.cod_item} - {self.descricao[:30]}"
