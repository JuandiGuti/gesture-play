@echo off
:: Ir al directorio del backend
cd /d "%~dp0..\backend"

:: Activar entorno virtual local
call venv\Scripts\activate

:: Ejecutar la app
python app.py

:: Esperar para ver mensajes
pause
