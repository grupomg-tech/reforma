@echo off
REM =====================================================
REM   INICIADOR DO SERVIDOR - REFORMA/EAGLE (Windows)
REM =====================================================
REM   Execute este arquivo para iniciar o servidor
REM   Django com túnel ngrok
REM =====================================================

title Eagle - Servidor de Desenvolvimento

echo.
echo ========================================
echo   EAGLE - Sistema de Gestao Fiscal
echo   Iniciando servidor...
echo ========================================
echo.

REM Verifica se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo Instale Python 3.10+ em https://python.org
    pause
    exit /b 1
)

REM Ativa ambiente virtual se existir
if exist "venv\Scripts\activate.bat" (
    echo [INFO] Ativando ambiente virtual...
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Ativando ambiente virtual...
    call .venv\Scripts\activate.bat
) else (
    echo [AVISO] Ambiente virtual nao encontrado.
    echo [DICA] Crie um com: python -m venv venv
)

REM Instala dependências se necessário
echo.
echo [INFO] Verificando dependencias...
pip show django >nul 2>&1
if errorlevel 1 (
    echo [INFO] Instalando dependencias...
    pip install -r requirements.txt
)

REM Inicia o servidor
echo.
echo [INFO] Iniciando servidor com ngrok...
echo.
python iniciar_servidor.py

pause
