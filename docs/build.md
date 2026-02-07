# Build and Run
how to run the application locally and how to generate a Windows executable (.exe).

## Prerequisites
- Python 3.11.9  
- [uv](https://docs.astral.sh/uv/getting-started/installation/#__tabbed_1_2) installed
- PyInstaller installed  

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
uv sync
```

## 4. Run Development Server
```bash
uvicorn main:app --reload
```

## 5. Build .exe File
Run:
```bash
python -m PyInstaller --noconfirm --onefile --icon=icon.ico --noconsole --name app_launcher --add-data "static;static" app_launcher.py
```