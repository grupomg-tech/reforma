"""
Models do app Accounts - Usuários e Autenticação
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Modelo de usuário customizado"""
    email = models.EmailField('E-mail', unique=True)
    telefone = models.CharField('Telefone', max_length=20, blank=True)
    avatar = models.ImageField('Avatar', upload_to='avatars/', blank=True, null=True)
    
    # Usa email como username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['first_name', 'last_name']
    
    def __str__(self):
        return self.get_full_name() or self.email
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class Profile(models.Model):
    """Perfil estendido do usuário"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    cargo = models.CharField('Cargo', max_length=100, blank=True)
    departamento = models.CharField('Departamento', max_length=100, blank=True)
    empresas = models.ManyToManyField('empresa.Empresa', blank=True, related_name='usuarios')
    
    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'
    
    def __str__(self):
        return f"Perfil de {self.user}"
