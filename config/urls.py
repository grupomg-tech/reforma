"""
URL configuration for Reforma/Eagle project.

Sistema de Gestão Fiscal e Tributária
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Redirect root to dashboards
    path('', RedirectView.as_view(url='/dashboards/', permanent=False), name='home'),
    
    # Apps
    path('accounts/', include('apps.accounts.urls')),
    path('dashboards/', include('apps.dashboards.urls')),
    path('empresa/', include('apps.empresa.urls')),
    
    # SPED
    path('importar-sped/', include('apps.sped.urls_importar')),
    path('exportar-sped/', include('apps.sped.urls_exportar')),
    path('excluir-sped/', include('apps.sped.urls_excluir')),
    
    # Documentos Fiscais
    path('api/documentos-fiscais/', include('apps.documentos_fiscais.urls_api')),
    path('api/documentos/', include('apps.documentos_fiscais.urls')),
    
    # Reforma Tributária
    path('reforma-tributaria/', include('apps.reforma_tributaria.urls')),
    
    # XML Manager
    path('importar-xmls/', include('apps.xml_manager.urls_importar')),
    path('xml/', include('apps.xml_manager.urls')),
    
    # Utilitários
    path('utilitarios/', include('apps.utilitarios.urls')),
]

# Serve arquivos de mídia em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin site customization
admin.site.site_header = 'Eagle - Administração'
admin.site.site_title = 'Eagle Admin'
admin.site.index_title = 'Painel de Administração'
