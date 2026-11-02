import html
import os
import socket
import sys
import threading
import time
import webview

LOADING_HTML = """<!DOCTYPE html>
<html>
<head>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: #1a1a2e;
    display: flex; align-items: center; justify-content: center;
    height: 100vh; font-family: 'Segoe UI', sans-serif;
  }
  .container { text-align: center; color: #c8a84b; }
  h1 { font-size: 2.2rem; margin-bottom: 0.5rem; letter-spacing: 2px; }
  p { color: #888; font-size: 0.95rem; margin-top: 1.2rem; }
  .dots span {
    display: inline-block; width: 10px; height: 10px; margin: 0 4px;
    background: #c8a84b; border-radius: 50%;
    animation: bounce 1.4s infinite ease-in-out both;
  }
  .dots span:nth-child(2) { animation-delay: 0.2s; }
  .dots span:nth-child(3) { animation-delay: 0.4s; }
  @keyframes bounce {
    0%, 80%, 100% { transform: scale(0); opacity: 0.3; }
    40% { transform: scale(1); opacity: 1; }
  }
</style>
</head>
<body>
  <div class="container">
    <h1>&#9876; TOW Arbiter</h1>
    <div class="dots"><span></span><span></span><span></span></div>
    <p>Loading AI model and knowledge base...</p>
  </div>
</body>
</html>"""


def _create_api_socket() -> socket.socket:
    """Reserve an available loopback port for this app's API."""
    api_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        api_socket.bind(("127.0.0.1", 0))
        api_socket.listen()
        api_socket.setblocking(False)
    except OSError:
        api_socket.close()
        raise
    return api_socket


def _show_initialization_error(window, message: str) -> None:
    safe_message = html.escape(message)
    window.load_html(
        "<!DOCTYPE html><html><body style='background:#1a1a2e;color:#c8a84b;"
        "font-family:Segoe UI,sans-serif;padding:3rem'>"
        "<h1>TOW Arbiter could not start</h1>"
        f"<p style='color:#ddd'>{safe_message}</p></body></html>"
    )


def _apply_window_icon() -> None:
    """Set the title bar icon to match the exe icon (Windows only)."""
    if sys.platform != 'win32':
        return
    import ctypes
    import ctypes.wintypes as wintypes

    hwnd = ctypes.windll.user32.FindWindowW(None, "TOW Arbiter")
    if not hwnd:
        return

    WM_SETICON = 0x0080
    ICON_SMALL = 0
    ICON_BIG = 1

    h_large = wintypes.HICON()
    h_small = wintypes.HICON()

    if getattr(sys, 'frozen', False):
        src = sys.executable
    else:
        src = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           'frontend', 'public', 'app_icon.ico')

    if not os.path.exists(src):
        return

    count = ctypes.windll.shell32.ExtractIconExW(
        src, 0, ctypes.byref(h_large), ctypes.byref(h_small), 1
    )
    if count > 0:
        if h_large.value:
            ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, h_large.value)
        if h_small.value:
            ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, h_small.value)

# Run the API server in a separate thread.
def _run_api(api_socket: socket.socket) -> None:
    import uvicorn
    from api import app as fastapi_app
    port = api_socket.getsockname()[1]
    config = uvicorn.Config(app=fastapi_app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)
    server.run(sockets=[api_socket])

# Wait for the API to be ready and then navigate the webview window to the app URL.
def _wait_and_navigate(window, app_url: str) -> None:
    import requests
    while True:
        try:
            # Check if the API server is ready by querying the /status endpoint.
            r = requests.get(f"{app_url}/status", timeout=2)
            if r.ok:
                status = r.json()
                if status.get("ready"):
                    window.load_url(app_url)
                    return
                message = status.get("message", "")
                if message.startswith("error:"):
                    _show_initialization_error(window, message)
                    return
        except Exception:
            pass
        time.sleep(1)


def main() -> None:
    api_socket = _create_api_socket()
    app_url = f"http://127.0.0.1:{api_socket.getsockname()[1]}"
    window = webview.create_window(
        "TOW Arbiter",
        html=LOADING_HTML,
        width=700,
        height=750,
        text_select=True,
    )

    threading.Thread(target=_run_api, args=(api_socket,), daemon=True).start()
    threading.Thread(target=_wait_and_navigate, args=(window, app_url), daemon=True).start()

    webview.start(func=_apply_window_icon)


if __name__ == '__main__':
    main()
