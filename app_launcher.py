"""Launch the FastAPI application and embeds it inside a native desktop window using pywebview.

It starts the FastAPI server in a background thread, waits until the
server is available, and then creates a window that loads the web
interface. This allows the application to run as a standalone desktop
program without requiring a browser.

Author: Juan Esteban Bedoya <jebedoyal@udistrital.edu.co>

This file is part of ComputerScience2 project.

ComputerScience2 is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

ComputerScience2 is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with ComputerScience2. If not, see <https://www.gnu.org/licenses/>.
"""

import threading
import time

import requests
import uvicorn
import webview

from main import app


def start_api():
	"""Run the FastAPI server in a background thread.

	The server is started using Uvicorn on host 127.0.0.1 and port 8000.
	"""
	uvicorn.run(app, host='127.0.0.1', port=8000, reload=False)


def wait_for_server(url: str, timeout: int = 10) -> bool:
	"""Wait until the FastAPI server becomes available.

	It repeatedly sends HTTP requests to the specified URL until
	the server responds with a 200 status code or the timeout is reached.

	Args:
	    url (str): The server URL to check.
	    timeout (int, optional): Maximum waiting time in seconds.
	        Defaults to 10.

	Returns:
	    bool: True if the server is available, False otherwise.

	"""
	for _ in range(timeout * 10):
		try:
			r = requests.get(url, timeout=2)
			if r.status_code == 200:
				return True
		except requests.exceptions.ConnectionError:
			time.sleep(0.1)
	return False


if __name__ == '__main__':
	threading.Thread(target=start_api, daemon=True).start()

	if wait_for_server('http://127.0.0.1:8000'):
		webview.create_window('Ciencias de la Computacion II', 'http://127.0.0.1:8000')
		webview.start()
	else:
		print('Error: FastAPI server did not start in time.')
