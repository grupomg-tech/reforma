from django.urls import path
from . import views

app_name = 'api_documentos'

urlpatterns = [
    path('', views.api_documentos, name='list'),
]
