from django.urls import path
from . import views

app_name = 'reforma_tributaria'

urlpatterns = [
    path('', views.index, name='index'),
    path('consulta-gtin/', views.consulta_gtin, name='consulta_gtin'),
    path('consulta/', views.consulta, name='consulta'),
    path('api/processar-xml/', views.api_processar_xml, name='api_processar_xml'),
]
