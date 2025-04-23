@echo off
set nginx_path=C:\Users\mbj_r\Documents\Python\nginx
set nginx_exe=%nginx_path%\nginx.exe
set project_path=C:\Users\mbj_r\Documents\Python\inventory_25

echo Verificando ruta de Nginx...
if not exist "%nginx_exe%" (
    echo Error: No se encuentra nginx.exe en %nginx_path%
    pause
    exit /b 1
)

echo Cerrando procesos anteriores de Nginx (si existen)...
taskkill /f /im nginx.exe >nul 2>&1

REM echo Validando configuración de Nginx...
cd /d "%nginx_path%"
REM nginx.exe -t
REM if errorlevel 1 (
REM     echo La configuración de Nginx no es válida.
REM     pause
REM     exit /b 1
REM )

echo Iniciando Nginx...
start "" "%nginx_exe%"
echo Nginx deberia estar en ejecucion. Verifica con tasklist. 

echo Verificando ruta de Nginx...
if not exist "%nginx_exe%" (
    echo Error: No se encuentra nginx.exe en %nginx_path%
    pause
    exit /b 1
)

echo Iniciando waitress
cd /d "%project_path%"
"%project_path%\venv\Scripts\waitress-serve" --listen=0.0.0.0:5000 main:app

pause