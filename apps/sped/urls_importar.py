from django.urls import path
from . import views

app_name = 'sped_importar'

urlpatterns = [
    path('', views.importar_sped, name='importar'),
    path('consultar-participantes/<int:registro_id>/', views.consultar_participantes, name='consultar_participantes'),
    path('status-participantes/<int:registro_id>/', views.status_participantes, name='status_participantes'),
    path('listar-participantes-pendentes/<int:registro_id>/', views.listar_participantes_pendentes, name='listar_participantes_pendentes'),
    path('listar-participantes-consultados/<int:registro_id>/', views.listar_participantes_consultados, name='listar_participantes_consultados'),
    path('consultar-participante-individual/<int:registro_id>/<int:participante_id>/', views.consultar_participante_individual, name='consultar_participante_individual'),
]
