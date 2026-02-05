from django.urls import path
from . import views

app_name = 'dashboards'

urlpatterns = [
    path('', views.index, name='index'),
    path('relatorio-fiscal/', views.relatorio_fiscal, name='relatorio_fiscal'),
    path('api/periodos/', views.api_periodos, name='api_periodos'),
    path('api/buscar-xml-produto/', views.api_buscar_xml_produto, name='api_buscar_xml_produto'),
    path('api/listar-chaves-saida/', views.api_listar_chaves_saida, name='api_listar_chaves_saida'),
]
