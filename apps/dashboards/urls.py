from django.urls import path
from . import views

app_name = 'dashboards'

urlpatterns = [
    path('', views.index, name='index'),
    path('relatorio-fiscal/', views.relatorio_fiscal, name='relatorio_fiscal'),
    path('api/periodos/', views.api_periodos, name='api_periodos'),
    path('api/buscar-xml-produto/', views.api_buscar_xml_produto, name='api_buscar_xml_produto'),
    path('api/listar-chaves-saida/', views.api_listar_chaves_saida, name='api_listar_chaves_saida'),
    path('api/chaves-processadas/', views.api_chaves_processadas, name='api_chaves_processadas'),
    path('api/exportar-relatorio-erros/', views.api_exportar_relatorio_erros, name='api_exportar_relatorio_erros'),
    path('api/salvar-produtos-api/', views.api_salvar_produtos_api, name='api_salvar_produtos_api'),
]
