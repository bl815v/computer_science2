
import threading
import uvicorn
import webview
import time
import requests
from main import app

def start_api():
    """Run FastAPI server in background thread"""
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)

def wait_for_server(url, timeout=10):
    """Wait until the FastAPI server is available."""
    for _ in range(timeout * 10):
        try:
            r = requests.get(url)
            if r.status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            time.sleep(0.1)
    return False

if __name__ == "__main__":
    threading.Thread(target=start_api, daemon=True).start()

    if wait_for_server("http://127.0.0.1:8000"):
        webview.create_window("Mi App", "http://127.0.0.1:8000")
        webview.start()
    else:
        print("Error: FastAPI server did not start in time.")
