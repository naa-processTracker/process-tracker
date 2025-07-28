# process-tracker

A simple desktop app that tracks and ranks the applications you use the most on Windows.

- Tracks currently visible windows every 10 seconds
- Stores usage data locally (sqlite)
- Electron frontend + FastAPI backend (packaged as exe)
- Shows a live ranking of the most used apps (by active window time)
- All processing happens on your PC (no data leaves your device)

## Features

- 10-second interval tracking of active application windows
- SQLite-based local storage
- FastAPI backend, Electron-based frontend UI
- Auto-packaged as a standalone Windows app (no installation needed)
- Displays most-used applications (ranked by active time)

## How it works

1. **FastAPI backend** scans open windows every 10 seconds and records usage.
2. **Electron frontend** fetches and displays the latest app usage ranking.
3. Both backend and frontend are bundled together.  
   Simply run `process-tracker.exe` – the server starts automatically.

## Development

- Backend: Python (FastAPI, APScheduler, psutil, pywin32, sqlite3)
- Frontend: Electron, HTML/JS (or React)

## Build & Packaging

- **Electron app is packaged via `electron-packager`**
- **FastAPI backend is bundled as an EXE using `pyinstaller`**

> _Note: The `/process-tracker-win32-x64/` build output and other generated files are not committed to Git (`.gitignore`)._

## License

MIT
