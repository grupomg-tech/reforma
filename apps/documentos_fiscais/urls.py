from django.urls import path
from . import views

app_name = 'documentos'

urlpatterns = [
    path('exportar/', views.exportar, name='exportar'),
]
