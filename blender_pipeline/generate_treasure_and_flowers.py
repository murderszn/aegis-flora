"""
Aegis Flora: High-Fidelity 3D Treasure, Relics & Hero Floral Assets Generator
Generates GLTF (.glb) models and isometric PNG renders using Blender 5.1
1. prop_treasure_chest: Steampunk/Greco-Roman strongbox with brass brackets, open lid, spilling gold coins & cyan mana crystals.
2. prop_relic_urn: Classical Greco-Roman amphora/urn with gold filigree, overflowing with gold coins, gems & trailing wisteria.
3. flora_clockwork_lotus: Multi-tiered blooming lotus with pink petals, brass stamens, cyan mana core, in a marble basin.
4. flora_golden_chrysanthemum: Radiating golden chrysanthemum in an ornate brass planter with emerald leaves.
"""

import bpy
import math
import os

OUTPUT_MODELS_DIR = "/Users/jahflyx/towers/blender_pipeline/models"
OUTPUT_RENDERS_DIR = "/Users/jahflyx/towers/blender_pipeline/renders"
os.makedirs(OUTPUT_MODELS_DIR, exist_ok=True)
os.makedirs(OUTPUT_RENDERS_DIR, exist_ok=True)

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes: bpy.data.meshes.remove(block)
    for block in bpy.data.materials: bpy.data.materials.remove(block)
    for block in bpy.data.lights: bpy.data.lights.remove(block)
    for block in bpy.data.cameras: bpy.data.cameras.remove(block)

def create_pbr_material(name, base_color, metallic=0.0, roughness=0.5, emissive=(0,0,0,1), emissive_strength=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = base_color
        bsdf.inputs['Metallic'].default_value = metallic
        bsdf.inputs['Roughness'].default_value = roughness
        if 'Emission Color' in bsdf.inputs:
            bsdf.inputs['Emission Color'].default_value = emissive
            bsdf.inputs['Emission Strength'].default_value = emissive_strength
        elif 'Emission' in bsdf.inputs:
            bsdf.inputs['Emission'].default_value = emissive
    return mat

def setup_studio_lighting(target_z=1.0, ortho_scale=5.2):
    sun_data = bpy.data.lights.new(name="KeySun", type='SUN')
    sun_data.energy = 3.6
    sun_data.color = (1.0, 0.95, 0.85)
    sun_obj = bpy.data.objects.new(name="KeySun", object_data=sun_data)
    bpy.context.collection.objects.link(sun_obj)
    sun_obj.rotation_euler = (math.radians(52), math.radians(18), math.radians(45))

    fill_data = bpy.data.lights.new(name="FillLight", type='SUN')
    fill_data.energy = 1.3
    fill_data.color = (0.28, 0.48, 0.58)
    fill_obj = bpy.data.objects.new(name="FillLight", object_data=fill_data)
    bpy.context.collection.objects.link(fill_obj)
    fill_obj.rotation_euler = (math.radians(45), math.radians(-30), math.radians(-135))

    rim_data = bpy.data.lights.new(name="RimLight", type='POINT')
    rim_data.energy = 550.0
    rim_data.color = (1.0, 0.68, 0.28)
    rim_obj = bpy.data.objects.new(name="RimLight", object_data=rim_data)
    bpy.context.collection.objects.link(rim_obj)
    rim_obj.location = (-4.0, -3.5, target_z + 3.5)

    cam_data = bpy.data.cameras.new(name="IsoCamera")
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = ortho_scale
    cam_obj = bpy.data.objects.new(name="IsoCamera", object_data=cam_data)
    bpy.context.collection.objects.link(cam_obj)
    
    # Position camera looking directly at (0, 0, target_z)
    cam_obj.location = (7.0, -7.0, target_z + 5.715)
    cam_obj.rotation_euler = (math.radians(54.736), 0, math.radians(45))
    bpy.context.scene.camera = cam_obj

def setup_render_engine():
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'

def export_asset(name):
    glb_path = os.path.join(OUTPUT_MODELS_DIR, f"{name}.glb")
    render_path = os.path.join(OUTPUT_RENDERS_DIR, f"{name}_render.png")
    bpy.ops.export_scene.gltf(filepath=glb_path, export_format='GLB', use_selection=False)
    bpy.context.scene.render.filepath = render_path
    bpy.ops.render.render(write_still=True)
    print(f"Asset finished: {glb_path} and {render_path}")

# ==============================================================================
# 1. PROP: TREASURE CHEST / RELIQUARY STRONGBOX
# ==============================================================================
def build_treasure_chest():
    clear_scene()
    setup_render_engine()
    setup_studio_lighting(target_z=0.6, ortho_scale=4.2)

    m_iron = create_pbr_material("CastIron", (0.12, 0.14, 0.16, 1.0), metallic=0.88, roughness=0.45)
    m_brass = create_pbr_material("AntiqueBrass", (0.85, 0.68, 0.22, 1.0), metallic=0.92, roughness=0.25)
    m_wood = create_pbr_material("PolishedTeak", (0.32, 0.18, 0.09, 1.0), metallic=0.05, roughness=0.35)
    m_gold = create_pbr_material("GoldCoins", (0.96, 0.78, 0.18, 1.0), metallic=0.95, roughness=0.2)
    m_mana = create_pbr_material("ManaCrystal", (0.0, 0.96, 0.83, 1.0), metallic=0.1, roughness=0.15,
                                 emissive=(0.0, 0.96, 0.83, 1.0), emissive_strength=3.8)
    m_ruby = create_pbr_material("RubyGem", (0.92, 0.1, 0.25, 1.0), metallic=0.2, roughness=0.1,
                                 emissive=(0.92, 0.1, 0.25, 1.0), emissive_strength=2.5)

    # 1. Low Flagstone Plinth Base
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.06))
    plinth = bpy.context.active_object
    plinth.scale = (2.2, 1.8, 0.12)
    m_stone = create_pbr_material("AgedStone", (0.82, 0.8, 0.75, 1.0), roughness=0.65)
    plinth.data.materials.append(m_stone)

    # 2. Main Chest Body Box
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.42))
    base = bpy.context.active_object
    base.scale = (1.5, 0.95, 0.6)
    base.data.materials.append(m_wood)

    # Iron bottom & top perimeter trim
    for bz in [0.14, 0.7]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, bz))
        rim = bpy.context.active_object
        rim.scale = (1.54, 0.99, 0.06)
        rim.data.materials.append(m_iron)

    # 4 Brass Corner Reinforcement Brackets
    for cx in [-0.74, 0.74]:
        for cy in [-0.46, 0.46]:
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cx, cy, 0.42))
            post = bpy.context.active_object
            post.scale = (0.08, 0.08, 0.64)
            post.data.materials.append(m_brass)

    # 2 Vertical Brass Girdle Straps
    for sx in [-0.42, 0.42]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sx, 0, 0.42))
        strap = bpy.context.active_object
        strap.scale = (0.1, 0.98, 0.62)
        strap.data.materials.append(m_brass)

    # Keyhole Escutcheon Plate on Front
    bpy.ops.mesh.primitive_cylinder_add(radius=0.14, depth=0.04, location=(0, -0.49, 0.46))
    lock = bpy.context.active_object
    lock.rotation_euler = (math.radians(90), 0, 0)
    lock.data.materials.append(m_brass)

    # 3. Open Arched Lid (Pivoting from rear hinge at y = 0.45, z = 0.72)
    # Tilted back at 55 degrees
    lid_tilt = math.radians(-50)
    lid_pivot_y = 0.45
    lid_pivot_z = 0.72

    bpy.ops.mesh.primitive_cylinder_add(radius=0.48, depth=1.52, location=(0, 0.45, 0.72))
    lid = bpy.context.active_object
    lid.scale = (0.5, 1.0, 1.0)
    lid.rotation_euler = (lid_tilt, 0, math.radians(90))
    lid.location = (0, 0.48, 1.02)
    lid.data.materials.append(m_wood)

    # Lid Brass Ribs
    for lsx in [-0.42, 0.42]:
        bpy.ops.mesh.primitive_torus_add(major_segments=24, minor_segments=8, major_radius=0.5, minor_radius=0.035, location=(lsx, 0.48, 1.02))
        lband = bpy.context.active_object
        lband.scale = (0.5, 1.0, 1.0)
        lband.rotation_euler = (lid_tilt, 0, math.radians(90))
        lband.data.materials.append(m_brass)

    # 4. Overflowing Loot Heap: Gold Coins, Scrap Gears, Mana Crystals
    # Dense coin bed inside
    for ix in [-0.45, -0.2, 0.1, 0.4]:
        for iy in [-0.2, 0.0, 0.15]:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.16, location=(ix + iy*0.1, iy, 0.62 + abs(ix)*0.04))
            coin_mound = bpy.context.active_object
            coin_mound.data.materials.append(m_gold)

    # Loose gold coins spilling over the front lip onto the plinth
    spill_coords = [
        (0.15, -0.45, 0.65), (-0.1, -0.47, 0.62), (0.35, -0.46, 0.6),
        (0.2, -0.62, 0.14), (-0.25, -0.58, 0.14), (0.45, -0.55, 0.14),
        (0.0, -0.68, 0.14), (-0.45, -0.52, 0.14), (0.55, -0.65, 0.14),
        (0.28, -0.75, 0.14), (-0.18, -0.74, 0.14)
    ]
    for c_i, (px, py, pz) in enumerate(spill_coords):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.025, location=(px, py, pz))
        coin = bpy.context.active_object
        coin.rotation_euler = (math.radians(12 * (c_i % 3)), math.radians(18 * (c_i % 2)), math.radians(c_i * 35))
        coin.data.materials.append(m_gold)

    # Spilled Clockwork Gears
    for gx, gy, gz, rot in [(-0.35, -0.62, 0.15, 25), (0.42, -0.68, 0.15, -35)]:
        bpy.ops.mesh.primitive_torus_add(major_segments=16, minor_segments=6, major_radius=0.16, minor_radius=0.035, location=(gx, gy, gz))
        gear = bpy.context.active_object
        gear.rotation_euler = (math.radians(20), math.radians(rot), 0)
        gear.data.materials.append(m_brass)

    # Radiant Cyan Mana Crystals clustered in the treasure bed
    crystal_coords = [
        (0.22, 0.05, 0.82, 25, 15, 30),
        (-0.28, -0.08, 0.78, -20, 20, 45),
        (0.0, 0.12, 0.88, 10, -25, 10),
        (-0.12, -0.02, 0.84, -15, -15, 60),
        (0.38, -0.08, 0.76, 30, 10, -20)
    ]
    for cx, cy, cz, rx, ry, rz in crystal_coords:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.075, depth=0.34, location=(cx, cy, cz))
        crys = bpy.context.active_object
        crys.rotation_euler = (math.radians(rx), math.radians(ry), math.radians(rz))
        crys.data.materials.append(m_mana)

    # Faceted Ruby Gemstones
    for rx, ry, rz in [(-0.02, -0.22, 0.72), (0.28, -0.2, 0.7)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.2, location=(rx, ry, rz))
        ruby = bpy.context.active_object
        ruby.rotation_euler = (math.radians(35), math.radians(-20), math.radians(40))
        ruby.data.materials.append(m_ruby)

    # Internal Chest Glow
    c_light = bpy.data.lights.new(name="ChestManaGlow", type='POINT')
    c_light.energy = 90.0
    c_light.color = (0.0, 0.96, 0.83)
    c_light_obj = bpy.data.objects.new(name="ChestManaGlow", object_data=c_light)
    bpy.context.collection.objects.link(c_light_obj)
    c_light_obj.location = (0, 0, 0.8)

    export_asset("prop_treasure_chest")

# ==============================================================================
# 2. PROP: ANCIENT GRECO-ROMAN RELIC URN / AMPHORA OF AMBROSIA
# ==============================================================================
def build_relic_urn():
    clear_scene()
    setup_render_engine()
    setup_studio_lighting(target_z=1.35, ortho_scale=4.6)

    m_marble = create_pbr_material("TravertineMarble", (0.88, 0.85, 0.78, 1.0), metallic=0.04, roughness=0.38)
    m_brass = create_pbr_material("InlaidGoldFiligree", (0.92, 0.75, 0.22, 1.0), metallic=0.92, roughness=0.22)
    m_gold = create_pbr_material("GoldCoins", (0.96, 0.78, 0.18, 1.0), metallic=0.95, roughness=0.2)
    m_wisteria = create_pbr_material("WisteriaBlooms", (0.68, 0.45, 0.82, 1.0), metallic=0.0, roughness=0.45,
                                     emissive=(0.5, 0.3, 0.7, 1.0), emissive_strength=0.8)
    m_mana = create_pbr_material("ManaGlow", (0.0, 0.96, 0.83, 1.0), metallic=0.1, roughness=0.1,
                                 emissive=(0.0, 0.96, 0.83, 1.0), emissive_strength=3.5)

    # 1. Stepped Plinth Base
    bpy.ops.mesh.primitive_cylinder_add(radius=0.72, depth=0.16, location=(0, 0, 0.08))
    p1 = bpy.context.active_object
    p1.data.materials.append(m_marble)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.55, depth=0.12, location=(0, 0, 0.22))
    p2 = bpy.context.active_object
    p2.data.materials.append(m_brass)

    # 2. Urn Stem & Swelling Ovoid Body
    bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.3, location=(0, 0, 0.43))
    stem = bpy.context.active_object
    stem.data.materials.append(m_marble)

    # Lower body cone
    bpy.ops.mesh.primitive_cone_add(radius1=0.25, radius2=0.78, depth=0.65, location=(0, 0, 0.88))
    body_low = bpy.context.active_object
    body_low.data.materials.append(m_marble)

    # Mid body sphere
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.8, location=(0, 0, 1.32))
    body_mid = bpy.context.active_object
    body_mid.scale = (1.0, 1.0, 0.85)
    body_mid.data.materials.append(m_marble)

    # Brass decorative relief girdle ring
    bpy.ops.mesh.primitive_torus_add(major_segments=32, minor_segments=12, major_radius=0.8, minor_radius=0.055, location=(0, 0, 1.32))
    girdle = bpy.context.active_object
    girdle.data.materials.append(m_brass)

    # Upper shoulder & fluted neck
    bpy.ops.mesh.primitive_cone_add(radius1=0.75, radius2=0.38, depth=0.52, location=(0, 0, 1.76))
    shoulder = bpy.context.active_object
    shoulder.data.materials.append(m_marble)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.38, depth=0.45, location=(0, 0, 2.15))
    neck = bpy.context.active_object
    neck.data.materials.append(m_marble)

    # Flaring rim lip
    bpy.ops.mesh.primitive_torus_add(major_segments=32, minor_segments=12, major_radius=0.46, minor_radius=0.07, location=(0, 0, 2.38))
    rim = bpy.context.active_object
    rim.data.materials.append(m_brass)

    # 3. Twin High Looped Scroll Handles
    for hx in [-1, 1]:
        bpy.ops.mesh.primitive_torus_add(major_segments=24, minor_segments=8, major_radius=0.36, minor_radius=0.05, location=(hx * 0.68, 0, 1.95))
        handle = bpy.context.active_object
        handle.scale = (0.5, 1.0, 1.4)
        handle.rotation_euler = (math.radians(90), 0, 0)
        handle.data.materials.append(m_brass)

    # 4. Spilling Gold & Mana Ambrosia from the Top
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.38, location=(0, 0, 2.42))
    gold_top = bpy.context.active_object
    gold_top.scale = (1.0, 1.0, 0.45)
    gold_top.data.materials.append(m_gold)

    # Mana crystal protruding from top
    bpy.ops.mesh.primitive_cylinder_add(radius=0.09, depth=0.4, location=(0.06, 0.04, 2.65))
    top_crys = bpy.context.active_object
    top_crys.rotation_euler = (math.radians(15), math.radians(-10), math.radians(20))
    top_crys.data.materials.append(m_mana)

    # Spilling gold coins dripping down the handle and rim
    for i, (cx, cy, cz) in enumerate([
        (0.32, -0.15, 2.25), (0.38, -0.22, 2.05), (0.46, -0.22, 1.8), (0.52, -0.18, 1.55),
        (0.5, -0.1, 0.1), (0.62, 0.12, 0.04), (0.58, -0.26, 0.03), (0.35, 0.4, 0.02)
    ]):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.075, depth=0.025, location=(cx, cy, cz))
        c = bpy.context.active_object
        c.rotation_euler = (math.radians(25 + i*10), math.radians(15 * i), math.radians(40 * i))
        c.data.materials.append(m_gold)

    # 5. Trailing Wisteria Blooms draping around the urn body
    for vi in range(7):
        va = vi * (math.pi / 3.5) + 0.3
        vx = math.cos(va) * 0.65
        vy = math.sin(va) * 0.65
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.13, location=(vx, vy, 0.4 + vi*0.14))
        bloom = bpy.context.active_object
        bloom.scale = (1.0, 1.0, 1.4)
        bloom.data.materials.append(m_wisteria)

    # Glowing mana nectar point light
    urn_light = bpy.data.lights.new(name="UrnManaLight", type='POINT')
    urn_light.energy = 85.0
    urn_light.color = (0.0, 0.96, 0.83)
    urn_light_obj = bpy.data.objects.new(name="UrnManaLight", object_data=urn_light)
    bpy.context.collection.objects.link(urn_light_obj)
    urn_light_obj.location = (0, 0, 2.7)

    export_asset("prop_relic_urn")

# ==============================================================================
# 3. FLORA: HERO CLOCKWORK LOTUS BLOOM
# ==============================================================================
def build_clockwork_lotus():
    clear_scene()
    setup_render_engine()
    setup_studio_lighting(target_z=0.7, ortho_scale=4.2)

    m_marble = create_pbr_material("CarvedMarbleBasin", (0.92, 0.9, 0.85, 1.0), metallic=0.04, roughness=0.3)
    m_brass = create_pbr_material("FiligreeBrass", (0.88, 0.72, 0.22, 1.0), metallic=0.92, roughness=0.22)
    m_petal_outer = create_pbr_material("PetalRose", (0.92, 0.45, 0.58, 1.0), metallic=0.0, roughness=0.35,
                                        emissive=(0.85, 0.35, 0.48, 1.0), emissive_strength=0.25)
    m_petal_inner = create_pbr_material("PetalPalePink", (0.98, 0.78, 0.85, 1.0), metallic=0.0, roughness=0.3,
                                        emissive=(0.95, 0.7, 0.8, 1.0), emissive_strength=0.3)
    m_stamen_gold = create_pbr_material("GoldStamen", (1.0, 0.82, 0.2, 1.0), metallic=0.85, roughness=0.25)
    m_mana_core = create_pbr_material("ManaStamenCore", (0.0, 0.98, 0.88, 1.0), metallic=0.1, roughness=0.1,
                                     emissive=(0.0, 0.98, 0.88, 1.0), emissive_strength=4.0)
    m_water = create_pbr_material("BasinWater", (0.1, 0.35, 0.45, 0.8), metallic=0.1, roughness=0.05)

    # 1. Classical Scalloped Marble Basin
    bpy.ops.mesh.primitive_cylinder_add(radius=1.35, depth=0.28, location=(0, 0, 0.14))
    basin_base = bpy.context.active_object
    basin_base.data.materials.append(m_marble)

    bpy.ops.mesh.primitive_torus_add(major_segments=32, minor_segments=12, major_radius=1.32, minor_radius=0.12, location=(0, 0, 0.26))
    basin_rim = bpy.context.active_object
    basin_rim.data.materials.append(m_brass)

    # Water surface in basin
    bpy.ops.mesh.primitive_cylinder_add(radius=1.22, depth=0.04, location=(0, 0, 0.26))
    water = bpy.context.active_object
    water.data.materials.append(m_water)

    # 2. Tier 1: Outer Flaring Petals (8 large flaring petals)
    for i in range(8):
        ang = i * (math.pi / 4)
        px = math.cos(ang) * 0.72
        py = math.sin(ang) * 0.72
        bpy.ops.mesh.primitive_cylinder_add(radius=0.32, depth=0.85, location=(px, py, 0.58))
        petal = bpy.context.active_object
        petal.scale = (0.55, 0.12, 1.0)
        petal.rotation_euler = (math.radians(35) * math.sin(ang), -math.radians(35) * math.cos(ang), ang + math.pi/2)
        petal.data.materials.append(m_petal_outer)

    # 3. Tier 2: Mid Blooming Petals (8 petals offset by 22.5 deg, more upright)
    for i in range(8):
        ang = i * (math.pi / 4) + (math.pi / 8)
        px = math.cos(ang) * 0.52
        py = math.sin(ang) * 0.52
        bpy.ops.mesh.primitive_cylinder_add(radius=0.28, depth=0.8, location=(px, py, 0.78))
        petal = bpy.context.active_object
        petal.scale = (0.5, 0.12, 1.0)
        petal.rotation_euler = (math.radians(22) * math.sin(ang), -math.radians(22) * math.cos(ang), ang + math.pi/2)
        petal.data.materials.append(m_petal_inner)

    # 4. Tier 3: Inner Cup Petals (6 upright cupped petals)
    for i in range(6):
        ang = i * (math.pi / 3)
        px = math.cos(ang) * 0.32
        py = math.sin(ang) * 0.32
        bpy.ops.mesh.primitive_cylinder_add(radius=0.24, depth=0.72, location=(px, py, 0.95))
        petal = bpy.context.active_object
        petal.scale = (0.45, 0.1, 1.0)
        petal.rotation_euler = (math.radians(10) * math.sin(ang), -math.radians(10) * math.cos(ang), ang + math.pi/2)
        petal.data.materials.append(m_petal_inner)

    # 5. Center Receptacle: Filigree Brass Gear & Stamens
    bpy.ops.mesh.primitive_cylinder_add(radius=0.28, depth=0.18, location=(0, 0, 0.88))
    receptacle = bpy.context.active_object
    receptacle.data.materials.append(m_brass)

    # Filigree Stamens Ring
    for s in range(16):
        sa = s * (math.pi / 8)
        sx = math.cos(sa) * 0.22
        sy = math.sin(sa) * 0.22
        bpy.ops.mesh.primitive_cylinder_add(radius=0.018, depth=0.28, location=(sx, sy, 1.05))
        stamen = bpy.context.active_object
        stamen.rotation_euler = (math.radians(15) * math.sin(sa), -math.radians(15) * math.cos(sa), 0)
        stamen.data.materials.append(m_stamen_gold)

    # Glowing Cyan Mana Heart Seed
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(0, 0, 1.1))
    mana_seed = bpy.context.active_object
    mana_seed.scale = (1.0, 1.0, 1.4)
    mana_seed.data.materials.append(m_mana_core)

    # Lotus Glow Light
    lotus_light = bpy.data.lights.new(name="LotusGlow", type='POINT')
    lotus_light.energy = 95.0
    lotus_light.color = (0.0, 0.98, 0.88)
    lotus_light_obj = bpy.data.objects.new(name="LotusGlow", object_data=lotus_light)
    bpy.context.collection.objects.link(lotus_light_obj)
    lotus_light_obj.location = (0, 0, 1.3)

    export_asset("flora_clockwork_lotus")

# ==============================================================================
# 4. FLORA: HERO GOLDEN CHRYSANTHEMUM IN BRASS PLANTER
# ==============================================================================
def build_golden_chrysanthemum():
    clear_scene()
    setup_render_engine()
    setup_studio_lighting(target_z=1.35, ortho_scale=4.6)

    m_brass = create_pbr_material("EngravedBrassPlanter", (0.86, 0.68, 0.22, 1.0), metallic=0.92, roughness=0.25)
    m_marble = create_pbr_material("PlinthMarble", (0.88, 0.86, 0.8, 1.0), metallic=0.04, roughness=0.35)
    m_gold_petal = create_pbr_material("ChrysanthemumGold", (0.96, 0.72, 0.18, 1.0), metallic=0.05, roughness=0.3,
                                       emissive=(0.92, 0.62, 0.12, 1.0), emissive_strength=0.3)
    m_amber_petal = create_pbr_material("ChrysanthemumAmber", (0.92, 0.48, 0.14, 1.0), metallic=0.05, roughness=0.35,
                                        emissive=(0.85, 0.38, 0.1, 1.0), emissive_strength=0.25)
    m_leaf = create_pbr_material("SerratedLeaf", (0.14, 0.42, 0.22, 1.0), metallic=0.0, roughness=0.45)
    m_soil = create_pbr_material("RichSoil", (0.16, 0.12, 0.08, 1.0), metallic=0.0, roughness=0.9)

    # 1. Classical Square Plinth & Fluted Brass Planter Urn
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.12))
    plinth = bpy.context.active_object
    plinth.scale = (1.2, 1.2, 0.24)
    plinth.data.materials.append(m_marble)

    # Planter base cone
    bpy.ops.mesh.primitive_cone_add(radius1=0.62, radius2=0.38, depth=0.32, location=(0, 0, 0.38))
    urn_base = bpy.context.active_object
    urn_base.data.materials.append(m_brass)

    # Planter main body bowl
    bpy.ops.mesh.primitive_cylinder_add(radius=0.72, depth=0.5, location=(0, 0, 0.78))
    urn_body = bpy.context.active_object
    urn_body.data.materials.append(m_brass)

    # Planter rim ring
    bpy.ops.mesh.primitive_torus_add(major_segments=32, minor_segments=10, major_radius=0.76, minor_radius=0.07, location=(0, 0, 1.02))
    urn_rim = bpy.context.active_object
    urn_rim.data.materials.append(m_brass)

    # Soil top
    bpy.ops.mesh.primitive_cylinder_add(radius=0.68, depth=0.1, location=(0, 0, 0.98))
    soil = bpy.context.active_object
    soil.data.materials.append(m_soil)

    # 2. Main Central Stem & Foliage Leaves
    bpy.ops.mesh.primitive_cylinder_add(radius=0.055, depth=0.9, location=(0, 0, 1.45))
    stem = bpy.context.active_object
    stem.data.materials.append(m_leaf)

    # Serrated emerald leaves arching outwards
    for li in range(5):
        la = li * (2 * math.pi / 5) + 0.2
        lx = math.cos(la) * 0.38
        ly = math.sin(la) * 0.38
        bpy.ops.mesh.primitive_cylinder_add(radius=0.16, depth=0.58, location=(lx, ly, 1.32 + (li%2)*0.15))
        leaf = bpy.context.active_object
        leaf.scale = (0.45, 0.08, 1.0)
        leaf.rotation_euler = (math.radians(50) * math.sin(la), -math.radians(50) * math.cos(la), la + math.pi/2)
        leaf.data.materials.append(m_leaf)

    # 3. Dense Radiating Dome Chrysanthemum Flower Head
    # Dome core base
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.44, location=(0, 0, 1.95))
    dome = bpy.context.active_object
    dome.scale = (1.0, 1.0, 0.7)
    dome.data.materials.append(m_amber_petal)

    # Outer tier petals (radiating curl)
    for p in range(18):
        pa = p * (2 * math.pi / 18)
        px = math.cos(pa) * 0.5
        py = math.sin(pa) * 0.5
        bpy.ops.mesh.primitive_cylinder_add(radius=0.09, depth=0.5, location=(px, py, 1.86))
        pet = bpy.context.active_object
        pet.scale = (0.5, 0.1, 1.0)
        pet.rotation_euler = (math.radians(35) * math.sin(pa), -math.radians(35) * math.cos(pa), pa + math.pi/2)
        pet.data.materials.append(m_amber_petal)

    # Mid tier petals
    for p in range(14):
        pa = p * (2 * math.pi / 14) + 0.15
        px = math.cos(pa) * 0.35
        py = math.sin(pa) * 0.35
        bpy.ops.mesh.primitive_cylinder_add(radius=0.085, depth=0.45, location=(px, py, 2.02))
        pet = bpy.context.active_object
        pet.scale = (0.45, 0.1, 1.0)
        pet.rotation_euler = (math.radians(22) * math.sin(pa), -math.radians(22) * math.cos(pa), pa + math.pi/2)
        pet.data.materials.append(m_gold_petal)

    # Inner tier dense spiral crown petals
    for p in range(10):
        pa = p * (2 * math.pi / 10) + 0.3
        px = math.cos(pa) * 0.2
        py = math.sin(pa) * 0.2
        bpy.ops.mesh.primitive_cylinder_add(radius=0.075, depth=0.38, location=(px, py, 2.16))
        pet = bpy.context.active_object
        pet.scale = (0.4, 0.1, 1.0)
        pet.rotation_euler = (math.radians(10) * math.sin(pa), -math.radians(10) * math.cos(pa), pa + math.pi/2)
        pet.data.materials.append(m_gold_petal)

    # Golden stamen core
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.13, location=(0, 0, 2.25))
    stamen_core = bpy.context.active_object
    stamen_core.data.materials.append(m_gold_petal)

    export_asset("flora_golden_chrysanthemum")

if __name__ == "__main__":
    print("Generating Treasure Chest...")
    build_treasure_chest()
    print("Generating Relic Urn...")
    build_relic_urn()
    print("Generating Hero Clockwork Lotus...")
    build_clockwork_lotus()
    print("Generating Hero Golden Chrysanthemum...")
    build_golden_chrysanthemum()
    print("=== ALL TREASURE & FLORAL ASSETS GENERATED SUCCESSFULLY ===")
