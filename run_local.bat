@echo off
echo.
echo ======================================================
echo           GSMS - Starting Local Server
echo ======================================================
echo.

:: Activate and Run
call venv\Scripts\activate
echo [GSMS] Server starting at: http://127.0.0.1:8000
python manage.py runserver

pause
