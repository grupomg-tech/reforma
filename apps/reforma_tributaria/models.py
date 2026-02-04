from django.db import models

class ConsultaGTIN(models.Model):
    gtin = models.CharField(max_length=14)
    ncm = models.CharField(max_length=8)
    descricao = models.TextField()
    retorno_sefaz = models.TextField(blank=True)
    consultado_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Consulta GTIN'
        verbose_name_plural = 'Consultas GTIN'
