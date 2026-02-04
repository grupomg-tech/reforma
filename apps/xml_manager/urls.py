from django.urls import path
from . import views

app_name = 'xml_manager'

urlpatterns = [
    path('lote/', views.lote, name='lote'),
]
