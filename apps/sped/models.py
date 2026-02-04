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
