# Aegis Flora - Electron Desktop Wrapper

This directory contains the Electron packaging setup for the Aegis Flora web game.

## Prerequisites
- Node.js (v18 or higher)
- macOS (for building the DMG)

## Getting Started

1. Navigate to this directory:
   ```bash
   cd desktop
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the app locally for testing:
   ```bash
   npm start
   ```

## Creating an Icon (.icns)

If you have a 1024x1024 PNG icon, you can generate the required `.icns` file using the provided script:
```bash
chmod +x scripts/create-icns.sh
./scripts/create-icns.sh path/to/your-icon.png build/icon.icns
```
Ensure the output file is named `icon.icns` and placed in the `build/` directory so `electron-builder` picks it up automatically.

## Building the DMG

To build a distribution-ready `.dmg` file:
```bash
npm run build
```
The resulting `.dmg` will be located in the `desktop/dist/` directory.

## Code Signing

The `package.json` and GitHub Actions workflow are configured for code signing.
To sign the app locally or via CI, you must provide the following environment variables:
- `CSC_LINK` (path or base64 of the Developer ID Application certificate .p12 file)
- `CSC_KEY_PASSWORD` (password for the certificate)
- `APPLE_ID` (your Apple ID for notarization)
- `APPLE_APP_SPECIFIC_PASSWORD` (app-specific password for notarization)
- `APPLE_TEAM_ID` (your Apple Team ID)

*If these are not provided, `electron-builder` will skip signing and output an unsigned DMG.*
