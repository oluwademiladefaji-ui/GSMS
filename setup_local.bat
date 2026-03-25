@echo off
echo.
echo ======================================================
echo           GSMS - Initial Setup (Local)
echo ======================================================
echo.

:: 1. Create venv if not exist
if not exist venv (
    echo [1/4] Creating virtual environment...
    python -m venv venv
) else (
    echo [1/4] Virtual environment already exists.
)

:: 2. Activate and Install
echo [2/4] Installing dependencies...
call venv\Scripts\activate
pip install -r requirements.txt --quiet

:: 3. Migrate database (SQLite)
echo [3/4] Running migrations...
python manage.py migrate

:: 4. Create BUAdmin if needed
echo [4/4] Ensuring admin exists...
python manage.py shell -c "from accounts.models import User; User.objects.create_superuser('BUAdmin', 'admin@bu.edu', 'Admin') if not User.objects.filter(username='BUAdmin').exists() else print('Admin account ready.')"

echo.
echo ======================================================
echo   Setup Complete! You can now run the app.
echo ======================================================
echo.
pause
