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
for /f "tokens=2 delims= " %%A in ('python --version') do set PY_VER=%%A
set VER_OK=%PY_VER:~0,4%
if not "%VER_OK%" == "3.10" (
    echo.
    echo [ERROR] Se requiere Python 3.10. Descárgalo desde:
    echo https://www.python.org/downloads/release/python-3100/
    echo.
    start https://www.python.org/downloads/release/python-3100/
    pause
    exit /b
)

:: Crear entorno virtual para backend si no existe
if not exist backend\venv (
    echo [INFO] Creando entorno virtual para BACKEND...
    python -m venv backend\venv
    call backend\venv\Scripts\activate && pip install -r backend\requirements.txt && call deactivate
) else (
    echo [INFO] Entorno virtual de BACKEND ya existe.
)

:: Crear entorno virtual para frontend si no existe
if not exist frontend\venv (
    echo [INFO] Creando entorno virtual para FRONTEND...
    python -m venv frontend\venv
    call frontend\venv\Scripts\activate && pip install -r frontend\requirements.txt && call deactivate
) else (
    echo [INFO] Entorno virtual de FRONTEND ya existe.
)

:: Mensaje final
echo.
echo [SUCCESS] Entorno preparado correctamente (Python 3.10 verificado).
pause
