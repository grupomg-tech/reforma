# 🏗️ Estrutura do Projeto Reforma/Eagle

Este documento apresenta a estrutura completa do projeto Django **Reforma/Eagle** - um sistema de gestão fiscal e tributária.

## 📁 Árvore do Projeto

```
reforma/
│
├── 📄 manage.py                         # Script de gerenciamento Django
├── 📄 requirements.txt                  # Dependências do projeto
├── 📄 .env.example                      # Exemplo de variáveis de ambiente
├── 📄 .gitignore                        # Arquivos ignorados pelo Git
├── 📄 README.md                         # Documentação do projeto
├── 📄 iniciar_servidor.py               # Script para iniciar servidor + ngrok
├── 📄 iniciar_servidor.bat              # Script Windows para iniciar servidor
├── 📄 iniciar_servidor.sh               # Script Linux/Mac para iniciar servidor
│
├── 📁 config/                           # Configurações principais do Django
│   ├── 📄 __init__.py
│   ├── 📄 settings.py                   # Configurações gerais
│   ├── 📄 settings_local.py             # Configurações locais (não versionado)
│   ├── 📄 urls.py                       # URLs principais
│   ├── 📄 wsgi.py                       # WSGI config
│   ├── 📄 asgi.py                       # ASGI config
│   └── 📄 celery.py                     # Configuração do Celery (tarefas)
│
├── 📁 apps/                             # Aplicações Django
│   │
│   ├── 📁 accounts/                     # App de Autenticação e Usuários
│   │   ├── 📄 __init__.py
│   │   ├── 📄 admin.py
│   │   ├── 📄 apps.py
│   │   ├── 📄 forms.py
│   │   ├── 📄 models.py                 # User, Profile, Grupo
│   │   ├── 📄 urls.py
│   │   ├── 📄 views.py
│   │   ├── 📁 templates/accounts/
│   │   │   ├── 📄 login.html
│   │   │   ├── 📄 logout.html
│   │   │   ├── 📄 profile.html
│   │   │   ├── 📄 usuarios.html
│   │   │   └── 📄 perfis.html
│   │   └── 📁 migrations/
│   │
│   ├── 📁 dashboards/                   # App de Dashboards
│   │   ├── 📄 __init__.py
│   │   ├── 📄 admin.py
│   │   ├── 📄 apps.py
│   │   ├── 📄 models.py
│   │   ├── 📄 urls.py
│   │   ├── 📄 views.py
│   │   ├── 📁 templates/dashboards/
│   │   │   └── 📄 index.html
│   │   └── 📁 migrations/
│   │
│   ├── 📁 empresa/                      # App de Empresas
│   │   ├── 📄 __init__.py
│   │   ├── 📄 admin.py
│   │   ├── 📄 apps.py
│   │   ├── 📄 forms.py
│   │   ├── 📄 models.py                 # Empresa (CNPJ, Razão Social, UF, CNAE, etc.)
│   │   ├── 📄 urls.py
│   │   ├── 📄 views.py
│   │   ├── 📄 utils.py                  # Utilitários (consulta CNPJ, validações)
│   │   ├── 📁 templates/empresa/
│   │   │   ├── 📄 index.html
│   │   │   ├── 📄 detail.html
│   │   │   └── 📄 form.html
│   │   └── 📁 migrations/
│   │
│   ├── 📁 sped/                         # App de SPED (Importar/Exportar/Excluir)
│   │   ├── 📄 __init__.py
│   │   ├── 📄 admin.py
│   │   ├── 📄 apps.py
│   │   ├── 📄 forms.py
│   │   ├── 📄 models.py                 # RegistroSPED, Bloco0000, etc.
│   │   ├── 📄 urls.py
│   │   ├── 📄 views.py
│   │   ├── 📄 parser.py                 # Parser de arquivos SPED
│   │   ├── 📄 tasks.py                  # Tarefas Celery para processamento
│   │   ├── 📁 templates/sped/
│   │   │   ├── 📄 importar.html
│   │   │   ├── 📄 exportar.html
│   │   │   └── 📄 excluir.html
│   │   └── 📁 migrations/
│   │
│   ├── 📁 documentos_fiscais/           # App de Documentos Fiscais
│   │   ├── 📄 __init__.py
│   │   ├── 📄 admin.py
│   │   ├── 📄 apps.py
│   │   ├── 📄 forms.py
│   │   ├── 📄 models.py                 # NFe, CTe, NFSe, MDFe
│   │   ├── 📄 urls.py
│   │   ├── 📄 views.py
│   │   ├── 📄 api_views.py              # Views da API
│   │   ├── 📄 serializers.py            # Serializers DRF
│   │   ├── 📁 templates/documentos_fiscais/
│   │   │   ├── 📄 index.html
│   │   │   ├── 📄 nfe_list.html
│   │   │   ├── 📄 cte_list.html
│   │   │   ├── 📄 nfse_list.html
│   │   │   └── 📄 mdfe_list.html
│   │   └── 📁 migrations/
│   │
│   ├── 📁 reforma_tributaria/           # App da Reforma Tributária
│   │   ├── 📄 __init__.py
│   │   ├── 📄 admin.py
│   │   ├── 📄 apps.py
│   │   ├── 📄 forms.py
│   │   ├── 📄 models.py                 # ConsultaGTIN, Aliquota, Anexo
│   │   ├── 📄 urls.py
│   │   ├── 📄 views.py
│   │   ├── 📄 api_views.py              # API para consulta GTIN
│   │   ├── 📄 sefaz_client.py           # Cliente para API SEFAZ
│   │   ├── 📁 templates/reforma_tributaria/
│   │   │   ├── 📄 index.html
│   │   │   ├── 📄 consulta_gtin.html
│   │   │   └── 📄 consulta.html
│   │   └── 📁 migrations/
│   │
│   ├── 📁 xml_manager/                  # App de Gerenciamento de XMLs
│   │   ├── 📄 __init__.py
│   │   ├── 📄 admin.py
│   │   ├── 📄 apps.py
│   │   ├── 📄 forms.py
│   │   ├── 📄 models.py
│   │   ├── 📄 urls.py
│   │   ├── 📄 views.py
│   │   ├── 📄 parser.py                 # Parser de XMLs fiscais
│   │   ├── 📁 templates/xml_manager/
│   │   │   └── 📄 importar.html
│   │   └── 📁 migrations/
│   │
│   └── 📁 utilitarios/                  # App de Utilitários
│       ├── 📄 __init__.py
│       ├── 📄 admin.py
│       ├── 📄 apps.py
│       ├── 📄 models.py                 # Log de Atividades
│       ├── 📄 urls.py
│       ├── 📄 views.py
│       ├── 📁 templates/utilitarios/
│       │   └── 📄 logs.html
│       └── 📁 migrations/
│
├── 📁 static/                           # Arquivos Estáticos
│   ├── 📁 css/
│   │   ├── 📄 base.css
│   │   ├── 📄 sidebar.css
│   │   └── 📄 forms.css
│   ├── 📁 js/
│   │   ├── 📄 base.js
│   │   ├── 📄 sidebar.js
│   │   ├── 📄 utils.js
│   │   └── 📄 toasts.js
│   └── 📁 images/
│       ├── 📄 favicon.ico
│       ├── 📄 logo.png
│       └── 📄 logo_completa.png
│
├── 📁 templates/                        # Templates Globais
│   ├── 📄 base.html                     # Template base com sidebar
│   ├── 📄 base_auth.html                # Template para páginas de auth
│   ├── 📁 includes/
│   │   ├── 📄 sidebar.html
│   │   ├── 📄 header.html
│   │   ├── 📄 footer.html
│   │   ├── 📄 messages.html
│   │   └── 📄 pagination.html
│   └── 📁 errors/
│       ├── 📄 404.html
│       └── 📄 500.html
│
├── 📁 media/                            # Uploads de usuários
│   ├── 📁 certificados/                 # Certificados digitais
│   ├── 📁 logos/                        # Logos das empresas
│   ├── 📁 sped/                         # Arquivos SPED
│   └── 📁 xmls/                         # XMLs importados
│
└── 📁 logs/                             # Logs da aplicação
    ├── 📄 django.log
    ├── 📄 celery.log
    └── 📄 sped.log
```

## 🗄️ Modelos Principais

### 📌 accounts.models
- **User** - Usuário customizado (email como username)
- **Profile** - Perfil do usuário
- **Grupo** - Grupos de permissões

### 📌 empresa.models
- **Empresa**
  - cnpj_cpf (CharField)
  - razao_social (CharField)
  - uf (ForeignKey → UF)
  - cnae_fiscal (ForeignKey → CNAE)
  - regime_tributario (CharField)
  - inscricao_estadual (CharField)
  - logo (ImageField)
  - certificado_digital (FileField)
  - senha_certificado (CharField - criptografado)
  - data_validade_certificado (DateField)
  - status_certificado (CharField)

### 📌 sped.models
- **Registro0000** - Abertura do arquivo SPED
- **RegistroFiscal** - Registros do SPED Fiscal
- **RegistroContribuicoes** - Registros do SPED Contribuições
- **ProcessamentoSPED** - Status de processamentos

### 📌 documentos_fiscais.models
- **DocumentoFiscal** (Abstract)
- **NFe** - Nota Fiscal Eletrônica
- **CTe** - Conhecimento de Transporte
- **NFSe** - Nota Fiscal de Serviço
- **MDFe** - Manifesto de Documentos Fiscais

### 📌 reforma_tributaria.models
- **ConsultaGTIN** - Histórico de consultas GTIN
- **Aliquota** - Alíquotas CBS/IBS
- **AnexoRT** - Anexos da Reforma Tributária

## 🌐 URLs Principais

| URL | App | View |
|-----|-----|------|
| `/` | dashboards | index |
| `/dashboards/` | dashboards | index |
| `/accounts/login/` | accounts | login |
| `/accounts/logout/` | accounts | logout |
| `/accounts/` | accounts | usuarios |
| `/empresa/` | empresa | list/create |
| `/empresa/<id>/` | empresa | detail |
| `/importar-sped/` | sped | importar |
| `/exportar-sped/` | sped | exportar |
| `/excluir-sped/` | sped | excluir |
| `/importar-xmls/` | xml_manager | importar |
| `/api/documentos-fiscais/` | documentos_fiscais | api |
| `/api/documentos/exportar/` | documentos_fiscais | exportar |
| `/reforma-tributaria/` | reforma_tributaria | index |
| `/reforma-tributaria/consulta-gtin/` | reforma_tributaria | consulta_gtin |
| `/reforma-tributaria/api/processar-xml/` | reforma_tributaria | api_processar |
| `/utilitarios/` | utilitarios | logs |
| `/xml/lote/` | xml_manager | lote |

## 🛠️ Tecnologias Utilizadas

- **Backend:** Django 5.x
- **Frontend:** Bootstrap 5.3.3, Bootstrap Icons, Font Awesome 6.5
- **Banco de Dados:** PostgreSQL (produção) / SQLite (desenvolvimento)
- **Task Queue:** Celery + Redis
- **Servidor:** Nginx + Gunicorn
- **Túnel:** ngrok (desenvolvimento)

## 📦 Dependências Principais

```txt
Django>=5.0
djangorestframework
celery
redis
psycopg2-binary
python-decouple
gunicorn
whitenoise
Pillow
openpyxl
lxml
requests
cryptography
pyngrok
```

## 🚀 Execução

Para iniciar o servidor local com ngrok:

```bash
# Windows
iniciar_servidor.bat

# Linux/Mac
./iniciar_servidor.sh

# Ou diretamente com Python
python iniciar_servidor.py
```

---
*Sistema Eagle - Gestão Fiscal e Tributária v1.0.0*
