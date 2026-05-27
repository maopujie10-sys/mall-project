// Friday AI OS - Electron Desktop
const { app, BrowserWindow, Tray, Menu, nativeImage, globalShortcut, ipcMain } = require("electron");
const path = require("path");

let mainWindow;
let tray;

function createWindow() {
  try {
    mainWindow = new BrowserWindow({
      width: 1400,
      height: 900,
      minWidth: 1024,
      minHeight: 680,
      frame: false,
      backgroundColor: "#0a0d1a",
      webPreferences: {
        preload: path.join(__dirname, "preload.cjs"),
        nodeIntegration: false,
        contextIsolation: true,
        webgl: true,
      },
      icon: path.join(__dirname, "../public/icons/icon-512.png"),
      show: false,
    });

    const isDev = process.env.NODE_ENV !== "production";
    if (isDev) {
      mainWindow.loadURL("http://localhost:5173/ai/");
    } else {
      mainWindow.loadFile(path.join(__dirname, "../dist/index.html"));
    }

    mainWindow.once("ready-to-show", () => {
      mainWindow.show();
      mainWindow.focus();
    });

    ipcMain.on("window-minimize", () => mainWindow.minimize());
    ipcMain.on("window-maximize", () => {
      mainWindow.isMaximized() ? mainWindow.unmaximize() : mainWindow.maximize();
    });
    ipcMain.on("window-close", () => mainWindow.close());
    ipcMain.on("window-toggle-fullscreen", () => {
      mainWindow.setFullScreen(!mainWindow.isFullScreen());
    });
  } catch (e) {
    console.error("createWindow failed:", e);
  }
}

function createTray() {
  try {
    const icon = nativeImage.createFromDataURL(
      "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAAbwAAAG8B8aLcQwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAEESURBVDiNpZMxTsNAEEX/rNeOg4SCEgmJA3AEbkDFCbgBFQ2noOEESFyAgoKSK0TkAIkLUNDgxLsdFswajJUI8aXRavbPzH87I+Sc+R8pAK8A1keIMcYqxpgXAFcAZpM8L4DjGGO1aZrXG4DPA3AmIg/A50cA5pxfRORFRE5mAiKCUko9TQL4cRwviK2IyLlt2z8BpJRmAL6S1tf1foD3GM2ciNwCeGma5usXoGlp27bvMVl6nudNTQCXIlIBeJim6dc4wK7rHmOMtwB20zT9mNF7AHsAZc759K8Xw4cxxqsY4wuAXc/z2l8AN8De3dI0LYdhGK4A7ABorxGRX4+OETkyxrgbY9wC8ApgPUVEFgGc1nYfxbsYmmMMAAAAAElFTkSuQmCC"
    );
    tray = new Tray(icon.resize(16, 16));
    const contextMenu = Menu.buildFromTemplate([
      { label: "打开 Friday AI", click: () => { mainWindow.show(); mainWindow.focus(); } },
      { type: "separator" },
      { label: "AI 状态", enabled: false },
      { label: "  大脑在线 ?", enabled: false },
      { type: "separator" },
      { label: "退出", click: () => { app.quit(); } },
    ]);
    tray.setToolTip("Friday AI OS - 运行中");
    tray.setContextMenu(contextMenu);
    tray.on("double-click", () => { mainWindow.show(); mainWindow.focus(); });
  } catch (e) {
    console.error("createTray failed:", e);
  }
}

app.whenReady().then(() => {
  createWindow();
  createTray();
  globalShortcut.register("CommandOrControl+Shift+F", () => {
    if (mainWindow) { mainWindow.show(); mainWindow.focus(); }
  });
});

app.on("window-all-closed", () => { /* 托盘保持运行 */ });
app.on("activate", () => { if (!mainWindow) createWindow(); });
app.on("before-quit", () => { globalShortcut.unregisterAll(); });