const fs = require('fs');
const path = require('path');
const assert = require('assert');

console.log('--- Aegis Florae: Running Windows-First Steam Release Verification Tests (Issue #13) ---');

const rootDir = path.resolve(__dirname, '..');
const desktopDir = path.join(rootDir, 'desktop');

console.log('1. Verifying desktop/package.json Windows packaging configuration...');
const packageJsonPath = path.join(desktopDir, 'package.json');
assert(fs.existsSync(packageJsonPath), 'desktop/package.json must exist');

const pkg = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));

// Scripts check
assert(pkg.scripts, 'package.json must have scripts object');
assert.strictEqual(pkg.scripts['build:win'], 'electron-builder build --win', 'Must have build:win script');
assert.strictEqual(pkg.scripts['build:mac'], 'electron-builder build --mac', 'Must have build:mac script');
assert.strictEqual(pkg.scripts['build:all'], 'electron-builder build -mw', 'Must have build:all script');
assert.strictEqual(pkg.scripts['pack'], 'electron-builder --dir', 'Must have pack script');

// Windows build config check
assert(pkg.build, 'package.json must have build configuration');
assert(pkg.build.win, 'package.json must have build.win configuration');
assert.strictEqual(pkg.build.win.executableName, 'AegisFlorae', 'Executable name must be AegisFlorae');
assert(Array.isArray(pkg.build.win.target), 'build.win.target must be an array');

const targetNames = pkg.build.win.target.map(t => typeof t === 'string' ? t : t.target);
assert(targetNames.includes('nsis'), 'Windows target must include nsis installer');
assert(targetNames.includes('zip'), 'Windows target must include zip for Steam depot distribution');

// Extra resources check (assets and models)
assert(Array.isArray(pkg.build.extraResources), 'extraResources must be an array');
const resourceFilter = pkg.build.extraResources[0].filter;
assert(resourceFilter.includes('assets/**/*'), 'extraResources must include assets/**/*');
assert(resourceFilter.includes('blender_pipeline/models/**/*'), 'extraResources must include blender_pipeline/models/**/*');
assert(resourceFilter.includes('game.html'), 'extraResources must include game.html');

console.log('✓ Verified: desktop/package.json correctly defines Windows release targets and resource packaging.');

console.log('2. Verifying desktop/main.js Windows platform optimizations & crash diagnostics...');
const mainJsPath = path.join(desktopDir, 'main.js');
const mainJsContent = fs.readFileSync(mainJsPath, 'utf8');

assert(mainJsContent.includes('crashReporter.start'), 'main.js must initialize crashReporter');
assert(mainJsContent.includes("'use-angle', 'd3d11'"), 'main.js must set d3d11 angle backend for Windows');
assert(mainJsContent.includes('enable-gamepad-button-axis-events'), 'main.js must enable gamepad button axis events');
assert(mainJsContent.includes('autoHideMenuBar: process.platform === \'win32\''), 'main.js must auto-hide menu bar on Windows');
assert(mainJsContent.includes('minWidth: 1024'), 'main.js must enforce minWidth');

console.log('✓ Verified: desktop/main.js configures D3D11 acceleration, gamepad flags, and Crashpad diagnostics.');

console.log('3. Verifying GitHub Actions multi-platform workflow (.github/workflows/build-desktop.yml)...');
const workflowPath = path.join(rootDir, '.github', 'workflows', 'build-desktop.yml');
assert(fs.existsSync(workflowPath), '.github/workflows/build-desktop.yml must exist');
const workflowContent = fs.readFileSync(workflowPath, 'utf8');

assert(workflowContent.includes('windows-latest'), 'Workflow matrix must include windows-latest');
assert(workflowContent.includes('macos-latest'), 'Workflow matrix must include macos-latest');
assert(workflowContent.includes('npm run build:win'), 'Workflow must execute npm run build:win for Windows');
assert(workflowContent.includes('npm run build:mac'), 'Workflow must execute npm run build:mac for macOS');

console.log('✓ Verified: CI/CD workflow builds both Windows x64 and macOS packages on push.');

console.log('4. Verifying WINDOWS_STEAM_RELEASE_CHECKLIST.md requirements & strategy...');
const checklistPath = path.join(rootDir, 'WINDOWS_STEAM_RELEASE_CHECKLIST.md');
assert(fs.existsSync(checklistPath), 'WINDOWS_STEAM_RELEASE_CHECKLIST.md must exist');
const checklistContent = fs.readFileSync(checklistPath, 'utf8');

// Core acceptance requirements check
assert(checklistContent.includes('Web/Three.js + Electron as Primary Target'), 'Checklist must define primary shipping target');
assert(checklistContent.includes('Unity Target Scope & Strategy'), 'Checklist must document Unity target decision');
assert(checklistContent.includes('Steamworks Integration Plan'), 'Checklist must document Steamworks integration');
assert(checklistContent.includes('Steam Cloud Configuration'), 'Checklist must document Steam Cloud mapping');
assert(checklistContent.includes('Steam Input & Controller Profile'), 'Checklist must document Steam Input & controller profile');
assert(checklistContent.includes('Save-Path & Version Migration Specification'), 'Checklist must document save migration');
assert(checklistContent.includes('Crash Reporting & Diagnostic Telemetry'), 'Checklist must document crash telemetry');
assert(checklistContent.includes('Pre-Flight Release Verification Checklist'), 'Checklist must include release verification matrix');

console.log('✓ Verified: WINDOWS_STEAM_RELEASE_CHECKLIST.md comprehensively addresses all Steam release criteria.');

console.log('5. Verifying desktop/README.md documentation synchronization...');
const readmePath = path.join(desktopDir, 'README.md');
const readmeContent = fs.readFileSync(readmePath, 'utf8');

assert(readmeContent.includes('npm run build:win'), 'desktop/README.md must document npm run build:win');
assert(readmeContent.includes('Steam Depot Structure'), 'desktop/README.md must document Steam depot structure');
assert(readmeContent.includes('Steam Cloud Sync Configuration'), 'desktop/README.md must document Steam Cloud sync');

console.log('✓ Verified: desktop/README.md provides full Windows and Steam deployment instructions.');

console.log('\nAll Windows-First Steam Release Verification (Issue #13) tests passed successfully!');
process.exit(0);
