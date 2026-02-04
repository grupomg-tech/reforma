@echo off
chcp 65001 >nul
title Eagle + ngrok

echo.
echo ========================================
echo    EAGLE - Sistema de Gestao Fiscal
echo    Iniciando Django + ngrok...
echo ========================================
echo.

REM Configuracao da porta
set PORTA=8000

REM Ativa venv se existir
if exist "venv\Scripts\activate.bat" call venv\Scripts\activate.bat
if exist ".venv\Scripts\activate.bat" call .venv\Scripts\activate.bat

REM Verifica dependencias
pip show pyngrok >nul 2>&1 || pip install pyngrok
pip show django >nul 2>&1 || pip install django python-decouple whitenoise

REM Migracoes
python manage.py migrate --run-syncdb >nul 2>&1

REM Inicia ngrok em nova janela
start "NGROK - URL Externa" cmd /k "python -m pyngrok.ngrok http %PORTA%"

REM Aguarda 3 segundos
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo    SERVIDOR DJANGO INICIADO!
echo ========================================
echo    Local: http://localhost:%PORTA%
echo    Ngrok: Veja a URL na outra janela
echo ========================================
echo    Ctrl+C para parar
echo.

REM Inicia Django
python manage.py runserver 0.0.0.0:%PORTA%

pause
