// Concept-art tower artifacts: blender_pipeline/generate_concept_towers.py must
// produce valid, non-empty .glb exports plus preview renders for both towers.
const assert = require('assert');
const fs = require('fs');
const path = require('path');

console.log('--- Aegis Florae: Running Concept Tower Artifact Tests ---');

const rootDir = path.resolve(__dirname, '..');
const modelsDir = path.join(rootDir, 'blender_pipeline', 'models');
const rendersDir = path.join(rootDir, 'blender_pipeline', 'renders');
const gameHtml = fs.readFileSync(path.join(rootDir, 'game.html'), 'utf8');

assert.ok(fs.existsSync(path.join(rootDir, 'blender_pipeline', 'generate_concept_towers.py')),
  'generator script must exist');

for (const name of ['tower_heliostat_orchid', 'tower_mycelium_bell']) {
  const glbPath = path.join(modelsDir, name + '.glb');
  assert.ok(fs.existsSync(glbPath), name + '.glb must exist');
  const buf = fs.readFileSync(glbPath);
  assert.ok(buf.length > 50000, name + '.glb must be substantial, got ' + buf.length);
  assert.strictEqual(buf.readUInt32LE(0), 0x46546C67, name + '.glb must have glTF magic');
  assert.strictEqual(buf.readUInt32LE(12 + 4), 0x4E4F534A, name + '.glb must have JSON chunk');
  const jsonLen = buf.readUInt32LE(12);
  const gltf = JSON.parse(buf.subarray(20, 20 + jsonLen).toString('utf8'));
  assert.ok(gltf.meshes && gltf.meshes.length >= 10, name + ' must contain meshes');
  assert.ok(gltf.materials && gltf.materials.length >= 5, name + ' must contain materials');
  console.log(`✓ ${name}.glb valid (${Math.round(buf.length / 1024)} KB, ${gltf.meshes.length} meshes)`);

  const pngPath = path.join(rendersDir, name + '_render.png');
  assert.ok(fs.existsSync(pngPath), name + '_render.png must exist');
  const png = fs.readFileSync(pngPath);
  assert.strictEqual(png.readUInt32BE(0), 0x89504E47, name + ' render must be a PNG');
  assert.strictEqual(png.readUInt32BE(16), 1024, name + ' render must be 1024px wide');
  assert.strictEqual(png.readUInt32BE(20), 1024, name + ' render must be 1024px tall');
  console.log(`✓ ${name}_render.png valid 1024x1024`);
}

assert(gameHtml.includes("key: 'heliostat'"), 'Heliostat Orchid must be loaded by the local game');
assert(gameHtml.includes("key: 'mycelium'"), 'Mycelium Bell must be loaded by the local game');
assert(gameHtml.includes('mergeStaticGltfRoot(root, !decorative)'), 'Authored GLBs must be merged by material at runtime');
assert(gameHtml.includes("type === 'beam' && GLTF_CACHE.heliostat"), 'Heliostat Orchid must power the Prism role');
assert(gameHtml.includes("GLTF_CACHE.mycelium || GLTF_CACHE.resonance"), 'Mycelium Bell must power the Resonance role');
console.log('✓ Concept towers wired through runtime draw-call optimization');

console.log('\nAll Concept Tower Artifact tests passed!');
process.exit(0);
