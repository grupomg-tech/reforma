"""Views do app Accounts"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def usuarios_list(request):
    """Lista de usuários"""
    return render(request, 'accounts/usuarios.html')


@login_required
def perfis_list(request):
    """Lista de perfis"""
    return render(request, 'accounts/perfis.html')


@login_required
def profile(request):
    """Perfil do usuário logado"""
    return render(request, 'accounts/profile.html')
