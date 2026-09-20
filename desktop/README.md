# Aegis Flora - Desktop Release Packaging (Windows & macOS)

This directory contains the desktop application packaging setup for **Aegis Flora**, powered by Electron and `electron-builder`.

Aegis Flora ships with a **Windows-first Steam release architecture** while maintaining parity for macOS.

---

## Prerequisites

- **Node.js**: v18.0.0 or higher (v20+ LTS recommended)
- **Windows**: Windows 10/11 x64, PowerShell 7+ or Command Prompt. (For building Windows binaries from source or in CI)
- **macOS**: macOS 12+ (for building DMG with Xcode command line tools and `iconutil`)

---

## Getting Started

1. Navigate to the `desktop` directory:
   ```bash
   cd desktop
   ```

2. Install runtime and build dependencies:
   ```bash
   npm install
   ```

3. Launch the game locally in desktop development mode:
   ```bash
   npm start
   ```

---

## Build Targets

The packaging pipeline produces distribution-ready binaries for both platforms:

### 1. Windows (Primary Steam Target)
```bash
npm run build:win
```
Produces:
- **`AegisFlora-Setup-1.0.0.exe`**: Standalone NSIS installer with desktop shortcut and uninstaller.
- **`AegisFlora-1.0.0-win.zip`**: Unpacked portable binary directory ready for direct integration into the **SteamPipe Content Builder** depot (`ContentBuilder/content/`).

### 2. macOS
```bash
npm run build:mac
```
Produces:
- **`Aegis Flora-1.0.0.dmg`**: Drag-and-drop macOS disk image with Applications link and code signing hooks.

### 3. Dual-Platform Build (Cross-platform)
```bash
npm run build:all
```

---

## Steamworks Integration Plan & Paths

### Steam Depot Structure
For deployment via the Steamworks Partner portal:
1. Run `npm run build:win` (or `npm run pack`).
2. Point your Steam depot script (`depot_<depot_id>.vdf`) to the generated portable folder in `dist/win-unpacked/`:
   ```
   "DepotPath" "."
   "LocalPath" "path/to/desktop/dist/win-unpacked/*"
   "Recursive" "1"
   ```
3. Set the launch executable in Steamworks App Config to `AegisFlora.exe`.

### Save Path & Steam Cloud Sync Configuration
Aegis Flora persists player state (unlocked Verdant Glyphs, audio/clarity preferences, high scores, wave records) via browser `localStorage` isolated within the Electron application data directory.

- **Windows Location**:
  `%APPDATA%\Aegis Flora\Local Storage\leveldb\`
- **macOS Location**:
  `~/Library/Application Support/Aegis Flora/Local Storage/leveldb/`
- **Steam Cloud Auto-Cloud Configuration**:
  - Root: `WinAppDataRoaming`
  - Subdirectory: `Aegis Flora`
  - Pattern: `*`
  - OS: `Windows` (and mapped for `MacOS`)

### Steam Input & Gamepad Support
- Electron command-line flags include `--enable-gamepad-button-axis-events` to ensure standard Chromium Gamepad API access.
- Works natively with Xbox 360/One/Series XInput, DualShock 4/DualSense, and Steam Deck controllers.
- Recommended Steam Input community layout: **Standard Gamepad with High-Precision Stick Mouse**.

---

## Crash Reporting & Diagnostic Telemetry

Aegis Flora initializes Electron's `crashReporter` at application startup:
- Local crash dumps are automatically recorded in:
  - Windows: `%APPDATA%\Aegis Flora\Crashpad\reports`
  - macOS: `~/Library/Application Support/Aegis Flora/Crashpad/reports`
- To route crash dumps to an enterprise crash reporting service (e.g. Backtrace / Sentry), configure `submitURL` and toggle `uploadToServer: true` in `desktop/main.js`.

---

## Creating Application Icons

- **Windows (`build/icon.ico`)**:
  Place a multi-resolution `.ico` (containing 16x16, 32x32, 48x48, 64x64, 128x128, 256x256 layers) at `desktop/build/icon.ico`.
- **macOS (`build/icon.icns`)**:
  Convert a 1024x1024 PNG icon using the included script:
  ```bash
  chmod +x scripts/create-icns.sh
  ./scripts/create-icns.sh path/to/icon.png build/icon.icns
  ```

---

## CI/CD Pipeline

Automated dual-platform builds are triggered on every commit to `main` via GitHub Actions (`.github/workflows/build-desktop.yml`). The workflow compiles and uploads artifacts for both `Aegis-Flora-Windows-x64` and `Aegis-Flora-macOS-DMG`.
