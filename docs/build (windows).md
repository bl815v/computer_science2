# Build and Run (Windows)
how to run the application locally and how to generate a Windows executable (.exe).

## Prerequisites
- Windows 10 or later  
- Python 3.14+  
- [uv](https://docs.astral.sh/uv/getting-started/installation/#__tabbed_1_2) installed
- Project dependencies installed (`uv sync`)  
- PyInstaller installed  
- Visual C++ Build Tools (required on Windows)

## 1. Create Virtual Environment

```bash
uv venv
```

## 2. Activate Environment
```bash
.\.venv\Scripts\activate
```

## 3. Install Dependencies
```bash
uv pip install -r requirements.txt
```

## 4. Run Development Server
```bash
uvicorn main:app --reload
```

## Build .exe File

```bash
python -m PyInstaller --noconfirm --onefile --icon=icon.ico --noconsole --name app_launcher --add-data "static;static" app_launcher.py
```