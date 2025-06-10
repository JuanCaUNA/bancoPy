@echo off
REM Script para iniciar la Interfaz Gráfica del Sistema Bancario SINPE
REM Asegúrese de tener Python instalado y las dependencias

echo ====================================
echo   Sistema Bancario SINPE - GUI
echo ====================================
echo.

REM Verificar si Python 3.12 está instalado
py -3.12 --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.12 no está instalado o no está en el PATH
    echo Instale Python 3.12 desde https://python.org
    pause
    exit /b 1
)

echo Python 3.12 detectado correctamente
echo.

REM Verificar dependencias
echo Verificando dependencias...
py -3.12 -m pip list | findstr Flask >nul 2>&1
if errorlevel 1 (
    echo Instalando dependencias...
    py -3.12 -m pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: No se pudieron instalar las dependencias
        pause
        exit /b 1
    )
)

echo Dependencias OK
echo.

REM Iniciar la interfaz gráfica
echo Iniciando Interfaz Gráfica...
echo.
py -3.12 run_gui.py

if errorlevel 1 (
    echo.
    echo ERROR: La aplicación terminó con errores
    pause
)

echo.
echo Gracias por usar el Sistema Bancario SINPE
pause
