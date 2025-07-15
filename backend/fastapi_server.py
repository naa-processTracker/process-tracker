import win32gui
import win32process
import psutil
import sqlite3
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler

DB_PATH = "apps.db"

# ========== DB & 추적 함수 ==========
def enum_window_callback(hwnd, windows):
    if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        title = win32gui.GetWindowText(hwnd)
        windows.append((pid, title))

def get_visible_windows():
    windows = []
    win32gui.EnumWindows(enum_window_callback, windows)
    return windows

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS app_usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pid INTEGER,
        name TEXT,
        title TEXT,
        started_at TEXT,
        last_seen_at TEXT,
        count INTEGER
    )
    ''')
    conn.commit()
    conn.close()

def upsert_app(pid, name, title):
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "SELECT id, count FROM app_usage WHERE pid=? AND title=?",
            (pid, title)
        )
        row = cur.fetchone()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if row:
            cur.execute(
                "UPDATE app_usage SET count = count + 1, last_seen_at=? WHERE id=?",
                (now, row[0])
            )
            print(f"[UPDATE] {now} - {name} ({title}), count +1")
        else:
            cur.execute(
                "INSERT INTO app_usage (pid, name, title, started_at, last_seen_at, count) VALUES (?, ?, ?, ?, ?, 1)",
                (pid, name, title, now, now)
            )
            print(f"[INSERT] {now} - {name} ({title})")
        conn.commit()
    except Exception as e:
        print(f"[ERROR] upsert_app: {name} ({title}), {e}")
    finally:
        conn.close()

def scan_and_update():
    windows = get_visible_windows()
    seen_pid = set()
    for pid, title in windows:
        if pid in seen_pid:
            continue
        seen_pid.add(pid)
        try:
            proc = psutil.Process(pid)
            name = proc.name()
            upsert_app(pid, name, title)
        except Exception:
            pass

def select_top(n=10):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT name, title, count FROM app_usage ORDER BY count DESC LIMIT ?",
        (n,)
    )
    rows = cur.fetchall()
    conn.close()
    return [{"name": r[0], "title": r[1], "count": r[2]} for r in rows]

# ========== FastAPI 서버 ==========
app = FastAPI()

# CORS 허용 (React/Electron에서 fetch 가능하도록)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # 실제 배포 시엔 꼭 제한하기!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/top-apps")
def get_top_apps(n: int = 10):
    return select_top(n)

# ========== APScheduler ==========
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(scan_and_update, 'interval', seconds=10)
    scheduler.start()

# ========== Main ==========
if __name__ == "__main__":
    init_db()
    start_scheduler()
    import uvicorn
    print("서버 시작: http://localhost:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)