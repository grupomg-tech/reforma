from django.urls import path
from . import views

app_name = 'sped_excluir'

urlpatterns = [
    path('', views.excluir_sped, name='excluir'),
]
