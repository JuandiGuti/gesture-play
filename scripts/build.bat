@echo off
cd /d "%~dp0.."

:: --- Build script para entorno de trabajo de gesture-play ---

:: Comprobamos si Python está disponible
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Python no está instalado o no está en el PATH.
    echo Por favor instálalo desde:
    echo https://www.python.org/downloads/windows/
    echo.
    start https://www.python.org/downloads/windows/
    pause
    exit /b
)

:: Verificamos que sea Python 3.10
set "FOUND="
for /f "tokens=*" %%A in ('py -0') do (
    echo %%A | findstr /C:"3.10" >nul
    if not errorlevel 1 (
        set "FOUND=1"
    )
)

if not defined FOUND (
    echo.
    echo [ERROR] Se requiere tener instalada alguna versión de Python 3.10
    echo Descárgala desde:
    echo https://www.python.org/downloads/release/python-3100/
    echo.
    start https://www.python.org/downloads/release/python-3100/
    pause
    exit /b
)

:: Crear entorno virtual para backend si no existe
if not exist backend\venv (
    echo [INFO] Creando entorno virtual para BACKEND...
    py -3.10 -m venv backend\venv
    call backend\venv\Scripts\activate && pip install -r backend\requirements.txt && call deactivate
) else (
    echo [INFO] Entorno virtual de BACKEND ya existe.
)

:: Crear entorno virtual para frontend si no existe
if not exist frontend\venv (
    echo [INFO] Creando entorno virtual para FRONTEND...
    py -3.10 -m venv frontend\venv
    call frontend\venv\Scripts\activate && pip install -r frontend\requirements.txt && call deactivate
) else (
    echo [INFO] Entorno virtual de FRONTEND ya existe.
)

:: Mensaje final
echo.
echo [SUCCESS] Entorno preparado correctamente (Python 3.10 verificado).
pause
