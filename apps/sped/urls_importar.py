from django.urls import path
from . import views

app_name = 'sped_importar'

urlpatterns = [
    path('', views.importar_sped, name='importar'),
    path('consultar-participantes/<int:registro_id>/', views.consultar_participantes, name='consultar_participantes'),
    path('status-participantes/<int:registro_id>/', views.status_participantes, name='status_participantes'),
]
