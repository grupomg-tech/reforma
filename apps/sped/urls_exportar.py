from django.urls import path
from . import views

app_name = 'sped_exportar'

urlpatterns = [
    path('', views.exportar_sped, name='exportar'),
]
