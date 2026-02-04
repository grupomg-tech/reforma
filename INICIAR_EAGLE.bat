@echo off
chcp 65001 >nul
title Eagle - Sistema de Gestão Fiscal + ngrok

echo.
echo ╔═══════════════════════════════════════════════════════════════════╗
echo ║   ███████╗ █████╗  ██████╗ ██╗     ███████╗                      ║
echo ║   ██╔════╝██╔══██╗██╔════╝ ██║     ██╔════╝                      ║
echo ║   █████╗  ███████║██║  ███╗██║     █████╗                        ║
echo ║   ██╔══╝  ██╔══██║██║   ██║██║     ██╔══╝                        ║
echo ║   ███████╗██║  ██║╚██████╔╝███████╗███████╗                      ║
echo ║   ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚══════╝                      ║
echo ║                                                                   ║
echo ║           Sistema de Gestão Fiscal e Tributária                  ║
echo ║                       Versão 1.0.0                                ║
echo ╚═══════════════════════════════════════════════════════════════════╝
echo.

REM === CONFIGURAÇÕES ===
set PORTA=8000
set NGROK_TOKEN=

REM === VERIFICA PYTHON ===
echo [INFO] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado! Instale em https://python.org
    pause
    exit /b 1
)
echo [OK] Python encontrado!

REM === ATIVA AMBIENTE VIRTUAL SE EXISTIR ===
if exist "venv\Scripts\activate.bat" (
    echo [INFO] Ativando ambiente virtual...
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Ativando ambiente virtual...
    call .venv\Scripts\activate.bat
)

REM === VERIFICA/INSTALA DEPENDENCIAS ===
echo [INFO] Verificando dependencias...
pip show django >nul 2>&1
if errorlevel 1 (
    echo [INFO] Instalando Django...
    pip install django >nul 2>&1
)

pip show pyngrok >nul 2>&1
if errorlevel 1 (
    echo [INFO] Instalando pyngrok...
    pip install pyngrok >nul 2>&1
)

REM === EXECUTA MIGRACOES ===
echo [INFO] Executando migracoes do banco de dados...
python manage.py migrate --run-syncdb >nul 2>&1

REM === INICIA NGROK EM SEGUNDO PLANO ===
echo.
echo ════════════════════════════════════════════════════════════════
echo    INICIANDO NGROK...
echo ════════════════════════════════════════════════════════════════
echo.

REM Mata processos ngrok anteriores
taskkill /F /IM ngrok.exe >nul 2>&1

REM Inicia ngrok em uma nova janela
start "ngrok" cmd /c "python -c "from pyngrok import ngrok; t = ngrok.connect(%PORTA%, 'http'); print(''); print('═' * 60); print('   URL EXTERNA: ' + t.public_url); print('   URL LOCAL:   http://localhost:%PORTA%'); print('═' * 60); print(''); print('   Mantenha esta janela aberta!'); print('   Pressione Ctrl+C para encerrar o ngrok'); input()"" 

REM Aguarda ngrok iniciar
timeout /t 3 /nobreak >nul

REM === INICIA SERVIDOR DJANGO ===
echo.
echo ════════════════════════════════════════════════════════════════
echo    INICIANDO SERVIDOR DJANGO NA PORTA %PORTA%...
echo ════════════════════════════════════════════════════════════════
echo.
echo    Acesso Local: http://localhost:%PORTA%
echo    A URL externa do ngrok aparece na outra janela!
echo.
echo    Pressione Ctrl+C para encerrar o servidor
echo.
echo ════════════════════════════════════════════════════════════════
echo.

python manage.py runserver 0.0.0.0:%PORTA%

REM === CLEANUP AO SAIR ===
echo.
echo [INFO] Encerrando ngrok...
taskkill /F /IM ngrok.exe >nul 2>&1
echo [INFO] Servidor encerrado!
pause
