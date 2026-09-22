# Aegis Florae - Desktop Release Packaging (Windows & macOS)

Current release: **1.1.0**. Electron + `electron-builder` wrap the static
WebGL game (`game.html`) in a native window with GPU acceleration, gamepad
support, localStorage saves, and Crashpad diagnostics.

---

## Supported platforms

| Platform | Versions | Architectures | Notes |
|---|---|---|---|
| macOS | 12 Monterey or newer | arm64 (Apple Silicon), x64 (Intel) | Separate per-arch DMGs |
| Windows | 10 version 1909+, 11 | x64 | NSIS installer + portable ZIP |
| Windows ARM64 | — | — | **Unsupported.** ARM devices must use x64 emulation; ARM64 is not a build target. |

---

## Prerequisites

- **Node.js**: v18+ (v20+ LTS recommended)
- **macOS builds**: macOS 12+ with Xcode command line tools (for `iconutil`/`sips`)
- **Windows builds**: build on Windows (`windows-latest` in CI); cross-building
  Windows targets from macOS/Linux requires Wine and is not supported here

---

## Development commands

```bash
cd desktop
npm install        # first run (creates package-lock.json; enables `npm ci`)
npm start          # launch the game in desktop development mode
npm run pack       # unpacked local build in dist/ (no installer, no signing)
```

`npm run pack` output (`dist/mac-arm64/`, `dist/win-unpacked/`, …) is the
fastest way to test the packaged layout: run the app binary directly from
that folder. Icon files are optional for `pack`/`start` (falls back to the
default Electron icon).

---

## Production build commands

```bash
cd desktop
npm run check-icons   # fail fast if build/icon.ico / build/icon.icns are missing
npm run build:win     # Windows x64: NSIS installer + portable ZIP
npm run build:mac     # macOS: arm64 + x64 DMGs
npm run build:all     # both platforms (where the host supports them)
```

Expected output files in `desktop/dist/` (version/arch come from
`artifactName` in `package.json`):

- `Aegis Florae-1.1.0-mac-arm64.dmg` — Apple Silicon drag-to-Applications image
- `Aegis Florae-1.1.0-mac-x64.dmg` — Intel drag-to-Applications image
- `Aegis Florae-1.1.0-win-x64.exe` (NSIS setup) — exact setup name is
  `Aegis Florae-1.1.0-win-x64.exe`
- `Aegis Florae-1.1.0-win-x64.zip` — portable build for Steam depot upload
- `win-unpacked/` — unpacked portable tree used directly as the Steam depot
  source (launch executable: `AegisFlorae.exe`)

---

## How to test the unpacked application

1. `npm run pack` (macOS) or `npm run build:win` then look in
   `dist/win-unpacked/` (Windows).
2. Launch the app binary directly (`Aegis Florae.app` / `AegisFlorae.exe`) —
   no install step needed.
3. Confirm: `game.html` loads, WebGL renders (check renderer in DevTools),
   audio plays on first input gesture, a gamepad registers via the Gamepad
   API, and settings/high scores survive a window reload (localStorage).

## How to install the DMG (macOS)

1. Open `Aegis Florae-1.1.0-mac-{arm64,x64}.dmg` (match your chip).
2. Drag **Aegis Florae** onto the **Applications** link.
3. First launch of an unsigned build: right-click → Open (Gatekeeper), or
   `xattr -d com.apple.quarantine "/Applications/Aegis Florae.app"`.
4. Signed + notarized releases (see below) open normally on double-click.

## How to install the Windows EXE

1. Run the NSIS installer (`Aegis Florae-*-win-x64.exe`).
2. Pick Standard or a custom installation directory when prompted.
3. Launch from the Desktop or Start Menu shortcut.
4. Uninstall via **Settings → Apps → Aegis Florae → Uninstall** (also removes
   shortcuts; per-user save data under `%APPDATA%\Aegis Florae` is preserved).

## Steam depot usage (Windows portable build)

### Steam Depot Structure

1. Run `npm run build:win`.
2. Upload `dist/win-unpacked/` as the depot content:
   ```vdf
   "DepotBuildConfig"
   {
     "DepotID" "<DEPOT_ID>"
     "FileMapping"
     {
       "LocalPath" "desktop\\dist\\win-unpacked\\*"
       "DepotPath" "."
       "recursive" "1"
     }
   }
   ```
3. Set the Steamworks launch executable to `AegisFlorae.exe`.
4. The `.zip` artifact is the same portable tree in a single file — useful
   for DRM-free distribution and depot staging.

### Save Path & Steam Cloud Sync Configuration

Saves (`aegis_glyphs`, `aegis_settings`, `aegis_save_v1`, …) live in
`localStorage`, persisted under the Electron user-data directory:

- **Windows**: `%APPDATA%\Aegis Florae\Local Storage\leveldb\`
- **macOS**: `~/Library/Application Support/Aegis Florae/Local Storage/leveldb/`
- **Steam Auto-Cloud**: root `WinAppDataRoaming`, subdirectory `Aegis Florae`,
  pattern `*` (map macOS path equivalently).

### Steam Input & Gamepad Support

- `--enable-gamepad-button-axis-events` keeps the standard Chromium Gamepad
  API available: Xbox XInput, DualShock/DualSense, Steam Deck verified.
- Recommended Steam Input layout: **Standard Gamepad with High-Precision
  Stick Mouse**.

---

## Crash Reporting & Diagnostic Telemetry

`desktop/main.js` starts Electron's `crashReporter` at launch. Dumps stay
local by default (`uploadToServer: false`):

- Windows: `%APPDATA%\Aegis Florae\Crashpad\reports`
- macOS: `~/Library/Application Support/Aegis Florae/Crashpad/reports`

To forward to Backtrace/Sentry, set `submitURL` and `uploadToServer: true`.

---

## Icons

Production builds require both files (CI enforces via `npm run check-icons`;
electron-builder also fails on a dangling icon reference):

- `build/icon.ico` — multi-resolution Windows icon
  (16→256px; regenerate with `python3 scripts/generate-icons.py`, needs Pillow)
- `build/icon.icns` — macOS icon
  (regenerate with `./scripts/create-icns.sh <1024x1024-source.png> build/icon.icns`)

Default source artwork: `../assets/ability_glyphs_pbr.jpg` (1024×1024).

---

## Signing / notarization requirements

- **macOS**: hardened runtime + entitlements (`build/entitlements.mac.plist`)
  are always applied. Apple code signing and notarization happen **only**
  when these secrets are configured (GitHub Actions secrets or local env):
  `CSC_LINK`, `CSC_KEY_PASSWORD`, `APPLE_ID`,
  `APPLE_APP_SPECIFIC_PASSWORD`, `APPLE_TEAM_ID`.
  Without them the build succeeds unsigned (ad-hoc signature) and logs
  `skipped macOS notarization` — suitable for development and testing, not
  for public distribution. Never claim a signed/notarized release unless the
  workflow ran with these secrets present.
- **Windows**: no signing configured; the NSIS installer is unsigned and
  SmartScreen will prompt on first run. For a signed public release, add a
  code-signing certificate via `CSC_LINK`/`CSC_KEY_PASSWORD` (or
  `WIN_CSC_LINK`) in a follow-up.

---

## Release procedure

1. Update `version` in `desktop/package.json` (single source of truth).
2. Mirror the version in this README's artifact names, the CI artifact names
   in `.github/workflows/build-desktop.yml`, and
   `WINDOWS_STEAM_RELEASE_CHECKLIST.md` output names.
3. Run the full test suite (`node tests/*.test.js`) and `npm run check-icons`.
4. Tag `v<version>` (e.g. `git tag v1.1.0`) and push — CI builds, tests, and
   uploads versioned artifacts. `workflow_dispatch` allows manual runs.
5. Verify in CI: Windows NSIS+ZIP on `windows-latest`, macOS arm64+x64 DMGs
   on `macos-latest`.

## Known limitations

- Windows ARM64 is unsupported (x64 emulation only); no ARM64 build target.
- macOS minimum is 12 Monterey; older releases are untested.
- Unsigned builds trigger Gatekeeper (macOS) / SmartScreen (Windows) prompts.
- The game fetches Google Fonts and a radio stream at runtime, so the
  gameplay client needs network access for those assets.
- `blender_pipeline/*.py` generator scripts and `Unity/` sources are
  development-only and are intentionally excluded from the packaged app.
