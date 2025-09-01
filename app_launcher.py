
import threading
import uvicorn
import webview

def start_api():
    """Run FastAPI server in background thread"""
    uvicorn.run("main:app", host="127.0.0.1", port=8000)

if __name__ == "__main__":
    threading.Thread(target=start_api, daemon=True).start()

    webview.create_window("Mi App", "http://127.0.0.1:8000")
    webview.start()
