# TOW Arbiter

An AI rules assistant for Warhammer: The Old World, built with FastAPI + React.

## Quick Start: build and run the desktop app

Prerequisites: **Python 3.11 or newer** and **Node.js 20.19+** (or 22.12+) installed and on `PATH`.
These versions are required by the current frontend build tools.

In PowerShell, clone the repository, build the app, then launch it:

```powershell
git clone https://github.com/Ottowski/warhammer-ai-chatbot.git
Set-Location warhammer-ai-chatbot
.\build_desktop.ps1
& ".\TOW Arbiter\TOW Arbiter.exe"
```

The first build takes several minutes. The script creates `.venv` if needed, installs
Python and frontend dependencies, builds the frontend, and packages the executable.
It stops with an error if any step fails.

If PowerShell blocks the script, allow scripts for this session, then run the build again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\build_desktop.ps1
```

After building, launch the app from the repository root:

```powershell
& ".\TOW Arbiter\TOW Arbiter.exe"
```

The first launch can take a while while the knowledge base is indexed; the window shows
a loading screen until it is ready. Rebuild after changing the app or frontend code.

## Run from source (without building the .exe)

From the repository root in PowerShell, create a virtual environment, install the
dependencies, build the frontend, and start the API:

```powershell
Set-Location warhammer-ai-chatbot
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
npm --prefix frontend install
npm --prefix frontend run build
.\.venv\Scripts\python.exe -m uvicorn api:app --host 127.0.0.1 --port 8000
```

For source mode, open http://127.0.0.1:8000 in a browser for the web UI, or
http://127.0.0.1:8000/docs for the API documentation. FastAPI serves the built
frontend from `frontend/dist`.

## Requirements

- Python 3.11 or newer
- Node.js 20.19+ or 22.12+
- npm (included with Node.js)

The desktop build script installs the project dependencies automatically. The source
run steps above install them explicitly.

## Desktop app details

- The app opens in a native Windows window using pywebview.
- The frontend is bundled from `frontend/dist`; the backend API runs inside the app on
  `127.0.0.1:8000`. The desktop window displays the same UI served at that address, so
  the browser URL above is also available while the desktop app is running.
- Persistent vector store data is written under `%LOCALAPPDATA%\TOW-Arbiter\data\vector_store` in desktop mode.
- If the project path contains spaces, quote it in `Set-Location`. Use `&` to launch the executable from PowerShell.

## Troubleshooting

- **`TOW Arbiter.exe` closes immediately:** the build was incomplete or stale. Re-run `.\build_desktop.ps1` and check it ends with `Build finished.`
- **Port 8000 already in use:** both the desktop app and source mode use this local port.
  Close any other running instance of the app or API server, then retry.
- **Frontend build reports an unsupported Node.js version:** install Node.js 20.19+ or 22.12+, then rerun the build.
- **Running the build script from another folder:** it switches to the repository folder automatically.
