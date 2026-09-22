"""
Aegis Flora: Flower Bunches & Greek Ruins Asset Generator
Generates GLTF (.glb) models and isometric PNG renders using Blender's Python API.

Assets:
  1. flora_hero_bouquet       — Lush overflowing bouquet of chrysanthemums, peonies, lavender & ivy
                                 wrapped in aged parchment with brass wire, on a marble slab.
  2. flora_hanging_garland    — Draped floral garland/swag of wisteria, chrysanthemums & trailing
                                 ivy, designed to hang between columns or over archways.
  3. flora_overgrown_urn      — Classical stone urn cracked open with wild chrysanthemums, peonies
                                 & moss erupting from inside. Nature reclaiming architecture.
  4. ruin_doric_temple_facade — Three-column Doric temple front with fractured entablature, one
                                 column collapsed, pitted marble, lichen patches, scattered fragments.
  5. ruin_amphitheater_seats  — Curved semicircular stone seating tiers (cavea) partially collapsed,
                                 with wild grass tufts and flower accents growing between cracks.
  6. ruin_rubble_scatter_kit  — Modular debris kit: fallen column drums, carved frieze fragments,
                                 broken pediment chunks, loose ashlar blocks, with moss & flowers.

Run in Blender:
  blender --background --python generate_flower_bunches_and_ruins.py
"""

import bpy
import bmesh
import math
import os
import random

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
RENDERS_DIR = os.path.join(BASE_DIR, "renders")
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(RENDERS_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Shared Utilities (matching existing pipeline conventions)
# ---------------------------------------------------------------------------

def clear_scene():
    """Wipe everything for a clean build."""
    bpy.ops.wm.read_factory_settings(use_empty=True)


def set_input(node, name, val):
    """Version-safe node input setter (handles Blender 4.x / 5.x name changes)."""
    if name in node.inputs:
        node.inputs[name].default_value = val
    elif name == "Emission Color" and "Emission" in node.inputs:
        node.inputs["Emission"].default_value = val


def make_material(name, color, metallic=0.0, roughness=0.5,
                  emission=None, emission_strength=1.0):
    """Create a Principled BSDF PBR material."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()

    bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
    bsdf.location = (0, 0)
    set_input(bsdf, "Base Color", color)
    set_input(bsdf, "Metallic", metallic)
    set_input(bsdf, "Roughness", roughness)

    if emission:
        set_input(bsdf, "Emission Color", emission)
        set_input(bsdf, "Emission Strength", emission_strength)

    out = nodes.new(type="ShaderNodeOutputMaterial")
    out.location = (300, 0)
    mat.node_tree.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def setup_camera_and_lighting(target_z=2.0, ortho_scale=5.5):
    """Isometric camera rig + Aegis Flora 3-light studio setup."""
    # Camera
    cam_data = bpy.data.cameras.new(name="IsoCam")
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = ortho_scale
    cam = bpy.data.objects.new("IsoCam", cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = (6.0, -6.0, 5.0 + target_z)
    cam.rotation_euler = (math.radians(54.736), 0, math.radians(45))
    bpy.context.scene.camera = cam

    # Key Sun — Warm Gold (Mediterranean afternoon)
    sun_data = bpy.data.lights.new("SunKey", 'SUN')
    sun_data.energy = 4.8
    sun_data.color = (1.0, 0.96, 0.88)
    sun = bpy.data.objects.new("SunKey", sun_data)
    sun.rotation_euler = (math.radians(45), math.radians(20), math.radians(35))
    bpy.context.collection.objects.link(sun)

    # Fill Sun — Teal Ambient (deep cerulean sky bounce)
    fill_data = bpy.data.lights.new("FillTeal", 'SUN')
    fill_data.energy = 2.4
    fill_data.color = (0.15, 0.55, 0.65)
    fill = bpy.data.objects.new("FillTeal", fill_data)
    fill.rotation_euler = (math.radians(-35), math.radians(-15), math.radians(-130))
    bpy.context.collection.objects.link(fill)

    # Rim Light — Amber Glow (solar-edge catchlight)
    rim_data = bpy.data.lights.new("RimAmber", 'POINT')
    rim_data.energy = 220.0
    rim_data.color = (1.0, 0.75, 0.3)
    rim = bpy.data.objects.new("RimAmber", rim_data)
    rim.location = (-4.0, 4.0, target_z + 3.0)
    bpy.context.collection.objects.link(rim)

    # Render settings — EEVEE, 1K, transparent bg
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024
    scene.render.film_transparent = True


def smooth_object(obj):
    """Enable smooth shading on all faces."""
    for poly in obj.data.polygons:
        poly.use_smooth = True


def export_and_render(objs, model_name, render_name):
    """Select objects, export GLB, render PNG."""
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]

    glb = os.path.join(MODELS_DIR, f"{model_name}.glb")
    bpy.ops.export_scene.gltf(filepath=glb, export_format='GLB', use_selection=True)

    render_file = os.path.join(RENDERS_DIR, f"{render_name}.png")
    bpy.context.scene.render.filepath = render_file
    bpy.ops.render.render(write_still=True)
    print(f"  ✔ {model_name}: {glb}")
    print(f"  ✔ {render_name}: {render_file}")


# ---------------------------------------------------------------------------
# Aegis Flora Material Palette (consistent across all assets)
# ---------------------------------------------------------------------------

def palette():
    """Return dict of canonical Aegis Flora PBR materials."""
    return {
        # Architecture & Stone
        "marble":       make_material("CarraraMarble",      (0.90, 0.88, 0.82, 1.0), metallic=0.04, roughness=0.35),
        "marble_aged":  make_material("AgedMarble",         (0.78, 0.75, 0.68, 1.0), metallic=0.04, roughness=0.50),
        "travertine":   make_material("Travertine",         (0.82, 0.76, 0.62, 1.0), metallic=0.04, roughness=0.55),
        "flagstone":    make_material("Flagstone",          (0.52, 0.50, 0.46, 1.0), metallic=0.04, roughness=0.65),

        # Metals
        "brass":        make_material("AntiqueBrass",       (0.88, 0.68, 0.22, 1.0), metallic=0.92, roughness=0.22),
        "iron":         make_material("CastIron",           (0.18, 0.20, 0.22, 1.0), metallic=0.88, roughness=0.45),

        # Flora — Flowers
        "chrysanthemum":make_material("ChrysanthemumGold",  (0.95, 0.72, 0.08, 1.0), metallic=0.05, roughness=0.50),
        "peony":        make_material("PeonyMagenta",       (0.90, 0.38, 0.55, 1.0), metallic=0.00, roughness=0.55),
        "peony_pale":   make_material("PeonyPale",          (0.95, 0.72, 0.78, 1.0), metallic=0.00, roughness=0.45),
        "lavender":     make_material("AlpineLavender",     (0.58, 0.45, 0.82, 1.0), metallic=0.00, roughness=0.60),
        "wisteria":     make_material("WisteriaLilac",      (0.65, 0.42, 0.78, 1.0), metallic=0.00, roughness=0.55),
        "poppy_red":    make_material("PoppyRed",           (0.88, 0.18, 0.15, 1.0), metallic=0.00, roughness=0.50),
        "chamomile":    make_material("ChamomileWhite",     (0.96, 0.94, 0.82, 1.0), metallic=0.00, roughness=0.45),

        # Flora — Foliage
        "ivy":          make_material("IvyGreen",           (0.18, 0.42, 0.16, 1.0), metallic=0.00, roughness=0.60),
        "moss":         make_material("MossGreen",          (0.24, 0.44, 0.20, 1.0), metallic=0.00, roughness=0.70),
        "leaf_dark":    make_material("LeafDark",           (0.12, 0.32, 0.14, 1.0), metallic=0.00, roughness=0.55),
        "stem_green":   make_material("StemGreen",          (0.22, 0.38, 0.18, 1.0), metallic=0.00, roughness=0.55),
        "grass":        make_material("WildGrass",          (0.32, 0.52, 0.22, 1.0), metallic=0.00, roughness=0.55),

        # Wrapping / Organic
        "parchment":    make_material("AgedParchment",      (0.72, 0.62, 0.48, 1.0), metallic=0.00, roughness=0.70),
        "twine":        make_material("HempTwine",          (0.55, 0.45, 0.32, 1.0), metallic=0.00, roughness=0.80),
        "soil":         make_material("RichSoil",           (0.16, 0.12, 0.08, 1.0), metallic=0.00, roughness=0.90),

        # Lichen & weathering
        "lichen_orange":make_material("LichenOrange",       (0.78, 0.52, 0.18, 1.0), metallic=0.00, roughness=0.80),
        "lichen_grey":  make_material("LichenGrey",         (0.55, 0.58, 0.52, 1.0), metallic=0.00, roughness=0.75),

        # Energy / VFX
        "cyan_mana":    make_material("CyanMana",           (0.0, 0.95, 0.85, 1.0),
                                      emission=(0.0, 0.95, 0.85, 1.0), emission_strength=4.0),
        "spore_glow":   make_material("SporeGlow",          (0.0, 0.95, 0.88, 1.0),
                                      emission=(0.0, 0.95, 0.88, 1.0), emission_strength=3.5),
    }


# ==============================================================================
# HELPER: Flower-building sub-functions (reusable across assets)
# ==============================================================================

def _add_chrysanthemum(objs, mat, x, y, z, scale=0.18):
    """Dense multi-layered chrysanthemum flower head."""
    # Core dome
    bpy.ops.mesh.primitive_uv_sphere_add(radius=scale * 0.85, location=(x, y, z))
    core = bpy.context.active_object
    core.scale = (1.0, 1.0, 0.6)
    core.data.materials.append(mat)
    smooth_object(core)
    objs.append(core)
    # Radiating petal ring (8 petals)
    for p in range(8):
        pa = p * (math.pi / 4)
        px = x + math.cos(pa) * scale * 1.1
        py = y + math.sin(pa) * scale * 1.1
        bpy.ops.mesh.primitive_cylinder_add(radius=scale * 0.35, depth=scale * 1.8,
                                            vertices=8, location=(px, py, z - scale * 0.1))
        pet = bpy.context.active_object
        pet.scale = (0.5, 0.12, 1.0)
        pet.rotation_euler = (math.radians(30) * math.sin(pa),
                              -math.radians(30) * math.cos(pa),
                              pa + math.pi / 2)
        pet.data.materials.append(mat)
        smooth_object(pet)
        objs.append(pet)


def _add_peony(objs, mat, x, y, z, scale=0.22):
    """Lush ruffled peony bloom."""
    bpy.ops.mesh.primitive_uv_sphere_add(radius=scale, location=(x, y, z))
    bloom = bpy.context.active_object
    bloom.scale = (1.1, 1.1, 0.65)
    bloom.data.materials.append(mat)
    smooth_object(bloom)
    objs.append(bloom)
    # Outer ruffled petals (6)
    for p in range(6):
        pa = p * (math.pi / 3) + 0.15
        px = x + math.cos(pa) * scale * 1.2
        py = y + math.sin(pa) * scale * 1.2
        bpy.ops.mesh.primitive_uv_sphere_add(radius=scale * 0.55, location=(px, py, z - scale * 0.15))
        ruf = bpy.context.active_object
        ruf.scale = (1.0, 0.5, 0.4)
        ruf.rotation_euler = (0, 0, pa)
        ruf.data.materials.append(mat)
        smooth_object(ruf)
        objs.append(ruf)


def _add_lavender_spike(objs, mat_flower, mat_stem, x, y, z, height=0.7):
    """Tall lavender spike — thin stem topped with a tapered cluster."""
    bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=height, vertices=8,
                                        location=(x, y, z + height * 0.4))
    stem = bpy.context.active_object
    stem.data.materials.append(mat_stem)
    objs.append(stem)
    # Flower cluster at top
    bpy.ops.mesh.primitive_cone_add(vertices=10, radius1=0.06, depth=height * 0.35,
                                    location=(x, y, z + height * 0.75))
    tip = bpy.context.active_object
    tip.data.materials.append(mat_flower)
    smooth_object(tip)
    objs.append(tip)


def _add_ivy_trail(objs, mat, cx, cy, start_z, steps=10, radius=0.35, climb=0.15):
    """Spiral of small ivy leaf spheres climbing up from (cx, cy, start_z)."""
    for i in range(steps):
        ang = i * 0.6
        ix = cx + math.cos(ang) * radius
        iy = cy + math.sin(ang) * radius
        iz = start_z + i * climb
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, location=(ix, iy, iz))
        leaf = bpy.context.active_object
        leaf.scale = (1.0, 1.0, 0.35)
        leaf.data.materials.append(mat)
        smooth_object(leaf)
        objs.append(leaf)


def _add_moss_patch(objs, mat, x, y, z, radius=0.3):
    """Flat, irregular moss blob on a surface."""
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=(x, y, z))
    moss = bpy.context.active_object
    moss.scale = (1.2, 1.0, 0.15)
    moss.data.materials.append(mat)
    smooth_object(moss)
    objs.append(moss)


def _add_grass_tuft(objs, mat, x, y, z, blades=5, height=0.4):
    """Cluster of thin grass blade cylinders."""
    for b in range(blades):
        ba = b * (2 * math.pi / blades) + (b * 0.3)
        bx = x + math.cos(ba) * 0.04
        by = y + math.sin(ba) * 0.04
        lean = math.radians(8 + b * 3)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=height + b * 0.03,
                                            vertices=6, location=(bx, by, z + height * 0.45))
        blade = bpy.context.active_object
        blade.rotation_euler = (lean * math.sin(ba), -lean * math.cos(ba), ba)
        blade.data.materials.append(mat)
        objs.append(blade)


# ==============================================================================
# 1. FLORA: HERO FLOWER BOUQUET
#    A lush overflowing bunch of chrysanthemums, peonies, lavender & ivy
#    wrapped in aged parchment with brass wire, resting on a marble slab.
# ==============================================================================

def build_hero_bouquet():
    clear_scene()
    setup_camera_and_lighting(target_z=1.4, ortho_scale=5.0)
    p = palette()
    objs = []

    # -- Marble Display Slab --
    bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0.1))
    slab = bpy.context.active_object
    slab.scale = (1.0, 0.8, 0.08)
    slab.data.materials.append(p["marble"])
    objs.append(slab)

    # -- Parchment Wrap (angled cone to suggest gathered paper) --
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.65, radius2=0.15,
                                    depth=1.6, location=(0, 0, 0.75))
    wrap = bpy.context.active_object
    wrap.rotation_euler = (math.radians(-10), math.radians(5), 0)
    wrap.data.materials.append(p["parchment"])
    smooth_object(wrap)
    objs.append(wrap)

    # -- Brass Twine Bindings (2 wire rings) --
    for ring_z in [0.55, 0.85]:
        bpy.ops.mesh.primitive_torus_add(major_radius=0.42, minor_radius=0.018,
                                         major_segments=24, minor_segments=8,
                                         location=(0, 0, ring_z))
        ring = bpy.context.active_object
        ring.data.materials.append(p["brass"])
        smooth_object(ring)
        objs.append(ring)

    # -- Hemp Twine Bow at center --
    bpy.ops.mesh.primitive_torus_add(major_radius=0.18, minor_radius=0.025,
                                     major_segments=16, minor_segments=8,
                                     location=(0, -0.42, 0.7))
    bow = bpy.context.active_object
    bow.rotation_euler = (math.radians(75), 0, 0)
    bow.data.materials.append(p["twine"])
    smooth_object(bow)
    objs.append(bow)

    # -- Main Flower Dome: Central chrysanthemum cluster --
    #    Dense arrangement bursting out the top of the wrap
    chrys_positions = [
        (0.0, 0.0, 1.55),
        (0.22, 0.15, 1.48), (-0.20, 0.12, 1.50),
        (0.10, -0.22, 1.45), (-0.15, -0.18, 1.42),
        (0.30, -0.05, 1.38), (-0.32, 0.0, 1.40),
    ]
    for cx, cy, cz in chrys_positions:
        _add_chrysanthemum(objs, p["chrysanthemum"], cx, cy, cz, scale=0.17)

    # -- Peony accents (larger, magenta/pale pink) --
    peony_positions = [
        (0.35, 0.25, 1.35, "peony"),
        (-0.38, 0.22, 1.38, "peony_pale"),
        (0.05, 0.35, 1.32, "peony"),
        (-0.25, -0.30, 1.30, "peony_pale"),
        (0.28, -0.28, 1.28, "peony"),
    ]
    for px, py, pz, pmat in peony_positions:
        _add_peony(objs, p[pmat], px, py, pz, scale=0.20)

    # -- Lavender spikes poking upward --
    lav_positions = [
        (0.40, 0.10, 1.20), (-0.42, -0.10, 1.22),
        (0.15, 0.38, 1.18), (-0.10, 0.40, 1.15),
        (0.32, -0.32, 1.12), (-0.35, 0.28, 1.14),
        (0.0, -0.40, 1.10), (0.45, -0.15, 1.08),
    ]
    for lx, ly, lz in lav_positions:
        _add_lavender_spike(objs, p["lavender"], p["stem_green"], lx, ly, lz, height=0.65)

    # -- Chamomile sprigs (small white puffs) --
    for ci in range(6):
        ca = ci * (math.pi / 3) + 0.4
        cx = math.cos(ca) * 0.48
        cy = math.sin(ca) * 0.42
        cz = 1.25 + (ci % 2) * 0.1
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(cx, cy, cz))
        cham = bpy.context.active_object
        cham.scale = (1, 1, 0.5)
        cham.data.materials.append(p["chamomile"])
        smooth_object(cham)
        objs.append(cham)

    # -- Trailing ivy tendrils draping downward --
    _add_ivy_trail(objs, p["ivy"], 0.5, 0.0, 0.35, steps=8, radius=0.12, climb=-0.06)
    _add_ivy_trail(objs, p["ivy"], -0.45, 0.15, 0.40, steps=7, radius=0.10, climb=-0.05)
    _add_ivy_trail(objs, p["leaf_dark"], 0.1, -0.48, 0.32, steps=6, radius=0.08, climb=-0.04)

    # -- Scattered fallen petals on slab --
    for fi in range(8):
        fa = fi * 0.85 + 0.3
        fx = math.cos(fa) * (0.55 + fi * 0.06)
        fy = math.sin(fa) * (0.45 + fi * 0.04)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=0.008, vertices=8,
                                            location=(fx, fy, 0.19))
        petal = bpy.context.active_object
        petal.rotation_euler = (0, 0, fa * 2.3)
        petal.data.materials.append(p["chrysanthemum"] if fi % 2 == 0 else p["peony"])
        objs.append(petal)

    # -- Floating cyan mana spores (Aegis Flora signature) --
    for si in range(4):
        sa = si * (math.pi / 2) + 0.5
        sx = math.cos(sa) * 0.3
        sy = math.sin(sa) * 0.25
        sz = 1.7 + si * 0.12
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.04, location=(sx, sy, sz))
        spore = bpy.context.active_object
        spore.data.materials.append(p["spore_glow"])
        objs.append(spore)

    export_and_render(objs, "flora_hero_bouquet", "flora_hero_bouquet_render")


# ==============================================================================
# 2. FLORA: HANGING FLORAL GARLAND / SWAG
#    Designed to drape between columns, over archways, or along balustrades.
#    Crescent-shaped catenary curve of wisteria, chrysanthemums & ivy.
# ==============================================================================

def build_hanging_garland():
    clear_scene()
    setup_camera_and_lighting(target_z=1.6, ortho_scale=6.0)
    p = palette()
    objs = []

    # -- Brass Mounting Hooks (two anchor points) --
    for hx in [-1.6, 1.6]:
        bpy.ops.mesh.primitive_torus_add(major_radius=0.12, minor_radius=0.03,
                                         major_segments=16, minor_segments=8,
                                         location=(hx, 0, 2.6))
        hook = bpy.context.active_object
        hook.data.materials.append(p["brass"])
        smooth_object(hook)
        objs.append(hook)

    # -- Main Garland Vine Rope (catenary curve using positioned cylinders) --
    garland_points = 20
    for i in range(garland_points):
        t = (i / (garland_points - 1)) * 2.0 - 1.0  # -1 to 1
        gx = t * 1.6
        # Catenary sag: deepest at center
        gz = 2.5 - 0.8 * (1.0 - t * t)
        gy = 0.0
        bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.18, vertices=8,
                                            location=(gx, gy, gz))
        seg = bpy.context.active_object
        # Angle each segment toward the next
        if i < garland_points - 1:
            next_t = ((i + 1) / (garland_points - 1)) * 2.0 - 1.0
            next_gz = 2.5 - 0.8 * (1.0 - next_t * next_t)
            dx = (next_t * 1.6) - gx
            dz = next_gz - gz
            seg.rotation_euler = (0, math.atan2(dz, dx) - math.pi / 2, math.radians(90))
        seg.data.materials.append(p["ivy"] if i % 3 != 0 else p["stem_green"])
        smooth_object(seg)
        objs.append(seg)

        # Flowers and wisteria draping at intervals
        if i % 3 == 0:
            _add_chrysanthemum(objs, p["chrysanthemum"], gx, gy, gz - 0.05, scale=0.14)
        elif i % 3 == 1:
            _add_peony(objs, p["peony"], gx + 0.05, gy, gz - 0.08, scale=0.12)

    # -- Hanging Wisteria Cascades (cone clusters drooping down) --
    wist_x = [-1.1, -0.4, 0.3, 1.0]
    for wx in wist_x:
        t = wx / 1.6  # normalized position
        wz = 2.5 - 0.8 * (1.0 - t * t)
        for droop in range(3):
            bpy.ops.mesh.primitive_cone_add(vertices=10, radius1=0.10 - droop * 0.02,
                                            depth=0.35 - droop * 0.06,
                                            location=(wx + droop * 0.03, 0.05, wz - 0.2 - droop * 0.28))
            wist = bpy.context.active_object
            wist.rotation_euler = (math.radians(180), 0, 0)
            wist.data.materials.append(p["wisteria"])
            smooth_object(wist)
            objs.append(wist)

    # -- Ivy leaf trails along the catenary --
    _add_ivy_trail(objs, p["ivy"], -0.8, 0.08, 1.85, steps=6, radius=0.06, climb=-0.08)
    _add_ivy_trail(objs, p["leaf_dark"], 0.6, -0.08, 1.90, steps=5, radius=0.05, climb=-0.07)

    # -- Chamomile sprigs for lightness --
    for ci in range(5):
        cx = -1.2 + ci * 0.6
        t = cx / 1.6
        cz = 2.5 - 0.8 * (1.0 - t * t) + 0.12
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, location=(cx, 0.08, cz))
        cham = bpy.context.active_object
        cham.scale = (1, 1, 0.5)
        cham.data.materials.append(p["chamomile"])
        smooth_object(cham)
        objs.append(cham)

    export_and_render(objs, "flora_hanging_garland", "flora_hanging_garland_render")


# ==============================================================================
# 3. FLORA: OVERGROWN URN PLANTER
#    Classical stone urn cracked open with chrysanthemums, peonies & moss
#    erupting from inside — nature reclaiming architecture.
# ==============================================================================

def build_overgrown_urn():
    clear_scene()
    setup_camera_and_lighting(target_z=1.4, ortho_scale=4.8)
    p = palette()
    objs = []

    # -- Stepped marble plinth --
    bpy.ops.mesh.primitive_cylinder_add(radius=0.75, depth=0.14, vertices=24, location=(0, 0, 0.07))
    base1 = bpy.context.active_object
    base1.data.materials.append(p["marble"])
    smooth_object(base1)
    objs.append(base1)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.58, depth=0.10, vertices=24, location=(0, 0, 0.19))
    base2 = bpy.context.active_object
    base2.data.materials.append(p["marble_aged"])
    smooth_object(base2)
    objs.append(base2)

    # -- Urn stem --
    bpy.ops.mesh.primitive_cylinder_add(radius=0.20, depth=0.28, vertices=16, location=(0, 0, 0.38))
    stem = bpy.context.active_object
    stem.data.materials.append(p["marble_aged"])
    smooth_object(stem)
    objs.append(stem)

    # -- Urn body (lower cone + mid sphere + upper cone + flared lip) --
    bpy.ops.mesh.primitive_cone_add(radius1=0.20, radius2=0.62, depth=0.52, vertices=20,
                                    location=(0, 0, 0.76))
    body_lo = bpy.context.active_object
    body_lo.data.materials.append(p["marble"])
    smooth_object(body_lo)
    objs.append(body_lo)

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.65, location=(0, 0, 1.15))
    body_mid = bpy.context.active_object
    body_mid.scale = (1.0, 1.0, 0.75)
    body_mid.data.materials.append(p["marble"])
    smooth_object(body_mid)
    objs.append(body_mid)

    bpy.ops.mesh.primitive_cone_add(radius1=0.60, radius2=0.32, depth=0.40, vertices=20,
                                    location=(0, 0, 1.55))
    shoulder = bpy.context.active_object
    shoulder.data.materials.append(p["marble_aged"])
    smooth_object(shoulder)
    objs.append(shoulder)

    bpy.ops.mesh.primitive_torus_add(major_radius=0.38, minor_radius=0.055,
                                     major_segments=24, minor_segments=10,
                                     location=(0, 0, 1.75))
    lip = bpy.context.active_object
    lip.data.materials.append(p["brass"])
    smooth_object(lip)
    objs.append(lip)

    # -- Crack / break chunk (displaced shard revealing interior) --
    bpy.ops.mesh.primitive_cube_add(size=0.35, location=(0.52, -0.15, 1.0))
    shard = bpy.context.active_object
    shard.rotation_euler = (math.radians(15), math.radians(25), math.radians(40))
    shard.data.materials.append(p["marble_aged"])
    objs.append(shard)

    # -- Soil / earth visible in the crack --
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25, location=(0.45, -0.10, 0.95))
    soil = bpy.context.active_object
    soil.scale = (1.0, 0.8, 0.5)
    soil.data.materials.append(p["soil"])
    smooth_object(soil)
    objs.append(soil)

    # -- Flowers ERUPTING from top and crack --

    # Top: dense chrysanthemum dome
    top_flowers = [
        (0.0, 0.0, 1.95), (0.18, 0.12, 1.88), (-0.15, 0.10, 1.90),
        (0.08, -0.18, 1.85), (-0.20, -0.08, 1.82), (0.25, 0.0, 1.80),
    ]
    for fx, fy, fz in top_flowers:
        _add_chrysanthemum(objs, p["chrysanthemum"], fx, fy, fz, scale=0.16)

    # Side crack: peonies bursting through
    crack_peonies = [
        (0.55, -0.08, 1.15), (0.48, -0.20, 0.92), (0.60, 0.05, 1.05),
    ]
    for cpx, cpy, cpz in crack_peonies:
        _add_peony(objs, p["peony"], cpx, cpy, cpz, scale=0.18)

    # -- Lavender spikes rising from the top --
    for li in range(5):
        la = li * (math.pi / 2.5) + 0.3
        lx = math.cos(la) * 0.28
        ly = math.sin(la) * 0.25
        _add_lavender_spike(objs, p["lavender"], p["stem_green"], lx, ly, 1.70, height=0.55)

    # -- Moss patches on the body --
    _add_moss_patch(objs, p["moss"], 0.35, 0.40, 1.10, radius=0.18)
    _add_moss_patch(objs, p["moss"], -0.40, -0.30, 0.85, radius=0.15)
    _add_moss_patch(objs, p["moss"], 0.0, 0.55, 1.25, radius=0.12)

    # -- Ivy climbing up the urn --
    _add_ivy_trail(objs, p["ivy"], 0.0, 0.0, 0.30, steps=12, radius=0.55, climb=0.12)

    # -- Lichen patches (orange weathering) --
    for lx, ly, lz in [(0.48, 0.30, 1.30), (-0.50, 0.20, 0.70), (0.20, -0.55, 1.05)]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(lx, ly, lz))
        lich = bpy.context.active_object
        lich.scale = (1.5, 1.2, 0.12)
        lich.data.materials.append(p["lichen_orange"])
        smooth_object(lich)
        objs.append(lich)

    export_and_render(objs, "flora_overgrown_urn", "flora_overgrown_urn_render")


# ==============================================================================
# 4. RUIN: DORIC TEMPLE FAÇADE
#    Three fluted Doric columns (one collapsed) with fractured entablature,
#    triangular pediment, pitted marble, lichen, scattered stone fragments,
#    chrysanthemums & ivy growing in the cracks.
# ==============================================================================

def build_doric_temple():
    clear_scene()
    setup_camera_and_lighting(target_z=2.5, ortho_scale=9.0)
    p = palette()
    objs = []

    # -- Massive Stepped Stylobate Foundation (3 tiers) --
    for tier_i, (tier_w, tier_d, tier_h, tier_z) in enumerate([
        (5.2, 2.4, 0.18, 0.09),
        (4.8, 2.0, 0.16, 0.25),
        (4.4, 1.7, 0.14, 0.39),
    ]):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, tier_z))
        step = bpy.context.active_object
        step.scale = (tier_w, tier_d, tier_h)
        step.data.materials.append(p["marble"] if tier_i == 0 else p["marble_aged"])
        objs.append(step)

    # -- Three Doric Columns --
    col_positions = [(-1.5, 0, "standing"), (0.0, 0, "standing"), (1.5, 0, "collapsed")]

    for ci, (cx, cy, state) in enumerate(col_positions):
        # Column base (torus ring)
        bpy.ops.mesh.primitive_torus_add(major_radius=0.35, minor_radius=0.06,
                                         major_segments=20, minor_segments=10,
                                         location=(cx, cy, 0.50))
        cbase = bpy.context.active_object
        cbase.data.materials.append(p["marble"])
        smooth_object(cbase)
        objs.append(cbase)

        if state == "standing":
            # Fluted column shaft (use cylinder with tapered entasis)
            col_height = 2.8
            bpy.ops.mesh.primitive_cylinder_add(radius=0.28, depth=col_height, vertices=20,
                                                location=(cx, cy, 0.50 + col_height / 2))
            shaft = bpy.context.active_object
            shaft.data.materials.append(p["marble_aged"])
            smooth_object(shaft)
            objs.append(shaft)

            # Doric echinus (simple flaring cushion) + abacus slab
            bpy.ops.mesh.primitive_cone_add(vertices=20, radius1=0.32, radius2=0.40,
                                            depth=0.18, location=(cx, cy, 3.38))
            echinus = bpy.context.active_object
            echinus.data.materials.append(p["marble"])
            smooth_object(echinus)
            objs.append(echinus)

            bpy.ops.mesh.primitive_cube_add(size=0.85, location=(cx, cy, 3.55))
            abacus = bpy.context.active_object
            abacus.scale = (1.0, 1.0, 0.18)
            abacus.data.materials.append(p["marble"])
            objs.append(abacus)

        else:
            # Collapsed column: short stump + fallen drums
            bpy.ops.mesh.primitive_cylinder_add(radius=0.28, depth=0.9, vertices=20,
                                                location=(cx, cy, 0.95))
            stump = bpy.context.active_object
            stump.data.materials.append(p["marble_aged"])
            smooth_object(stump)
            objs.append(stump)

            # Fallen drum #1 — rolled to the side
            bpy.ops.mesh.primitive_cylinder_add(radius=0.26, depth=0.65, vertices=18,
                                                location=(cx + 0.6, cy + 0.5, 0.28))
            drum1 = bpy.context.active_object
            drum1.rotation_euler = (math.radians(88), 0, math.radians(35))
            drum1.data.materials.append(p["marble_aged"])
            smooth_object(drum1)
            objs.append(drum1)

            # Fallen drum #2
            bpy.ops.mesh.primitive_cylinder_add(radius=0.24, depth=0.55, vertices=16,
                                                location=(cx + 0.3, cy - 0.6, 0.24))
            drum2 = bpy.context.active_object
            drum2.rotation_euler = (math.radians(82), math.radians(15), math.radians(-20))
            drum2.data.materials.append(p["travertine"])
            smooth_object(drum2)
            objs.append(drum2)

            # Fallen abacus slab
            bpy.ops.mesh.primitive_cube_add(size=0.75, location=(cx + 0.9, cy + 0.2, 0.18))
            fallen_abacus = bpy.context.active_object
            fallen_abacus.scale = (1.0, 1.0, 0.2)
            fallen_abacus.rotation_euler = (math.radians(8), math.radians(-12), math.radians(42))
            fallen_abacus.data.materials.append(p["marble"])
            objs.append(fallen_abacus)

    # -- Fractured Entablature / Architrave spanning the two standing columns --
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.75, 0, 3.75))
    archi = bpy.context.active_object
    archi.scale = (2.0, 0.55, 0.28)
    archi.data.materials.append(p["marble"])
    objs.append(archi)

    # Broken end of architrave (angled chunk hanging)
    bpy.ops.mesh.primitive_cube_add(size=0.6, location=(0.55, 0, 3.55))
    archi_break = bpy.context.active_object
    archi_break.scale = (0.8, 0.55, 0.25)
    archi_break.rotation_euler = (0, math.radians(12), math.radians(-5))
    archi_break.data.materials.append(p["marble_aged"])
    objs.append(archi_break)

    # -- Triglyphs / Doric frieze detail (simple rectangular blocks on the architrave) --
    for ti in range(5):
        tx = -1.4 + ti * 0.55
        bpy.ops.mesh.primitive_cube_add(size=0.22, location=(tx, -0.28, 3.95))
        triglyph = bpy.context.active_object
        triglyph.scale = (1.0, 0.15, 1.4)
        triglyph.data.materials.append(p["marble"])
        objs.append(triglyph)

    # -- Triangular Pediment (for the two standing columns) --
    bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=1.3, depth=0.55,
                                    location=(-0.75, 0, 4.35))
    pediment = bpy.context.active_object
    pediment.rotation_euler = (math.radians(90), 0, math.radians(90))
    pediment.data.materials.append(p["marble"])
    objs.append(pediment)

    # -- Brass ornamental acroterion on pediment apex --
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(-0.75, 0, 4.70))
    acr = bpy.context.active_object
    acr.data.materials.append(p["brass"])
    smooth_object(acr)
    objs.append(acr)

    # -- Scattered stone debris on the ground --
    debris_positions = [
        (2.0, 0.8, 0.12, 0.15), (1.8, -0.7, 0.10, 0.12),
        (-2.1, 0.5, 0.11, 0.18), (-1.8, -0.8, 0.09, 0.10),
        (0.5, 0.9, 0.08, 0.08), (-0.3, -1.0, 0.10, 0.14),
    ]
    for dx, dy, dz, ds in debris_positions:
        bpy.ops.mesh.primitive_cube_add(size=ds * 2, location=(dx, dy, dz))
        deb = bpy.context.active_object
        deb.rotation_euler = (math.radians(dx * 15), math.radians(dy * 12), math.radians(ds * 200))
        deb.data.materials.append(p["travertine"])
        objs.append(deb)

    # -- Lichen Patches on marble surfaces --
    lichen_spots = [
        (-1.5, 0.30, 1.8, "lichen_orange"), (0.0, -0.30, 2.5, "lichen_grey"),
        (1.5, 0.20, 0.65, "lichen_orange"), (-0.75, 0.28, 3.88, "lichen_grey"),
    ]
    for lx, ly, lz, lmat in lichen_spots:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.10, location=(lx, ly, lz))
        lich = bpy.context.active_object
        lich.scale = (1.5, 1.2, 0.08)
        lich.data.materials.append(p[lmat])
        smooth_object(lich)
        objs.append(lich)

    # -- Moss in crevices / at column bases --
    _add_moss_patch(objs, p["moss"], -1.5, 0.0, 0.48, radius=0.20)
    _add_moss_patch(objs, p["moss"], 0.0, 0.0, 0.48, radius=0.18)
    _add_moss_patch(objs, p["moss"], 1.5, 0.0, 0.48, radius=0.22)

    # -- Chrysanthemums clustering at the base --
    for fi in range(10):
        fa = fi * 0.62 + 0.2
        fx = math.cos(fa) * (1.2 + fi * 0.12) + (fi % 3 - 1) * 0.3
        fy = math.sin(fa) * 0.6
        fz = 0.20
        _add_chrysanthemum(objs, p["chrysanthemum"], fx, fy, fz, scale=0.14)

    # -- Peonies in fallen column area --
    _add_peony(objs, p["peony"], 1.8, 0.3, 0.22, scale=0.16)
    _add_peony(objs, p["peony_pale"], 2.0, -0.4, 0.20, scale=0.14)
    _add_peony(objs, p["peony"], 1.4, -0.5, 0.18, scale=0.18)

    # -- Ivy climbing the left column --
    _add_ivy_trail(objs, p["ivy"], -1.5, 0.0, 0.50, steps=16, radius=0.32, climb=0.17)

    # -- Grass tufts in cracks --
    _add_grass_tuft(objs, p["grass"], -0.5, 0.8, 0.12)
    _add_grass_tuft(objs, p["grass"], 0.8, -0.7, 0.12)
    _add_grass_tuft(objs, p["grass"], 2.2, 0.0, 0.12)

    export_and_render(objs, "ruin_doric_temple_facade", "ruin_doric_temple_facade_render")


# ==============================================================================
# 5. RUIN: BROKEN AMPHITHEATER SEATING (CAVEA)
#    Curved semicircular tiered stone seating, partially collapsed on one side,
#    with grass, flowers, and moss growing between the worn blocks.
# ==============================================================================

def build_amphitheater():
    clear_scene()
    setup_camera_and_lighting(target_z=1.8, ortho_scale=8.0)
    p = palette()
    objs = []

    # -- Ground plane / orchestra floor (semicircular stone floor) --
    bpy.ops.mesh.primitive_cylinder_add(radius=2.0, depth=0.12, vertices=32, location=(0, 0, 0.06))
    floor = bpy.context.active_object
    floor.scale = (1.0, 0.6, 1.0)  # Half-circle effect via visual framing
    floor.data.materials.append(p["flagstone"])
    smooth_object(floor)
    objs.append(floor)

    # -- Brass / stone decorative ring on orchestra edge --
    bpy.ops.mesh.primitive_torus_add(major_radius=2.0, minor_radius=0.06,
                                     major_segments=32, minor_segments=10,
                                     location=(0, 0, 0.15))
    orch_ring = bpy.context.active_object
    orch_ring.scale = (1.0, 0.6, 1.0)
    orch_ring.data.materials.append(p["brass"])
    smooth_object(orch_ring)
    objs.append(orch_ring)

    # -- Tiered Semicircular Seating (5 tiers, curving around the back) --
    tiers = 5
    for tier in range(tiers):
        tier_radius = 2.4 + tier * 0.55
        tier_z = 0.22 + tier * 0.35
        seat_height = 0.30
        seat_depth = 0.45

        # Each tier is a series of stone blocks arranged in an arc
        blocks_in_tier = 10 + tier * 2
        arc_start = math.radians(160)  # Semicircle range
        arc_end = math.radians(380)
        arc_span = arc_end - arc_start

        for bi in range(blocks_in_tier):
            ba = arc_start + (bi / (blocks_in_tier - 1)) * arc_span
            bx = math.cos(ba) * tier_radius
            by = math.sin(ba) * tier_radius * 0.6  # squish for iso perspective
            bz = tier_z

            # Skip some blocks on the right side (tier 3+) to show collapse
            is_damaged = (tier >= 3 and bi > blocks_in_tier * 0.7)
            if is_damaged and bi % 2 == 0:
                # Fallen block on the ground instead
                bpy.ops.mesh.primitive_cube_add(size=0.38, location=(bx + 0.3, by - 0.2, 0.15))
                fallen = bpy.context.active_object
                fallen.rotation_euler = (math.radians(12), math.radians(-18), math.radians(ba * 57))
                fallen.data.materials.append(p["travertine"])
                objs.append(fallen)
                continue

            bpy.ops.mesh.primitive_cube_add(size=0.40, location=(bx, by, bz))
            block = bpy.context.active_object
            block.scale = (1.0, 0.85, 0.75)
            # Slight random rotation for organic look
            block.rotation_euler = (0, 0, ba + math.radians(90))
            mat_choice = p["marble"] if (tier + bi) % 3 != 0 else p["marble_aged"]
            block.data.materials.append(mat_choice)
            objs.append(block)

            # Grass tuft between every few blocks
            if bi % 4 == 2 and tier < 4:
                _add_grass_tuft(objs, p["grass"], bx, by, bz + 0.18, blades=3, height=0.25)

    # -- Collapsed section rubble pile (right side) --
    rubble_positions = [
        (2.8, -1.0, 0.12), (3.0, -0.6, 0.10), (2.5, -1.3, 0.14),
        (3.2, -0.9, 0.08), (2.7, -0.3, 0.11),
    ]
    for rx, ry, rz in rubble_positions:
        size = 0.25 + abs(rx) * 0.04
        bpy.ops.mesh.primitive_cube_add(size=size, location=(rx, ry, rz))
        rub = bpy.context.active_object
        rub.rotation_euler = (math.radians(rx * 8), math.radians(ry * 12), math.radians(rz * 200))
        rub.data.materials.append(p["travertine"])
        objs.append(rub)

    # -- Flowers growing in the tiers --
    flower_spots = [
        (-1.8, 0.8, 0.55), (-0.5, 1.6, 0.90), (0.8, 1.8, 1.20),
        (-2.2, 0.2, 0.55), (0.0, 2.0, 1.55), (-1.2, 1.5, 0.90),
    ]
    for fi, (fx, fy, fz) in enumerate(flower_spots):
        if fi % 2 == 0:
            _add_chrysanthemum(objs, p["chrysanthemum"], fx, fy, fz, scale=0.13)
        else:
            _add_peony(objs, p["peony"], fx, fy, fz, scale=0.14)

    # -- Moss patches on older tiers --
    _add_moss_patch(objs, p["moss"], -2.0, 1.0, 0.52, radius=0.25)
    _add_moss_patch(objs, p["moss"], 1.5, 1.2, 0.85, radius=0.20)
    _add_moss_patch(objs, p["moss"], 0.0, 1.8, 1.20, radius=0.18)

    # -- Lichen weathering --
    for lx, ly, lz in [(2.0, 0.5, 0.50), (-1.5, 1.8, 1.15), (0.5, 2.2, 1.50)]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(lx, ly, lz))
        lich = bpy.context.active_object
        lich.scale = (1.8, 1.4, 0.10)
        lich.data.materials.append(p["lichen_orange"])
        smooth_object(lich)
        objs.append(lich)

    # -- Ivy trail climbing up the back tier --
    _add_ivy_trail(objs, p["ivy"], -1.0, 1.8, 0.50, steps=10, radius=0.20, climb=0.15)

    export_and_render(objs, "ruin_amphitheater_seats", "ruin_amphitheater_seats_render")


# ==============================================================================
# 6. RUIN: RUBBLE SCATTER KIT (Modular Debris Pieces)
#    Fallen column drums, carved frieze fragments, broken pediment chunks,
#    loose ashlar blocks — with moss and flowers for dressing.
#    Arranged as a single scene for render, but designed modular.
# ==============================================================================

def build_rubble_kit():
    clear_scene()
    setup_camera_and_lighting(target_z=0.8, ortho_scale=6.5)
    p = palette()
    objs = []

    # -- Ground plane (cracked marble pavers) --
    bpy.ops.mesh.primitive_cube_add(size=5.5, location=(0, 0, 0.05))
    ground = bpy.context.active_object
    ground.scale = (1.0, 1.0, 0.02)
    ground.data.materials.append(p["flagstone"])
    objs.append(ground)

    # Paver grid lines (inlaid brass — Aegis Flora signature)
    for gx in [-2.0, -1.0, 0.0, 1.0, 2.0]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(gx, 0, 0.07))
        line = bpy.context.active_object
        line.scale = (0.02, 2.5, 0.01)
        line.data.materials.append(p["brass"])
        objs.append(line)
    for gy in [-2.0, -1.0, 0.0, 1.0, 2.0]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, gy, 0.07))
        line = bpy.context.active_object
        line.scale = (2.5, 0.02, 0.01)
        line.data.materials.append(p["brass"])
        objs.append(line)

    # -- PIECE A: Large Fallen Column Drum --
    bpy.ops.mesh.primitive_cylinder_add(radius=0.35, depth=0.85, vertices=20,
                                        location=(-1.2, 0.4, 0.28))
    drum_a = bpy.context.active_object
    drum_a.rotation_euler = (math.radians(88), 0, math.radians(22))
    drum_a.data.materials.append(p["marble"])
    smooth_object(drum_a)
    objs.append(drum_a)

    # Brass drum clamp ring
    bpy.ops.mesh.primitive_torus_add(major_radius=0.37, minor_radius=0.03,
                                     major_segments=20, minor_segments=8,
                                     location=(-1.2, 0.15, 0.28))
    clamp_a = bpy.context.active_object
    clamp_a.rotation_euler = (math.radians(88), 0, math.radians(22))
    clamp_a.data.materials.append(p["brass"])
    smooth_object(clamp_a)
    objs.append(clamp_a)

    # -- PIECE B: Smaller Column Drum --
    bpy.ops.mesh.primitive_cylinder_add(radius=0.28, depth=0.60, vertices=18,
                                        location=(1.0, -0.8, 0.22))
    drum_b = bpy.context.active_object
    drum_b.rotation_euler = (math.radians(85), math.radians(10), math.radians(-35))
    drum_b.data.materials.append(p["marble_aged"])
    smooth_object(drum_b)
    objs.append(drum_b)

    # -- PIECE C: Carved Frieze Fragment (rectangular relief slab) --
    bpy.ops.mesh.primitive_cube_add(size=0.8, location=(0.8, 0.9, 0.22))
    frieze = bpy.context.active_object
    frieze.scale = (1.5, 0.3, 0.6)
    frieze.rotation_euler = (math.radians(5), math.radians(-8), math.radians(15))
    frieze.data.materials.append(p["marble"])
    objs.append(frieze)

    # Relief detail (raised decorative strip)
    bpy.ops.mesh.primitive_cube_add(size=0.6, location=(0.8, 0.78, 0.32))
    relief = bpy.context.active_object
    relief.scale = (1.4, 0.05, 0.35)
    relief.rotation_euler = (math.radians(5), math.radians(-8), math.radians(15))
    relief.data.materials.append(p["travertine"])
    objs.append(relief)

    # -- PIECE D: Broken Pediment Triangle Chunk --
    bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=0.7, depth=0.35,
                                    location=(-0.5, -1.0, 0.18))
    ped_chunk = bpy.context.active_object
    ped_chunk.rotation_euler = (math.radians(92), math.radians(12), math.radians(55))
    ped_chunk.data.materials.append(p["marble"])
    objs.append(ped_chunk)

    # -- PIECE E: Scattered Ashlar Blocks (rectangular cut stone) --
    ashlar_positions = [
        (0.2, 0.3, 0.12, 0.25), (-0.6, -0.4, 0.10, 0.20),
        (1.5, 0.2, 0.14, 0.28), (-1.6, -0.8, 0.09, 0.18),
        (0.5, -1.5, 0.11, 0.22), (-0.2, 1.5, 0.13, 0.24),
    ]
    for ax, ay, az, asize in ashlar_positions:
        bpy.ops.mesh.primitive_cube_add(size=asize, location=(ax, ay, az))
        ash = bpy.context.active_object
        ash.scale = (1.2, 0.8, 0.6)
        ash.rotation_euler = (math.radians(ax * 5), math.radians(ay * 8), math.radians(asize * 400))
        ash.data.materials.append(p["travertine"] if abs(ax) > 1 else p["marble_aged"])
        objs.append(ash)

    # -- PIECE F: Corinthian Capital Fragment (ornate cube + sphere ornament) --
    bpy.ops.mesh.primitive_cube_add(size=0.5, location=(-1.8, 0.8, 0.18))
    cap_frag = bpy.context.active_object
    cap_frag.rotation_euler = (math.radians(15), math.radians(-22), math.radians(38))
    cap_frag.data.materials.append(p["marble"])
    objs.append(cap_frag)

    # Acanthus leaf suggestion (small sphere ornaments)
    for leaf_i in range(4):
        la = leaf_i * (math.pi / 2) + 0.3
        lx = -1.8 + math.cos(la) * 0.28
        ly = 0.8 + math.sin(la) * 0.28
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(lx, ly, 0.38))
        acanthus = bpy.context.active_object
        acanthus.scale = (1.0, 0.6, 0.8)
        acanthus.data.materials.append(p["marble_aged"])
        smooth_object(acanthus)
        objs.append(acanthus)

    # -- VEGETATION DRESSING --

    # Chrysanthemums growing around/on debris
    chrys_spots = [
        (-0.9, 0.5, 0.18), (0.3, -0.8, 0.15), (1.3, 0.6, 0.16),
        (-1.5, -0.3, 0.14), (0.0, 1.2, 0.15), (-0.3, -1.3, 0.12),
    ]
    for cx, cy, cz in chrys_spots:
        _add_chrysanthemum(objs, p["chrysanthemum"], cx, cy, cz, scale=0.12)

    # Peonies near the larger pieces
    _add_peony(objs, p["peony"], -1.0, 0.65, 0.18, scale=0.14)
    _add_peony(objs, p["peony_pale"], 0.9, -0.6, 0.16, scale=0.12)

    # Moss on surfaces
    _add_moss_patch(objs, p["moss"], -1.2, 0.4, 0.52, radius=0.22)  # on top of drum A
    _add_moss_patch(objs, p["moss"], 0.8, 0.9, 0.45, radius=0.18)   # on frieze
    _add_moss_patch(objs, p["moss"], -0.5, -1.0, 0.30, radius=0.15) # on pediment chunk

    # Grass tufts in cracks
    _add_grass_tuft(objs, p["grass"], -0.4, 0.8, 0.08)
    _add_grass_tuft(objs, p["grass"], 1.0, -0.3, 0.08)
    _add_grass_tuft(objs, p["grass"], -1.5, -1.2, 0.08)
    _add_grass_tuft(objs, p["grass"], 0.5, 1.0, 0.08)

    # Ivy trail climbing over the large drum
    _add_ivy_trail(objs, p["ivy"], -1.2, 0.4, 0.10, steps=8, radius=0.38, climb=0.06)

    # Lichen weathering spots
    for lx, ly, lz in [(-1.1, 0.55, 0.40), (0.85, 0.82, 0.28), (1.05, -0.75, 0.30)]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.07, location=(lx, ly, lz))
        lich = bpy.context.active_object
        lich.scale = (1.5, 1.3, 0.10)
        lich.data.materials.append(p["lichen_orange"])
        smooth_object(lich)
        objs.append(lich)

    # Floating cyan mana spores (scattered energy signature)
    for si in range(5):
        sx = -1.5 + si * 0.75
        sy = 0.5 - si * 0.3
        sz = 0.6 + si * 0.15
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.04, location=(sx, sy, sz))
        spore = bpy.context.active_object
        spore.data.materials.append(p["spore_glow"])
        objs.append(spore)

    export_and_render(objs, "ruin_rubble_scatter_kit", "ruin_rubble_scatter_kit_render")


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("=" * 72)
    print("  AEGIS FLORA: Flower Bunches & Greek Ruins Asset Generator")
    print("=" * 72)

    print("\n[1/6] Building Hero Flower Bouquet...")
    build_hero_bouquet()

    print("\n[2/6] Building Hanging Floral Garland...")
    build_hanging_garland()

    print("\n[3/6] Building Overgrown Urn Planter...")
    build_overgrown_urn()

    print("\n[4/6] Building Doric Temple Façade...")
    build_doric_temple()

    print("\n[5/6] Building Amphitheater Seating...")
    build_amphitheater()

    print("\n[6/6] Building Rubble Scatter Kit...")
    build_rubble_kit()

    print("\n" + "=" * 72)
    print("  ALL 6 FLOWER & RUIN ASSETS GENERATED SUCCESSFULLY")
    print("=" * 72)
