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

def setup_camera_and_lighting(target_z=1.6, ortho_scale=4.2):
    # Camera
    cam_data = bpy.data.cameras.new(name="IsoCam")
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = ortho_scale
    cam = bpy.data.objects.new("IsoCam", cam_data)
    bpy.context.collection.objects.link(cam)
    
    # 45 deg isometric perspective looking at (0, 0, target_z)
    cam.location = (5.5, -5.5, 4.5 + target_z)
    cam.rotation_euler = (math.radians(54.736), 0, math.radians(45))
    bpy.context.scene.camera = cam
    
    # Three-Point Cinematic Studio Lights
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
    
    # Rim Point Light (Incandescent Amber)
    rim_data = bpy.data.lights.new("RimAmber", 'POINT')
    rim_data.energy = 180.0
    rim_data.color = (1.0, 0.75, 0.3)
    rim = bpy.data.objects.new("RimAmber", rim_data)
    rim.location = (-3.5, 3.5, target_z + 2.5)
    bpy.context.collection.objects.link(rim)
    
    # Render settings
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024
    scene.render.film_transparent = True

def smooth_object(obj):
    for poly in obj.data.polygons:
        poly.use_smooth = True

# ==============================================================================
# 1. PRISM GATLING TURRET (High-Detail 3D)
# ==============================================================================
def build_prism_gatling():
    clear_scene()
    setup_camera_and_lighting(target_z=1.65, ortho_scale=4.2)
    
    mat_marble = make_material("CarraraMarble", (0.88, 0.85, 0.78, 1.0), metallic=0.04, roughness=0.3)
    mat_brass = make_material("PolishedBrass", (0.85, 0.62, 0.18, 1.0), metallic=0.92, roughness=0.22)
    mat_dark_iron = make_material("GunmetalIron", (0.14, 0.15, 0.17, 1.0), metallic=0.88, roughness=0.4)
    mat_cyan_mana = make_material("CyanManaCore", (0.0, 0.96, 0.88, 1.0), metallic=0.1, roughness=0.08,
                                  emission=(0.0, 0.96, 0.88, 1.0), emission_strength=4.5)
    mat_peony = make_material("PeonyPink", (0.9, 0.36, 0.54, 1.0), metallic=0.0, roughness=0.55)
    mat_leaf = make_material("IvyGreen", (0.16, 0.48, 0.24, 1.0), metallic=0.0, roughness=0.6)
    
    objs = []
    
    # 1. Base Stepped Plinth
    bpy.ops.mesh.primitive_cylinder_add(radius=1.2, depth=0.25, vertices=32, location=(0, 0, 0.125))
    b1 = bpy.context.active_object
    b1.data.materials.append(mat_marble)
    smooth_object(b1)
    objs.append(b1)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=1.02, depth=0.2, vertices=32, location=(0, 0, 0.325))
    b2 = bpy.context.active_object
    b2.data.materials.append(mat_marble)
    smooth_object(b2)
    objs.append(b2)
    
    # 2. Fluted Column Shaft
    bpy.ops.mesh.primitive_cylinder_add(radius=0.75, depth=1.6, vertices=32, location=(0, 0, 1.2))
    shaft = bpy.context.active_object
    shaft.data.materials.append(mat_marble)
    smooth_object(shaft)
    objs.append(shaft)
    
    # Flute ribs
    for f_idx in range(16):
        fa = f_idx * (math.pi / 8.0)
        fx = math.cos(fa) * 0.77
        fy = math.sin(fa) * 0.77
        bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=1.5, vertices=8, location=(fx, fy, 1.2))
        rib = bpy.context.active_object
        rib.data.materials.append(mat_marble)
        objs.append(rib)
        
    # 3. Capital (Corinthian Abacus)
    bpy.ops.mesh.primitive_cube_add(size=1.6, location=(0, 0, 2.05))
    cap = bpy.context.active_object
    cap.scale = (1.0, 1.0, 0.15)
    cap.data.materials.append(mat_marble)
    objs.append(cap)
    
    # Classical Peony & Ivy Trim
    for p_i in range(8):
        pa = p_i * (math.pi / 4.0)
        px = math.cos(pa) * 0.95
        py = math.sin(pa) * 0.95
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.13, location=(px, py, 1.95))
        fl = bpy.context.active_object
        fl.scale = (1.0, 1.0, 0.7)
        fl.data.materials.append(mat_peony if p_i % 2 == 0 else mat_leaf)
        smooth_object(fl)
        objs.append(fl)
        
    # 4. Antique Brass Turntable
    bpy.ops.mesh.primitive_cylinder_add(radius=0.72, depth=0.15, vertices=32, location=(0, 0, 2.22))
    turntable = bpy.context.active_object
    turntable.data.materials.append(mat_brass)
    smooth_object(turntable)
    objs.append(turntable)
    
    # Brass Gear Teeth Ring
    for g_i in range(12):
        ga = g_i * (math.pi / 6.0)
        gx = math.cos(ga) * 0.75
        gy = math.sin(ga) * 0.75
        bpy.ops.mesh.primitive_cube_add(size=0.12, location=(gx, gy, 2.22))
        tooth = bpy.context.active_object
        tooth.data.materials.append(mat_brass)
        objs.append(tooth)
        
    # 5. Heavy Gatling Gun Cradle
    bpy.ops.mesh.primitive_cube_add(size=0.65, location=(0, 0, 2.65))
    housing = bpy.context.active_object
    housing.scale = (0.85, 1.2, 0.65)
    housing.data.materials.append(mat_brass)
    objs.append(housing)
    
    # 6. Six-Barrel Rotating Gatling Array
    b_center = (0, -0.65, 2.65)
    for bi in range(6):
        ba = bi * (math.pi / 3.0)
        bx = b_center[0] + math.cos(ba) * 0.16
        bz = b_center[2] + math.sin(ba) * 0.16
        bpy.ops.mesh.primitive_cylinder_add(radius=0.045, depth=1.2, vertices=16, location=(bx, b_center[1] - 0.45, bz))
        barrel = bpy.context.active_object
        barrel.rotation_euler = (math.radians(90), 0, 0)
        barrel.data.materials.append(mat_dark_iron)
        smooth_object(barrel)
        objs.append(barrel)
        
    # Muzzle Stabilizer Ring
    bpy.ops.mesh.primitive_torus_add(major_radius=0.2, minor_radius=0.035, location=(0, -1.45, 2.65))
    ring = bpy.context.active_object
    ring.rotation_euler = (math.radians(90), 0, 0)
    ring.data.materials.append(mat_brass)
    smooth_object(ring)
    objs.append(ring)
    
    # 7. Hovering Octahedral Cyan Mana Crystal
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.32, depth=0.65, location=(0, 0.1, 3.45))
    c_top = bpy.context.active_object
    c_top.data.materials.append(mat_cyan_mana)
    objs.append(c_top)
    
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.32, depth=0.65, location=(0, 0.1, 3.05))
    c_bot = bpy.context.active_object
    c_bot.rotation_euler = (math.radians(180), 0, 0)
    c_bot.data.materials.append(mat_cyan_mana)
    objs.append(c_bot)
    
    # Export GLB and Render
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    
    glb = os.path.join(MODELS_DIR, "tower_prism_gatling.glb")
    bpy.ops.export_scene.gltf(filepath=glb, export_format='GLB', use_selection=True)
    
    render_file = os.path.join(RENDERS_DIR, "tower_prism_gatling_render.png")
    bpy.context.scene.render.filepath = render_file
    bpy.ops.render.render(write_still=True)
    print(f"Prism Gatling finished: {glb} and {render_file}")

# ==============================================================================
# 2. BLOOM CANNON (High-Detail 3D)
# ==============================================================================
def build_bloom_cannon():
    clear_scene()
    setup_camera_and_lighting(target_z=1.25, ortho_scale=3.8)
    
    mat_stone = make_material("PedestalStone", (0.58, 0.54, 0.48, 1.0), metallic=0.0, roughness=0.6)
    mat_patina = make_material("PatinaBrass", (0.7, 0.56, 0.28, 1.0), metallic=0.88, roughness=0.32)
    mat_iron = make_material("CastIron", (0.16, 0.17, 0.19, 1.0), metallic=0.85, roughness=0.45)
    mat_amber = make_material("SporeEmber", (1.0, 0.45, 0.08, 1.0), emission=(1.0, 0.45, 0.08, 1.0), emission_strength=4.5)
    
    objs = []
    
    # Stepped Dais Base
    bpy.ops.mesh.primitive_cylinder_add(radius=1.35, depth=0.28, vertices=32, location=(0, 0, 0.14))
    base = bpy.context.active_object
    base.data.materials.append(mat_stone)
    smooth_object(base)
    objs.append(base)
    
    # Rotating Turntable Ring
    bpy.ops.mesh.primitive_cylinder_add(radius=1.05, depth=0.18, vertices=32, location=(0, 0, 0.35))
    collar = bpy.context.active_object
    collar.data.materials.append(mat_patina)
    smooth_object(collar)
    objs.append(collar)
    
    # 8 Armored Mechanical Lotus Petals (Curved flaring plates)
    for pi in range(8):
        pa = pi * (math.pi / 4.0)
        px = math.cos(pa) * 0.72
        py = math.sin(pa) * 0.72
        bpy.ops.mesh.primitive_cube_add(size=0.38, location=(px, py, 0.75))
        petal = bpy.context.active_object
        petal.scale = (0.5, 0.14, 1.1)
        petal.rotation_euler = (math.sin(pa) * 0.38, -math.cos(pa) * 0.38, pa)
        petal.data.materials.append(mat_patina)
        smooth_object(petal)
        objs.append(petal)
        
    # Heavy Mortar Cannon Barrel
    bpy.ops.mesh.primitive_cylinder_add(radius=0.42, depth=1.75, vertices=24, location=(0, -0.15, 1.2))
    barrel = bpy.context.active_object
    barrel.rotation_euler = (math.radians(45), 0, 0)
    barrel.data.materials.append(mat_iron)
    smooth_object(barrel)
    objs.append(barrel)
    
    # Reinforced Brass Barrel Rings
    for by, bz in [(-0.02, 1.05), (-0.38, 1.45)]:
        bpy.ops.mesh.primitive_torus_add(major_radius=0.45, minor_radius=0.06, location=(0, by, bz))
        band = bpy.context.active_object
        band.rotation_euler = (math.radians(45), 0, 0)
        band.data.materials.append(mat_patina)
        smooth_object(band)
        objs.append(band)
        
    # Incandescent Spore Shell in Muzzle
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(0, -0.68, 1.75))
    shell = bpy.context.active_object
    shell.data.materials.append(mat_amber)
    smooth_object(shell)
    objs.append(shell)
    
    # Export & Render
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    
    glb = os.path.join(MODELS_DIR, "tower_bloom_cannon.glb")
    bpy.ops.export_scene.gltf(filepath=glb, export_format='GLB', use_selection=True)
    
    render_file = os.path.join(RENDERS_DIR, "tower_bloom_cannon_render.png")
    bpy.context.scene.render.filepath = render_file
    bpy.ops.render.render(write_still=True)
    print(f"Bloom Cannon finished: {glb} and {render_file}")

# ==============================================================================
# 3. DIESEL WALKER (High-Detail 3D Enemy Mech)
# ==============================================================================
def build_diesel_walker():
    clear_scene()
    setup_camera_and_lighting(target_z=1.45, ortho_scale=3.8)
    
    mat_iron = make_material("ArmorIron", (0.24, 0.25, 0.28, 1.0), metallic=0.88, roughness=0.35)
    mat_brass = make_material("RivetedBrass", (0.8, 0.6, 0.2, 1.0), metallic=0.9, roughness=0.28)
    mat_headlight = make_material("Headlight", (1.0, 0.65, 0.1, 1.0), emission=(1.0, 0.65, 0.1, 1.0), emission_strength=5.0)
    mat_joint = make_material("HydraulicJoint", (0.1, 0.1, 0.12, 1.0), metallic=0.92, roughness=0.25)
    
    objs = []
    
    # Boiler Torso
    bpy.ops.mesh.primitive_cylinder_add(radius=0.68, depth=1.05, vertices=24, location=(0, 0, 1.65))
    torso = bpy.context.active_object
    torso.rotation_euler = (math.radians(90), 0, 0)
    torso.data.materials.append(mat_iron)
    smooth_object(torso)
    objs.append(torso)
    
    # Front Armored Chest Plate
    bpy.ops.mesh.primitive_cube_add(size=0.75, location=(0, -0.58, 1.65))
    chest = bpy.context.active_object
    chest.scale = (0.9, 0.2, 0.8)
    chest.data.materials.append(mat_brass)
    objs.append(chest)
    
    # Dual Headlights
    for ex in [-0.22, 0.22]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.11, depth=0.14, vertices=16, location=(ex, -0.7, 1.72))
        eye = bpy.context.active_object
        eye.rotation_euler = (math.radians(90), 0, 0)
        eye.data.materials.append(mat_headlight)
        smooth_object(eye)
        objs.append(eye)
        
    # Dual Exhaust Smokestacks
    for px in [-0.3, 0.3]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.09, depth=0.75, vertices=16, location=(px, 0.32, 2.35))
        pipe = bpy.context.active_object
        pipe.data.materials.append(mat_iron)
        smooth_object(pipe)
        objs.append(pipe)
        
    # Pelvis Joint
    bpy.ops.mesh.primitive_cube_add(size=0.48, location=(0, 0, 1.15))
    hip = bpy.context.active_object
    hip.scale = (1.3, 0.6, 0.4)
    hip.data.materials.append(mat_joint)
    objs.append(hip)
    
    # Left & Right Legs
    for leg_sign in [-1, 1]:
        lx = leg_sign * 0.65
        # Thigh
        bpy.ops.mesh.primitive_cylinder_add(radius=0.13, depth=0.65, vertices=16, location=(lx, 0.1, 0.88))
        thigh = bpy.context.active_object
        thigh.rotation_euler = (math.radians(20), 0, 0)
        thigh.data.materials.append(mat_brass)
        smooth_object(thigh)
        objs.append(thigh)
        
        # Knee
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.16, location=(lx, 0.18, 0.58))
        knee = bpy.context.active_object
        knee.data.materials.append(mat_joint)
        smooth_object(knee)
        objs.append(knee)
        
        # Shin
        bpy.ops.mesh.primitive_cylinder_add(radius=0.11, depth=0.65, vertices=16, location=(lx, 0.05, 0.3))
        shin = bpy.context.active_object
        shin.rotation_euler = (math.radians(-15), 0, 0)
        shin.data.materials.append(mat_iron)
        smooth_object(shin)
        objs.append(shin)
        
        # Foot
        bpy.ops.mesh.primitive_cube_add(size=0.38, location=(lx, -0.05, 0.05))
        foot = bpy.context.active_object
        foot.scale = (0.8, 1.35, 0.25)
        foot.data.materials.append(mat_brass)
        objs.append(foot)
        
    # Export & Render
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    
    glb = os.path.join(MODELS_DIR, "enemy_diesel_walker.glb")
    bpy.ops.export_scene.gltf(filepath=glb, export_format='GLB', use_selection=True)
    
    render_file = os.path.join(RENDERS_DIR, "enemy_diesel_walker_render.png")
    bpy.context.scene.render.filepath = render_file
    bpy.ops.render.render(write_still=True)
    print(f"Diesel Walker finished: {glb} and {render_file}")

if __name__ == "__main__":
    build_prism_gatling()
    build_bloom_cannon()
    build_diesel_walker()
