from django.db import models
from apps.empresa.models import Empresa

class DocumentoFiscal(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    chave_acesso = models.CharField(max_length=44, unique=True)
    numero = models.IntegerField()
    serie = models.CharField(max_length=5)
    data_emissao = models.DateField()
    valor_total = models.DecimalField(max_digits=15, decimal_places=2)
    xml_conteudo = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        abstract = True

class NFe(DocumentoFiscal):
    modelo = models.CharField(max_length=2, default='55')
    
    class Meta:
        verbose_name = 'NF-e'
        verbose_name_plural = 'NF-es'

class CTe(DocumentoFiscal):
    modelo = models.CharField(max_length=2, default='57')
    
    class Meta:
        verbose_name = 'CT-e'
        verbose_name_plural = 'CT-es'
