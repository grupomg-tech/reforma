#!/usr/bin/env python
"""
╔═══════════════════════════════════════════════════════════════════╗
║           🚀 INICIADOR DO SERVIDOR - REFORMA/EAGLE 🚀             ║
║═══════════════════════════════════════════════════════════════════║
║  Este script inicia o servidor Django e cria um túnel ngrok       ║
║  para acesso externo (útil para testes e desenvolvimento)         ║
╚═══════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import time
import subprocess
import threading
import signal
from pathlib import Path

# Adiciona o diretório do projeto ao path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))


class Colors:
    """Cores para output no terminal"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_banner():
    """Exibe o banner inicial"""
    banner = f"""
{Colors.CYAN}╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   ███████╗ █████╗  ██████╗ ██╗     ███████╗                      ║
║   ██╔════╝██╔══██╗██╔════╝ ██║     ██╔════╝                      ║
║   █████╗  ███████║██║  ███╗██║     █████╗                        ║
║   ██╔══╝  ██╔══██║██║   ██║██║     ██╔══╝                        ║
║   ███████╗██║  ██║╚██████╔╝███████╗███████╗                      ║
║   ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚══════╝                      ║
║                                                                   ║
║           🦅 Sistema de Gestão Fiscal e Tributária               ║
║                       Versão 1.0.0                                ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝{Colors.END}
"""
    print(banner)


def check_requirements():
    """Verifica se as dependências estão instaladas"""
    print(f"{Colors.YELLOW}📦 Verificando dependências...{Colors.END}")
    
    required = ['django', 'pyngrok']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"{Colors.RED}❌ Pacotes faltando: {', '.join(missing)}{Colors.END}")
        print(f"{Colors.YELLOW}💡 Execute: pip install -r requirements.txt{Colors.END}")
        return False
    
    print(f"{Colors.GREEN}✅ Todas as dependências estão instaladas!{Colors.END}")
    return True


def setup_environment():
    """Configura variáveis de ambiente"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    # Carrega .env se existir
    env_file = BASE_DIR / '.env'
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            print(f"{Colors.GREEN}✅ Arquivo .env carregado{Colors.END}")
        except ImportError:
            print(f"{Colors.YELLOW}⚠️  python-dotenv não instalado, pulando .env{Colors.END}")


def run_migrations():
    """Executa as migrações do banco de dados"""
    print(f"\n{Colors.YELLOW}🗄️  Executando migrações...{Colors.END}")
    try:
        import django
        django.setup()
        from django.core.management import call_command
        call_command('migrate', verbosity=0)
        print(f"{Colors.GREEN}✅ Migrações aplicadas com sucesso!{Colors.END}")
        return True
    except Exception as e:
        print(f"{Colors.YELLOW}⚠️  Aviso nas migrações: {e}{Colors.END}")
        return True  # Continua mesmo com aviso


def collect_static():
    """Coleta arquivos estáticos"""
    print(f"\n{Colors.YELLOW}📁 Coletando arquivos estáticos...{Colors.END}")
    try:
        from django.core.management import call_command
        call_command('collectstatic', verbosity=0, interactive=False)
        print(f"{Colors.GREEN}✅ Arquivos estáticos coletados!{Colors.END}")
    except Exception as e:
        print(f"{Colors.YELLOW}⚠️  Aviso ao coletar estáticos: {e}{Colors.END}")


def start_ngrok(port=8000):
    """Inicia o túnel ngrok"""
    print(f"\n{Colors.CYAN}🌐 Iniciando túnel ngrok...{Colors.END}")
    
    try:
        from pyngrok import ngrok, conf
        
        # Configuração do ngrok
        ngrok_config = conf.get_default()
        
        # Verifica se há token de autenticação
        ngrok_token = os.environ.get('NGROK_AUTH_TOKEN')
        if ngrok_token:
            ngrok.set_auth_token(ngrok_token)
            print(f"{Colors.GREEN}✅ Token ngrok configurado{Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠️  Executando ngrok sem token (limite de sessões){Colors.END}")
            print(f"{Colors.YELLOW}   Para configurar: export NGROK_AUTH_TOKEN=seu_token{Colors.END}")
        
        # Inicia o túnel
        tunnel = ngrok.connect(port, "http")
        public_url = tunnel.public_url
        
        print(f"\n{Colors.GREEN}{'═' * 60}{Colors.END}")
        print(f"{Colors.GREEN}   🎉 TÚNEL NGROK ATIVO!{Colors.END}")
        print(f"{Colors.GREEN}{'═' * 60}{Colors.END}")
        print(f"{Colors.BOLD}   🌍 URL Externa: {Colors.CYAN}{public_url}{Colors.END}")
        print(f"{Colors.BOLD}   🏠 URL Local:   {Colors.CYAN}http://localhost:{port}{Colors.END}")
        print(f"{Colors.GREEN}{'═' * 60}{Colors.END}\n")
        
        return public_url
        
    except Exception as e:
        print(f"{Colors.RED}❌ Erro ao iniciar ngrok: {e}{Colors.END}")
        print(f"{Colors.YELLOW}💡 Instale o ngrok: pip install pyngrok{Colors.END}")
        print(f"{Colors.YELLOW}💡 Ou configure: ngrok config add-authtoken SEU_TOKEN{Colors.END}")
        return None


def start_django_server(port=8000, use_runserver_plus=False):
    """Inicia o servidor Django"""
    print(f"\n{Colors.CYAN}🚀 Iniciando servidor Django na porta {port}...{Colors.END}")
    
    try:
        import django
        django.setup()
        
        # Tenta usar runserver_plus (django-extensions) se disponível
        if use_runserver_plus:
            try:
                from django_extensions.management.commands import runserver_plus
                cmd = ['python', 'manage.py', 'runserver_plus', f'0.0.0.0:{port}']
            except ImportError:
                cmd = ['python', 'manage.py', 'runserver', f'0.0.0.0:{port}']
        else:
            cmd = ['python', 'manage.py', 'runserver', f'0.0.0.0:{port}']
        
        # Inicia o servidor em um subprocesso
        process = subprocess.Popen(
            cmd,
            cwd=str(BASE_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        return process
        
    except Exception as e:
        print(f"{Colors.RED}❌ Erro ao iniciar servidor: {e}{Colors.END}")
        return None


def handle_server_output(process):
    """Lê e exibe a saída do servidor Django"""
    try:
        for line in iter(process.stdout.readline, ''):
            if line:
                # Coloriza alguns outputs
                if 'error' in line.lower() or 'exception' in line.lower():
                    print(f"{Colors.RED}{line.rstrip()}{Colors.END}")
                elif 'warning' in line.lower():
                    print(f"{Colors.YELLOW}{line.rstrip()}{Colors.END}")
                elif '"GET' in line or '"POST' in line:
                    # Requisições HTTP
                    if '200' in line:
                        print(f"{Colors.GREEN}{line.rstrip()}{Colors.END}")
                    elif '404' in line:
                        print(f"{Colors.YELLOW}{line.rstrip()}{Colors.END}")
                    elif '500' in line:
                        print(f"{Colors.RED}{line.rstrip()}{Colors.END}")
                    else:
                        print(f"{Colors.BLUE}{line.rstrip()}{Colors.END}")
                else:
                    print(line.rstrip())
    except:
        pass


def cleanup(signum=None, frame=None):
    """Limpa recursos ao encerrar"""
    print(f"\n{Colors.YELLOW}🛑 Encerrando servidor...{Colors.END}")
    
    try:
        from pyngrok import ngrok
        ngrok.kill()
        print(f"{Colors.GREEN}✅ Túnel ngrok encerrado{Colors.END}")
    except:
        pass
    
    print(f"{Colors.GREEN}👋 Até logo!{Colors.END}")
    sys.exit(0)


def main():
    """Função principal"""
    print_banner()
    
    # Configuração de sinais para cleanup
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    # Parâmetros
    PORT = int(os.environ.get('PORT', 8000))
    USE_NGROK = os.environ.get('USE_NGROK', 'true').lower() == 'true'
    
    # Verifica dependências
    if not check_requirements():
        sys.exit(1)
    
    # Configura ambiente
    setup_environment()
    
    # Executa migrações
    run_migrations()
    
    # Coleta estáticos (opcional)
    # collect_static()
    
    # Inicia ngrok (se habilitado)
    ngrok_url = None
    if USE_NGROK:
        ngrok_url = start_ngrok(PORT)
        if ngrok_url:
            # Adiciona URL às configurações do Django
            os.environ['NGROK_URL'] = ngrok_url
    
    # Inicia servidor Django
    django_process = start_django_server(PORT)
    
    if django_process:
        print(f"\n{Colors.GREEN}{'═' * 60}{Colors.END}")
        print(f"{Colors.GREEN}   ✅ SERVIDOR INICIADO COM SUCESSO!{Colors.END}")
        print(f"{Colors.GREEN}{'═' * 60}{Colors.END}")
        print(f"{Colors.BOLD}   🏠 Acesso Local:   {Colors.CYAN}http://localhost:{PORT}{Colors.END}")
        if ngrok_url:
            print(f"{Colors.BOLD}   🌍 Acesso Externo: {Colors.CYAN}{ngrok_url}{Colors.END}")
        print(f"{Colors.GREEN}{'═' * 60}{Colors.END}")
        print(f"\n{Colors.YELLOW}   Pressione Ctrl+C para encerrar{Colors.END}\n")
        
        # Monitora output do servidor
        handle_server_output(django_process)
    else:
        print(f"{Colors.RED}❌ Falha ao iniciar o servidor{Colors.END}")
        cleanup()


if __name__ == '__main__':
    main()
