@echo off
cd /d "C:\Users\bl\3D Objects\computer_science2\computer_science2"
call .\.venv\Scripts\activate
python -m PyInstaller --noconfirm --onefile --icon=icon.ico --noconsole --name app_launcher --add-data "static;static" app_launcher.py
pause
