const { app, BrowserWindow, Menu, protocol, net, crashReporter } = require('electron');
const path = require('path');
const fs = require('fs');

// Setup Crash Reporting for production diagnostics
crashReporter.start({
  productName: 'Aegis Florae',
  companyName: 'murderszn',
  submitURL: 'https://submit.backtrace.io/murderszn/aegis-florae/crashpad',
  uploadToServer: false, // Keep crash dumps stored locally in userData/Crashpad by default
  compress: true
});

// GPU Acceleration & Gamepad Flags for WebGL / Three.js
app.commandLine.appendSwitch('ignore-gpu-blocklist');
app.commandLine.appendSwitch('enable-gpu-rasterization');
app.commandLine.appendSwitch('enable-zero-copy');
app.commandLine.appendSwitch('enable-gamepad-button-axis-events');
app.commandLine.appendSwitch('autoplay-policy', 'no-user-gesture-required');

if (process.platform === 'darwin') {
  app.commandLine.appendSwitch('use-angle', 'metal');
  app.commandLine.appendSwitch('enable-features', 'CanvasOopRasterization,Metal');
} else if (process.platform === 'win32') {
  // Windows DirectX 11 / D3D11 ANGLE backend for optimal desktop GPU performance
  app.commandLine.appendSwitch('use-angle', 'd3d11');
  app.commandLine.appendSwitch('enable-features', 'CanvasOopRasterization');
}

// Register custom protocol for local files (solves CORS issues for GLTF models)
protocol.registerSchemesAsPrivileged([
  { scheme: 'app', privileges: { secure: true, standard: true, supportFetchAPI: true, bypassCSP: true, corsEnabled: true } }
]);

function createWindow() {
  const iconPath = process.platform === 'win32'
    ? path.join(__dirname, 'build', 'icon.ico')
    : path.join(__dirname, 'build', 'icon.icns');

  const win = new BrowserWindow({
    width: 1440,
    height: 900,
    minWidth: 1024,
    minHeight: 600,
    title: 'Aegis Florae',
    icon: fs.existsSync(iconPath) ? iconPath : undefined,
    autoHideMenuBar: process.platform === 'win32',
    backgroundColor: '#0a0f0d',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      backgroundThrottling: false // Keep game loop running when window is in background
    }
  });

  // Minimal Custom Menu
  const menuTemplate = [
    {
      label: 'Aegis Florae',
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
    let decodedPath;
    try {
      decodedPath = decodeURIComponent(parsedUrl.pathname);
    } catch {
      return new Response('Bad request', { status: 400 });
    }
    const basePath = app.isPackaged
      ? process.resourcesPath
      : path.join(__dirname, '..');
    const filePath = path.normalize(path.join(basePath, decodedPath));
    // Block path traversal (e.g. app://localhost/../../etc/passwd): the
    // resolved path must stay inside the game root/resources directory.
    if (filePath !== basePath && !filePath.startsWith(basePath + path.sep)) {
      return new Response('Forbidden', { status: 403 });
    }
    return net.fetch('file://' + filePath);
  });

  if (process.platform === 'darwin' && typeof app.setName === 'function') {
    app.setName('Aegis Florae');
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
