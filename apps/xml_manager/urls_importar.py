from django.urls import path
from . import views

app_name = 'xml_importar'

urlpatterns = [
    path('', views.importar_xmls, name='importar'),
]
