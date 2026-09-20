import bpy
import bmesh
import math
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
RENDERS_DIR = os.path.join(BASE_DIR, "renders")
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(RENDERS_DIR, exist_ok=True)

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def set_input(node, name, val):
    if name in node.inputs:
        node.inputs[name].default_value = val
    elif name == "Emission Color" and "Emission" in node.inputs:
        node.inputs["Emission"].default_value = val

def make_material(name, color, metallic=0.0, roughness=0.5, emission=None, emission_strength=1.0):
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

def setup_camera_and_lighting(target_z=1.8, ortho_scale=4.5):
    cam_data = bpy.data.cameras.new(name="IsoCam")
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = ortho_scale
    cam = bpy.data.objects.new("IsoCam", cam_data)
    bpy.context.collection.objects.link(cam)
    
    cam.location = (6.0, -6.0, 5.0 + target_z)
    cam.rotation_euler = (math.radians(54.736), 0, math.radians(45))
    bpy.context.scene.camera = cam
    
    # Key Sun (Warm Gold)
    sun_data = bpy.data.lights.new("SunKey", 'SUN')
    sun_data.energy = 4.5
    sun_data.color = (1.0, 0.96, 0.88)
    sun = bpy.data.objects.new("SunKey", sun_data)
    sun.rotation_euler = (math.radians(45), math.radians(20), math.radians(35))
    bpy.context.collection.objects.link(sun)
    
    # Fill Sun (Teal Ambient)
    fill_data = bpy.data.lights.new("FillTeal", 'SUN')
    fill_data.energy = 2.2
    fill_data.color = (0.15, 0.55, 0.65)
    fill = bpy.data.objects.new("FillTeal", fill_data)
    fill.rotation_euler = (math.radians(-35), math.radians(-15), math.radians(-130))
    bpy.context.collection.objects.link(fill)
    
    # Rim Light (Amber Glow)
    rim_data = bpy.data.lights.new("RimAmber", 'POINT')
    rim_data.energy = 220.0
    rim_data.color = (1.0, 0.75, 0.3)
    rim = bpy.data.objects.new("RimAmber", rim_data)
    rim.location = (-4.0, 4.0, target_z + 3.0)
    bpy.context.collection.objects.link(rim)
    
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024
    scene.render.film_transparent = True

def smooth_object(obj):
    for poly in obj.data.polygons:
        poly.use_smooth = True

# ==============================================================================
# 1. VERDANT SANCTUM CORE (Tholos Rotunda + Armillary Rings + Mana Crystal)
# ==============================================================================
def build_sanctum_core():
    clear_scene()
    setup_camera_and_lighting(target_z=2.0, ortho_scale=5.8)
    
    mat_marble = make_material("CarraraMarble", (0.88, 0.85, 0.78, 1.0), metallic=0.04, roughness=0.32)
    mat_gold_brass = make_material("GoldBrass", (0.9, 0.68, 0.2, 1.0), metallic=0.92, roughness=0.2)
    mat_cyan_mana = make_material("SolarMana", (0.0, 0.96, 0.88, 1.0), metallic=0.1, roughness=0.08,
                                  emission=(0.0, 0.96, 0.88, 1.0), emission_strength=5.0)
    mat_peony = make_material("PeonyPink", (0.9, 0.36, 0.54, 1.0), metallic=0.0, roughness=0.55)
    
    objs = []
    
    # Stepped Circular Temple Dais
    bpy.ops.mesh.primitive_cylinder_add(radius=2.2, depth=0.3, vertices=32, location=(0, 0, 0.15))
    dais1 = bpy.context.active_object
    dais1.data.materials.append(mat_marble)
    smooth_object(dais1)
    objs.append(dais1)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=1.85, depth=0.25, vertices=32, location=(0, 0, 0.4))
    dais2 = bpy.context.active_object
    dais2.data.materials.append(mat_marble)
    smooth_object(dais2)
    objs.append(dais2)
    
    # 8 Corinthian Perimeter Columns
    for col_idx in range(8):
        angle = col_idx * (math.pi / 4.0)
        cx = math.cos(angle) * 1.5
        cy = math.sin(angle) * 1.5
        bpy.ops.mesh.primitive_cylinder_add(radius=0.14, depth=2.4, vertices=16, location=(cx, cy, 1.7))
        col = bpy.context.active_object
        col.data.materials.append(mat_marble)
        smooth_object(col)
        objs.append(col)
        
        # Column Base & Capital
        bpy.ops.mesh.primitive_cube_add(size=0.36, location=(cx, cy, 0.55))
        cbase = bpy.context.active_object
        cbase.scale = (1, 1, 0.4)
        cbase.data.materials.append(mat_marble)
        objs.append(cbase)
        
        bpy.ops.mesh.primitive_cube_add(size=0.38, location=(cx, cy, 2.95))
        ccap = bpy.context.active_object
        ccap.scale = (1, 1, 0.4)
        ccap.data.materials.append(mat_marble)
        objs.append(ccap)
        
    # Circular Architrave Ring
    bpy.ops.mesh.primitive_torus_add(major_radius=1.5, minor_radius=0.18, major_segments=32, minor_segments=12, location=(0, 0, 3.15))
    arch = bpy.context.active_object
    arch.data.materials.append(mat_marble)
    smooth_object(arch)
    objs.append(arch)
    
    # Domed Roof Cap
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.55, location=(0, 0, 3.15))
    dome = bpy.context.active_object
    dome.scale = (1, 1, 0.5)
    dome.data.materials.append(mat_marble)
    smooth_object(dome)
    objs.append(dome)
    
    # Rotunda Floral Peony Clusters
    for fi in range(12):
        fa = fi * (math.pi / 6.0)
        fx = math.cos(fa) * 1.62
        fy = math.sin(fa) * 1.62
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(fx, fy, 3.4))
        fl = bpy.context.active_object
        fl.scale = (1, 1, 0.7)
        fl.data.materials.append(mat_peony)
        smooth_object(fl)
        objs.append(fl)
        
    # Rotating Brass Armillary Rings
    for ring_i, r_rot in enumerate([(30, 20), (-25, 45), (60, -35)]):
        bpy.ops.mesh.primitive_torus_add(major_radius=1.0 - ring_i * 0.15, minor_radius=0.04, major_segments=32, minor_segments=12, location=(0, 0, 1.8))
        arm = bpy.context.active_object
        arm.rotation_euler = (math.radians(r_rot[0]), math.radians(r_rot[1]), 0)
        arm.data.materials.append(mat_gold_brass)
        smooth_object(arm)
        objs.append(arm)
        
    # Radiating Faceted Solar Mana Crystal (Center)
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.45, depth=0.9, location=(0, 0, 2.25))
    c_top = bpy.context.active_object
    c_top.data.materials.append(mat_cyan_mana)
    objs.append(c_top)
    
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.45, depth=0.9, location=(0, 0, 1.35))
    c_bot = bpy.context.active_object
    c_bot.rotation_euler = (math.radians(180), 0, 0)
    c_bot.data.materials.append(mat_cyan_mana)
    objs.append(c_bot)
    
    # Export and Render
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    
    glb = os.path.join(MODELS_DIR, "sanctum_core_rotunda.glb")
    bpy.ops.export_scene.gltf(filepath=glb, export_format='GLB', use_selection=True)
    
    render_file = os.path.join(RENDERS_DIR, "sanctum_core_rotunda_render.png")
    bpy.context.scene.render.filepath = render_file
    bpy.ops.render.render(write_still=True)
    print(f"Sanctum Core finished: {glb} and {render_file}")

# ==============================================================================
# 2. RESONANCE MONOLITH TOWER (Basalt Obelisk + Wisteria + Tuning Forks)
# ==============================================================================
def build_resonance_monolith():
    clear_scene()
    setup_camera_and_lighting(target_z=1.9, ortho_scale=4.5)
    
    mat_basalt = make_material("DarkBasalt", (0.28, 0.27, 0.29, 1.0), metallic=0.08, roughness=0.55)
    mat_brass = make_material("TuningBrass", (0.85, 0.65, 0.22, 1.0), metallic=0.92, roughness=0.25)
    mat_copper = make_material("ResonatorCopper", (0.8, 0.42, 0.25, 1.0), metallic=0.94, roughness=0.28)
    mat_violet_glow = make_material("SonicViolet", (0.7, 0.15, 0.85, 1.0), emission=(0.7, 0.15, 0.85, 1.0), emission_strength=4.5)
    mat_wisteria = make_material("WisteriaPurple", (0.6, 0.4, 0.75, 1.0), metallic=0.0, roughness=0.6)
    
    objs = []
    
    # Stepped Basalt Pedestal
    bpy.ops.mesh.primitive_cube_add(size=1.6, location=(0, 0, 0.15))
    base1 = bpy.context.active_object
    base1.scale = (1, 1, 0.2)
    base1.data.materials.append(mat_basalt)
    objs.append(base1)
    
    bpy.ops.mesh.primitive_cube_add(size=1.3, location=(0, 0, 0.4))
    base2 = bpy.context.active_object
    base2.scale = (1, 1, 0.2)
    base2.data.materials.append(mat_basalt)
    objs.append(base2)
    
    # Tapered Basalt Obelisk Shaft
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.65, radius2=0.38, depth=2.8, location=(0, 0, 1.9))
    obelisk = bpy.context.active_object
    obelisk.rotation_euler = (0, 0, math.radians(45))
    obelisk.data.materials.append(mat_basalt)
    objs.append(obelisk)
    
    # Obelisk Pyramidion Tip
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.38, depth=0.55, location=(0, 0, 3.55))
    tip = bpy.context.active_object
    tip.rotation_euler = (0, 0, math.radians(45))
    tip.data.materials.append(mat_brass)
    objs.append(tip)
    
    # Brass Central Acoustic Hub Collar
    bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=0.25, vertices=24, location=(0, -0.4, 2.0))
    hub = bpy.context.active_object
    hub.rotation_euler = (math.radians(90), 0, 0)
    hub.data.materials.append(mat_brass)
    smooth_object(hub)
    objs.append(hub)
    
    # Giant Polished Brass Tuning Forks (Left and Right)
    for side_sign in [-1, 1]:
        tx = side_sign * 0.95
        # Tuning fork stem
        bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.7, vertices=12, location=(tx, -0.4, 2.0))
        stem = bpy.context.active_object
        stem.rotation_euler = (0, math.radians(90), 0)
        stem.data.materials.append(mat_brass)
        objs.append(stem)
        
        # Dual prongs
        for prong_z in [-0.15, 0.15]:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.045, depth=0.9, vertices=12, location=(side_sign * 1.5, -0.4, 2.0 + prong_z))
            prong = bpy.context.active_object
            prong.rotation_euler = (0, math.radians(90), 0)
            prong.data.materials.append(mat_brass)
            objs.append(prong)
            
    # Copper Induction Resonator Coils
    for coil_z in [1.4, 2.6]:
        bpy.ops.mesh.primitive_torus_add(major_radius=0.35, minor_radius=0.08, major_segments=24, minor_segments=12, location=(0, -0.45, coil_z))
        coil = bpy.context.active_object
        coil.rotation_euler = (math.radians(90), 0, 0)
        coil.data.materials.append(mat_copper)
        smooth_object(coil)
        objs.append(coil)
        
    # Weeping Wisteria Vine Clusters
    for w_i in range(8):
        wa = w_i * (math.pi / 4.0)
        wx = math.cos(wa) * 0.55
        wy = math.sin(wa) * 0.55
        bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=0.8, vertices=8, location=(wx, wy, 2.9 - (w_i % 3) * 0.3))
        wist = bpy.context.active_object
        wist.data.materials.append(mat_wisteria)
        objs.append(wist)
        
    # Shimmering Violet Sonic Ground Shockwave Ring
    bpy.ops.mesh.primitive_torus_add(major_radius=1.8, minor_radius=0.04, major_segments=32, minor_segments=12, location=(0, 0, 0.08))
    ring = bpy.context.active_object
    ring.data.materials.append(mat_violet_glow)
    smooth_object(ring)
    objs.append(ring)
    
    # Export and Render
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    
    glb = os.path.join(MODELS_DIR, "tower_resonance_monolith.glb")
    bpy.ops.export_scene.gltf(filepath=glb, export_format='GLB', use_selection=True)
    
    render_file = os.path.join(RENDERS_DIR, "tower_resonance_monolith_render.png")
    bpy.context.scene.render.filepath = render_file
    bpy.ops.render.render(write_still=True)
    print(f"Resonance Monolith finished: {glb} and {render_file}")

# ==============================================================================
# 3. ZEPPELIN SKY-HULL (Armored War-Dirigible Aerial Automata)
# ==============================================================================
def build_zeppelin_sky_hull():
    clear_scene()
    setup_camera_and_lighting(target_z=2.0, ortho_scale=8.0)
    
    mat_hull_iron = make_material("HullIron", (0.35, 0.36, 0.38, 1.0), metallic=0.85, roughness=0.38)
    mat_brass_ribs = make_material("BrassRibs", (0.85, 0.65, 0.22, 1.0), metallic=0.92, roughness=0.25)
    mat_bronze_prop = make_material("PropBronze", (0.6, 0.45, 0.2, 1.0), metallic=0.9, roughness=0.22)
    mat_window = make_material("GondolaWindow", (1.0, 0.85, 0.4, 1.0), emission=(1.0, 0.85, 0.4, 1.0), emission_strength=3.5)
    
    objs = []
    
    # Main Airship Gasbag Hull (Elongated Streamlined Body along Y)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.2, location=(0, 0, 2.2))
    hull = bpy.context.active_object
    hull.scale = (1.1, 2.5, 1.1)
    hull.rotation_euler = (0, 0, 0)
    hull.data.materials.append(mat_hull_iron)
    smooth_object(hull)
    objs.append(hull)
    
    # Pointed Brass Nose Cone
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=1.0, depth=1.0, location=(0, -3.1, 2.2))
    nose = bpy.context.active_object
    nose.rotation_euler = (math.radians(-90), 0, 0)
    nose.data.materials.append(mat_brass_ribs)
    smooth_object(nose)
    objs.append(nose)
    
    # Armored Brass Girdle Rings
    for ring_y in [-1.8, -0.6, 0.6, 1.8]:
        bpy.ops.mesh.primitive_torus_add(major_radius=1.33, minor_radius=0.06, major_segments=32, minor_segments=12, location=(0, ring_y, 2.2))
        girdle = bpy.context.active_object
        girdle.rotation_euler = (math.radians(90), 0, 0)
        girdle.data.materials.append(mat_brass_ribs)
        smooth_object(girdle)
        objs.append(girdle)
        
    # Suspended Armored Gondola (Command Deck)
    bpy.ops.mesh.primitive_cube_add(size=0.8, location=(0, -0.6, 0.85))
    gondola = bpy.context.active_object
    gondola.scale = (0.7, 2.2, 0.7)
    gondola.data.materials.append(mat_hull_iron)
    objs.append(gondola)
    
    # Gondola Observation Windows
    bpy.ops.mesh.primitive_cube_add(size=0.7, location=(0, -1.45, 0.85))
    bridge = bpy.context.active_object
    bridge.scale = (0.72, 0.25, 0.4)
    bridge.data.materials.append(mat_window)
    objs.append(bridge)
    
    # Twin Smokestacks on Aft Deck
    for pipe_x in [-0.28, 0.28]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.11, depth=1.1, vertices=16, location=(pipe_x, 1.4, 3.4))
        pipe = bpy.context.active_object
        pipe.data.materials.append(mat_hull_iron)
        smooth_object(pipe)
        objs.append(pipe)
        
    # Twin Outrigger Propeller Engines (Left and Right)
    for prop_sign in [-1, 1]:
        px = prop_sign * 1.45
        # Engine Nacelle
        bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.8, vertices=16, location=(px, 0.2, 1.8))
        nacelle = bpy.context.active_object
        nacelle.rotation_euler = (math.radians(90), 0, 0)
        nacelle.data.materials.append(mat_brass_ribs)
        smooth_object(nacelle)
        objs.append(nacelle)
        
        # 3-Blade Propeller
        bpy.ops.mesh.primitive_cylinder_add(radius=0.55, depth=0.03, vertices=6, location=(px, -0.25, 1.8))
        prop = bpy.context.active_object
        prop.rotation_euler = (math.radians(90), 0, 0)
        prop.data.materials.append(mat_bronze_prop)
        objs.append(prop)
        
    # Clockwork Empennage Tail Fins (Vertical and Horizontal)
    bpy.ops.mesh.primitive_cube_add(size=0.5, location=(0, 2.8, 2.2))
    v_fin = bpy.context.active_object
    v_fin.scale = (0.1, 1.4, 2.2)
    v_fin.data.materials.append(mat_brass_ribs)
    objs.append(v_fin)
    
    bpy.ops.mesh.primitive_cube_add(size=0.5, location=(0, 2.8, 2.2))
    h_fin = bpy.context.active_object
    h_fin.scale = (2.2, 1.4, 0.1)
    h_fin.data.materials.append(mat_brass_ribs)
    objs.append(h_fin)
    
    # Export and Render
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    
    glb = os.path.join(MODELS_DIR, "enemy_zeppelin_sky_hull.glb")
    bpy.ops.export_scene.gltf(filepath=glb, export_format='GLB', use_selection=True)
    
    render_file = os.path.join(RENDERS_DIR, "enemy_zeppelin_sky_hull_render.png")
    bpy.context.scene.render.filepath = render_file
    bpy.ops.render.render(write_still=True)
    print(f"Zeppelin Sky-Hull finished: {glb} and {render_file}")

# ==============================================================================
# 4. GOLIATH COLOSSUS (Titan Walking Siege Fortress Boss)
# ==============================================================================
def build_goliath_colossus():
    clear_scene()
    setup_camera_and_lighting(target_z=2.2, ortho_scale=6.2)
    
    mat_heavy_armor = make_material("GoliathArmor", (0.22, 0.24, 0.26, 1.0), metallic=0.9, roughness=0.35)
    mat_brass_plate = make_material("GoliathBrass", (0.8, 0.6, 0.18, 1.0), metallic=0.92, roughness=0.26)
    mat_cyclops_eye = make_material("CrimsonEye", (1.0, 0.1, 0.15, 1.0), emission=(1.0, 0.1, 0.15, 1.0), emission_strength=6.0)
    mat_joint = make_material("HeavyJoint", (0.1, 0.1, 0.12, 1.0), metallic=0.95, roughness=0.2)
    
    objs = []
    
    # Massive Central Boiler Chassis (Upper Torso)
    bpy.ops.mesh.primitive_cylinder_add(radius=1.2, depth=1.8, vertices=24, location=(0, 0, 2.7))
    torso = bpy.context.active_object
    torso.rotation_euler = (math.radians(90), 0, 0)
    torso.data.materials.append(mat_heavy_armor)
    smooth_object(torso)
    objs.append(torso)
    
    # Cast-Brass Chest Breastplate
    bpy.ops.mesh.primitive_cube_add(size=1.2, location=(0, -0.9, 2.7))
    chest = bpy.context.active_object
    chest.scale = (1.1, 0.35, 1.0)
    chest.data.materials.append(mat_brass_plate)
    objs.append(chest)
    
    # Cyclopean Glowing Red Optic Lens (Center Visor)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.35, depth=0.25, vertices=24, location=(0, -1.15, 2.85))
    eye = bpy.context.active_object
    eye.rotation_euler = (math.radians(90), 0, 0)
    eye.data.materials.append(mat_cyclops_eye)
    smooth_object(eye)
    objs.append(eye)
    
    # Eye Heavy Brass Bezel
    bpy.ops.mesh.primitive_torus_add(major_radius=0.4, minor_radius=0.08, major_segments=24, minor_segments=12, location=(0, -1.18, 2.85))
    bezel = bpy.context.active_object
    bezel.rotation_euler = (math.radians(90), 0, 0)
    bezel.data.materials.append(mat_brass_plate)
    smooth_object(bezel)
    objs.append(bezel)
    
    # Quadruple Exhaust Smokestacks (Aft Boiler)
    for sx, sy in [(-0.55, 0.5), (0.55, 0.5), (-0.3, 0.8), (0.3, 0.8)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.14, depth=1.3, vertices=16, location=(sx, sy, 3.8))
        pipe = bpy.context.active_object
        pipe.data.materials.append(mat_heavy_armor)
        smooth_object(pipe)
        objs.append(pipe)
        
    # Massive Shoulder Pauldrons (Left & Right)
    for p_sign in [-1, 1]:
        px = p_sign * 1.55
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.75, location=(px, 0, 3.0))
        paul = bpy.context.active_object
        paul.scale = (0.7, 1.2, 0.9)
        paul.data.materials.append(mat_brass_plate)
        smooth_object(paul)
        objs.append(paul)
        
        # Heavy Bicep Arm Cannon
        bpy.ops.mesh.primitive_cylinder_add(radius=0.28, depth=1.4, vertices=16, location=(px, -0.4, 2.0))
        arm = bpy.context.active_object
        arm.rotation_euler = (math.radians(35), 0, 0)
        arm.data.materials.append(mat_heavy_armor)
        smooth_object(arm)
        objs.append(arm)
        
    # Reinforced Pelvis Girder
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.7))
    pelvis = bpy.context.active_object
    pelvis.scale = (1.6, 0.8, 0.5)
    pelvis.data.materials.append(mat_joint)
    objs.append(pelvis)
    
    # Colossal Hydraulic Walking Legs (Left & Right)
    for leg_sign in [-1, 1]:
        lx = leg_sign * 1.05
        # Heavy Thigh Piston
        bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=1.2, vertices=16, location=(lx, 0.15, 1.25))
        thigh = bpy.context.active_object
        thigh.rotation_euler = (math.radians(25), 0, 0)
        thigh.data.materials.append(mat_brass_plate)
        smooth_object(thigh)
        objs.append(thigh)
        
        # Massive Spherical Knee Joint
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.32, location=(lx, 0.35, 0.75))
        knee = bpy.context.active_object
        knee.data.materials.append(mat_joint)
        smooth_object(knee)
        objs.append(knee)
        
        # Armored Lower Shin
        bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=1.1, vertices=16, location=(lx, 0.15, 0.35))
        shin = bpy.context.active_object
        shin.rotation_euler = (math.radians(-20), 0, 0)
        shin.data.materials.append(mat_heavy_armor)
        smooth_object(shin)
        objs.append(shin)
        
        # Heavy Hydraulic Fortress Tread Foot
        bpy.ops.mesh.primitive_cube_add(size=0.7, location=(lx, 0, 0.1))
        foot = bpy.context.active_object
        foot.scale = (1.1, 1.7, 0.35)
        foot.data.materials.append(mat_brass_plate)
        objs.append(foot)
        
    # Export and Render
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    
    glb = os.path.join(MODELS_DIR, "enemy_goliath_colossus.glb")
    bpy.ops.export_scene.gltf(filepath=glb, export_format='GLB', use_selection=True)
    
    render_file = os.path.join(RENDERS_DIR, "enemy_goliath_colossus_render.png")
    bpy.context.scene.render.filepath = render_file
    bpy.ops.render.render(write_still=True)
    print(f"Goliath Colossus finished: {glb} and {render_file}")

if __name__ == "__main__":
    print("=== STARTING GENERATION OF EXPANDED 3D ASSETS ===")
    build_sanctum_core()
    build_resonance_monolith()
    build_zeppelin_sky_hull()
    build_goliath_colossus()
    print("=== ALL EXPANDED 3D ASSETS GENERATED AND EXPORTED SUCCESSFULLY ===")
