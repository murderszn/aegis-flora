#!/usr/bin/env node
/**
 * Pre-build gate for production desktop releases.
 * Fails with a clear message when required icon files are missing so that
 * electron-builder never runs with dangling `build/icon.*` references.
 *
 * Icon-less development runs (`npm start`, `electron-builder --dir`) are
 * unaffected — main.js falls back to the default Electron icon.
 *
 * Usage: node scripts/check-icons.js
 */
const fs = require('fs');
const path = require('path');

const buildDir = path.join(__dirname, '..', 'build');
const required = ['icon.ico', 'icon.icns'];
const missing = required.filter((f) => !fs.existsSync(path.join(buildDir, f)));

if (missing.length > 0) {
  console.error('ERROR: missing required production icon(s): ' + missing.join(', '));
  console.error('Expected location: desktop/build/');
  console.error('Generate them with:');
  console.error('  macOS icon : ./scripts/create-icns.sh <1024x1024-source.png> build/icon.icns');
  console.error('  Windows icon: python3 scripts/generate-icons.py [source] [build/icon.ico]');
  console.error('Default source artwork: ../assets/ability_glyphs_pbr.jpg (1024x1024).');
  process.exit(1);
}

for (const f of required) {
  const st = fs.statSync(path.join(buildDir, f));
  if (st.size === 0) {
    console.error(`ERROR: desktop/build/${f} is empty — regenerate it (see above).`);
    process.exit(1);
  }
  console.log(`ok: build/${f} (${st.size} bytes)`);
}
