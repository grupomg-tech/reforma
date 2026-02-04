from django.db import models

class UF(models.Model):
    codigo = models.IntegerField(primary_key=True)
    sigla = models.CharField(max_length=2)
    nome = models.CharField(max_length=50)
    
    class Meta:
        verbose_name = 'UF'
        verbose_name_plural = 'UFs'
        ordering = ['sigla']
    
    def __str__(self):
        return self.sigla

class CNAE(models.Model):
    codigo = models.CharField(max_length=10, primary_key=True)
    descricao = models.TextField()
    
    class Meta:
        verbose_name = 'CNAE'
        verbose_name_plural = 'CNAEs'
    
    def __str__(self):
        return f"{self.codigo} - {self.descricao[:50]}"

class Empresa(models.Model):
    REGIME_CHOICES = [
        ('1', 'Simples Nacional'),
        ('2', 'Simples Nacional - Excesso'),
        ('3', 'Regime Normal'),
    ]
    
    cnpj_cpf = models.CharField('CNPJ/CPF', max_length=18, unique=True)
    razao_social = models.CharField('Razão Social', max_length=200)
    uf = models.ForeignKey(UF, on_delete=models.PROTECT, verbose_name='UF')
    cnae_fiscal = models.ForeignKey(CNAE, on_delete=models.SET_NULL, null=True, blank=True)
    regime_tributario = models.CharField(max_length=1, choices=REGIME_CHOICES, blank=True)
    inscricao_estadual = models.CharField('IE', max_length=20, blank=True)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    certificado_digital = models.FileField(upload_to='certificados/', blank=True, null=True)
    senha_certificado = models.CharField(max_length=100, blank=True)
    data_validade_certificado = models.DateField(blank=True, null=True)
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['razao_social']
    
    def __str__(self):
        return f"{self.cnpj_cpf} - {self.razao_social}"
