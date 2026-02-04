from django.urls import path
from . import views

app_name = 'empresa'

urlpatterns = [
    path('', views.empresa_list, name='list'),
    path('<int:pk>/', views.empresa_detail, name='detail'),
    path('export/excel/', views.export_excel, name='export_excel'),
]
