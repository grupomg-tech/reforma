from django.urls import path
from . import views

app_name = 'dashboards'

urlpatterns = [
    path('', views.index, name='index'),
    path('relatorio-fiscal/', views.relatorio_fiscal, name='relatorio_fiscal'),
    path('api/periodos/', views.api_periodos, name='api_periodos'),
]
