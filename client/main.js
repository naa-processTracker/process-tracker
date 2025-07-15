const { app, BrowserWindow } = require("electron");
const { spawn } = require("child_process");
const path = require("path");

let pyProc = null;

function createWindow() {
  const win = new BrowserWindow({
    width: 900,
    height: 700,
    webPreferences: {
      // preload 등 필요시 추가
    },
  });
  win.loadFile("index.html"); // or React/Vite 빌드된 경로
}

function startPythonServer() {
  // fastapi_server.exe가 frontend 폴더 하위에 있다고 가정
  const exePath = path.join(__dirname, "fastapi_server.exe");
  pyProc = spawn(exePath, [], {
    cwd: __dirname,
    detached: true,
    stdio: "ignore",
  });
}

app.whenReady().then(() => {
  startPythonServer();
  // 서버가 완전히 켜질 때까지 살짝 딜레이 추천(2~3초)
  setTimeout(createWindow, 5000);
});

app.on("will-quit", () => {
  if (pyProc) pyProc.kill();
});
