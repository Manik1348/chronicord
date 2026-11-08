@echo off
cd /d "%~dp0"
python -m venv .venv || goto :err
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt pyinstaller || goto :err
pyinstaller --noconfirm --clean --onefile --windowed --name Chronicord ^
  --icon assets\icon.ico --add-data "assets;assets" main.py || goto :err
echo.
echo Готово: dist\Chronicord.exe
certutil -hashfile dist\Chronicord.exe SHA256
pause
exit /b 0
:err
echo Ошибка сборки.
pause
exit /b 1
