const { app, BrowserWindow, Menu, protocol, net } = require('electron');
const path = require('path');

// GPU Acceleration Flags for WebGL / Three.js
app.commandLine.appendSwitch('ignore-gpu-blocklist');
app.commandLine.appendSwitch('enable-gpu-rasterization');
app.commandLine.appendSwitch('enable-zero-copy');
if (process.platform === 'darwin') {
  app.commandLine.appendSwitch('use-angle', 'metal');
  app.commandLine.appendSwitch('enable-features', 'CanvasOopRasterization,Metal');
}

// Register custom protocol for local files (solves CORS issues for GLTF models)
protocol.registerSchemesAsPrivileged([
  { scheme: 'app', privileges: { secure: true, standard: true, supportFetchAPI: true, bypassCSP: true, corsEnabled: true } }
]);

function createWindow() {
  const win = new BrowserWindow({
    width: 1440,
    height: 900,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      backgroundThrottling: false // Keep game loop running when window is in background
    }
  });

  // Minimal Custom Menu
  const menuTemplate = [
    {
      label: 'Aegis Flora',
      submenu: [
        { role: 'about' },
        { type: 'separator' },
        { role: 'services' },
        { type: 'separator' },
        { role: 'hide' },
        { role: 'hideOthers' },
        { role: 'unhide' },
        { type: 'separator' },
        { role: 'quit' }
      ]
    },
    {
      label: 'Edit',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
        { role: 'paste' }
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'toggleDevTools' }
      ]
    },
    {
      label: 'Window',
      submenu: [
        { role: 'minimize' },
        { role: 'zoom' },
        { 
          label: 'Toggle Fullscreen',
          accelerator: 'F11',
          click: () => {
            win.setFullScreen(!win.isFullScreen());
          }
        },
        { role: 'close' }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(menuTemplate);
  Menu.setApplicationMenu(menu);

  // Load the game using our custom app:// protocol to resolve paths cleanly
  win.loadURL('app://localhost/game.html');
}

app.whenReady().then(() => {
  // Protocol handler serves files from the game root.
  // In dev: __dirname is /towers/desktop, so '../' → /towers/
  // In packaged: extraResources land in process.resourcesPath
  protocol.handle('app', (request) => {
    const parsedUrl = new URL(request.url);
    const decodedPath = decodeURIComponent(parsedUrl.pathname);
    const basePath = app.isPackaged
      ? process.resourcesPath
      : path.join(__dirname, '..');
    const filePath = path.join(basePath, decodedPath);
    return net.fetch('file://' + filePath);
  });

  if (process.platform === 'darwin') {
    app.dock.setName('Aegis Flora');
  }

  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
