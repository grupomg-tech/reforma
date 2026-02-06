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
    path('api/listar-chaves-entrada-sem-itens/', views.api_listar_chaves_entrada_sem_itens, name='api_listar_chaves_entrada_sem_itens'),
    path('api/salvar-produtos-entrada-api/', views.api_salvar_produtos_entrada_api, name='api_salvar_produtos_entrada_api'),
    path('api/chaves-entrada-processadas/', views.api_chaves_entrada_processadas, name='api_chaves_entrada_processadas'),
    path('api/importar-ajustes-manuais-icms/', views.api_importar_ajustes_manuais_icms, name='api_importar_ajustes_manuais_icms'),
    path('api/excluir-ajustes-manuais-icms/', views.api_excluir_ajustes_manuais_icms, name='api_excluir_ajustes_manuais_icms'),
    path('api/excluir-ajuste-manual-icms/<int:ajuste_id>/', views.api_excluir_ajuste_manual_icms, name='api_excluir_ajuste_manual_icms'),
]
