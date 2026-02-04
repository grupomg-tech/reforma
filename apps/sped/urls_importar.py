from django.urls import path
from . import views

app_name = 'sped_importar'

urlpatterns = [
    path('', views.importar_sped, name='importar'),
]
