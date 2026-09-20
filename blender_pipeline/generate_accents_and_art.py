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

def setup_camera_and_lighting(target_z=1.8, ortho_scale=4.8):
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
    sun_data.energy = 4.8
    sun_data.color = (1.0, 0.96, 0.88)
    sun = bpy.data.objects.new("SunKey", sun_data)
    sun.rotation_euler = (math.radians(45), math.radians(20), math.radians(35))
    bpy.context.collection.objects.link(sun)
    
    # Fill Sun (Teal Ambient)
    fill_data = bpy.data.lights.new("FillTeal", 'SUN')
    fill_data.energy = 2.4
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
# 1. ACCENT MASONRY BLOCKS & PLINTHS (Carrara Marble, Brass Inlay & Chrysanthemums)
# ==============================================================================
def build_masonry_blocks():
    clear_scene()
    setup_camera_and_lighting(target_z=1.2, ortho_scale=4.2)
    
    mat_marble = make_material("CarraraMarble", (0.9, 0.88, 0.82, 1.0), metallic=0.04, roughness=0.35)
    mat_brass = make_material("InlayBrass", (0.88, 0.68, 0.22, 1.0), metallic=0.92, roughness=0.22)
    mat_gold_flower = make_material("ChrysanthemumGold", (0.95, 0.72, 0.08, 1.0), metallic=0.05, roughness=0.5)
    mat_ivy = make_material("IvyGreen", (0.18, 0.42, 0.16, 1.0), metallic=0.0, roughness=0.6)
    mat_cyan_conduit = make_material("CyanConduit", (0.0, 0.95, 0.85, 1.0), emission=(0.0, 0.95, 0.85, 1.0), emission_strength=4.0)
    
    objs = []
    
    # Stepped Foundation Paver Slab
    bpy.ops.mesh.primitive_cube_add(size=2.4, location=(0, 0, 0.1))
    slab = bpy.context.active_object
    slab.scale = (1.0, 1.0, 0.08)
    slab.data.materials.append(mat_marble)
    objs.append(slab)
    
    # Inlaid Brass Floor Conduits (Labyrinthine lines on ground)
    for cx in [-0.8, 0.8]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cx, 0, 0.21))
        strip = bpy.context.active_object
        strip.scale = (0.04, 2.2, 0.02)
        strip.data.materials.append(mat_brass)
        objs.append(strip)
    for cy in [-0.8, 0.8]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, cy, 0.21))
        strip = bpy.context.active_object
        strip.scale = (2.2, 0.04, 0.02)
        strip.data.materials.append(mat_cyan_conduit)
        objs.append(strip)
        
    # Main Carved Monumental Block
    bpy.ops.mesh.primitive_cube_add(size=1.2, location=(-0.3, -0.2, 0.8))
    block1 = bpy.context.active_object
    block1.scale = (0.9, 0.9, 0.9)
    block1.data.materials.append(mat_marble)
    objs.append(block1)
    
    # Secondary Stacked Block (Half-offset)
    bpy.ops.mesh.primitive_cube_add(size=0.8, location=(-0.25, -0.2, 1.8))
    block2 = bpy.context.active_object
    block2.scale = (0.85, 0.85, 0.7)
    block2.data.materials.append(mat_marble)
    objs.append(block2)
    
    # Fallen Fluted Column Drum Beside Block
    bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=0.8, vertices=20, location=(0.75, 0.5, 0.45))
    drum = bpy.context.active_object
    drum.rotation_euler = (math.radians(90), 0, math.radians(25))
    drum.data.materials.append(mat_marble)
    smooth_object(drum)
    objs.append(drum)
    
    # Brass Band Clamping Drum
    bpy.ops.mesh.primitive_torus_add(major_radius=0.47, minor_radius=0.03, major_segments=24, minor_segments=12, location=(0.75, 0.5, 0.45))
    band = bpy.context.active_object
    band.rotation_euler = (math.radians(90), 0, math.radians(25))
    band.data.materials.append(mat_brass)
    smooth_object(band)
    objs.append(band)
    
    # Chrysanthemums Clustering at Block Base and Crevices
    for f_idx in range(14):
        ang = f_idx * 0.45
        fr = 0.7 + (f_idx % 4) * 0.25
        fx = math.cos(ang) * fr + 0.1
        fy = math.sin(ang) * fr + 0.1
        fz = 0.25 + (f_idx % 3) * 0.15
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(fx, fy, fz))
        fl = bpy.context.active_object
        fl.scale = (1, 1, 0.6)
        fl.data.materials.append(mat_gold_flower)
        smooth_object(fl)
        objs.append(fl)
        
    # Export & Render
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    
    glb = os.path.join(MODELS_DIR, "accent_masonry_blocks.glb")
    bpy.ops.export_scene.gltf(filepath=glb, export_format='GLB', use_selection=True)
    
    render_file = os.path.join(RENDERS_DIR, "accent_masonry_blocks_render.png")
    bpy.context.scene.render.filepath = render_file
    bpy.ops.render.render(write_still=True)
    print(f"Masonry Blocks finished: {glb} and {render_file}")

# ==============================================================================
# 2. STATUE OF ATHENA AUTOMATA (Winged Greco-Roman Deity with Clockwork)
# ==============================================================================
def build_statue_automata():
    clear_scene()
    setup_camera_and_lighting(target_z=2.1, ortho_scale=5.6)
    
    mat_statue_marble = make_material("StatueMarble", (0.92, 0.90, 0.85, 1.0), metallic=0.05, roughness=0.3)
    mat_brass_wings = make_material("ClockworkBrass", (0.88, 0.68, 0.2, 1.0), metallic=0.94, roughness=0.22)
    mat_cyan_spear = make_material("SolarSpear", (0.0, 0.98, 0.9, 1.0), emission=(0.0, 0.98, 0.9, 1.0), emission_strength=5.5)
    mat_peony = make_material("PeonyPink", (0.9, 0.38, 0.55, 1.0), metallic=0.0, roughness=0.55)
    mat_gold_flower = make_material("ChrysanthemumGold", (0.95, 0.72, 0.08, 1.0), metallic=0.05, roughness=0.5)
    
    objs = []
    
    # Stepped Corinthian Pedestal Plinth
    bpy.ops.mesh.primitive_cube_add(size=1.4, location=(0, 0, 0.2))
    p1 = bpy.context.active_object
    p1.scale = (1, 1, 0.3)
    p1.data.materials.append(mat_statue_marble)
    objs.append(p1)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.55, depth=0.9, vertices=24, location=(0, 0, 0.8))
    p2 = bpy.context.active_object
    p2.data.materials.append(mat_statue_marble)
    smooth_object(p2)
    objs.append(p2)
    
    bpy.ops.mesh.primitive_cube_add(size=1.1, location=(0, 0, 1.3))
    p3 = bpy.context.active_object
    p3.scale = (1, 1, 0.15)
    p3.data.materials.append(mat_statue_marble)
    objs.append(p3)
    
    # Statue Classical Robed Torso & Chiton
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.38, radius2=0.28, depth=1.4, location=(0, 0, 2.1))
    torso = bpy.context.active_object
    torso.data.materials.append(mat_statue_marble)
    smooth_object(torso)
    objs.append(torso)
    
    # Classical Goddess Head & Corinthian Helmet
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=(0, 0, 3.0))
    head = bpy.context.active_object
    head.data.materials.append(mat_statue_marble)
    smooth_object(head)
    objs.append(head)
    
    # Golden Laurel Crest
    bpy.ops.mesh.primitive_torus_add(major_radius=0.24, minor_radius=0.04, major_segments=24, minor_segments=12, location=(0, 0, 3.08))
    crest = bpy.context.active_object
    crest.data.materials.append(mat_brass_wings)
    smooth_object(crest)
    objs.append(crest)
    
    # Mechanical Clockwork Wings (Left and Right - Fan of articulated blades)
    for w_sign in [-1, 1]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(w_sign * 0.28, 0.2, 2.45))
        w_hub = bpy.context.active_object
        w_hub.data.materials.append(mat_brass_wings)
        objs.append(w_hub)
        
        for blade_i in range(5):
            b_angle = math.radians(22 + blade_i * 14)
            b_len = 0.9 + blade_i * 0.15
            bx = w_sign * (0.3 + math.sin(b_angle) * (b_len * 0.55))
            by = 0.25 + math.sin(b_angle) * 0.2
            bz = 2.45 + math.cos(b_angle) * (b_len * 0.55)
            bpy.ops.mesh.primitive_cube_add(size=0.18, location=(bx, by, bz))
            blade = bpy.context.active_object
            blade.scale = (w_sign * (b_len * 4.2), 0.14, 0.38)
            blade.rotation_euler = (math.radians(12), math.radians(-w_sign * (28 + blade_i * 8)), math.radians(w_sign * 22))
            blade.data.materials.append(mat_brass_wings)
            objs.append(blade)
            
    # Solar Mana Spear (Held in Hand)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.032, depth=2.4, vertices=12, location=(0.48, -0.15, 2.3))
    spear_shaft = bpy.context.active_object
    spear_shaft.data.materials.append(mat_brass_wings)
    objs.append(spear_shaft)
    
    # Radiant Spear Head Tip
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.11, depth=0.5, location=(0.48, -0.15, 3.65))
    spear_tip = bpy.context.active_object
    spear_tip.data.materials.append(mat_cyan_spear)
    objs.append(spear_tip)
    
    # Flower Garlands Draping Pedestal Base
    for fi in range(12):
        fa = fi * (math.pi / 6.0)
        fx = math.cos(fa) * 0.72
        fy = math.sin(fa) * 0.72
        fz = 0.38 + (fi % 2) * 0.12
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.14, location=(fx, fy, fz))
        fl = bpy.context.active_object
        fl.scale = (1, 1, 0.7)
        fl.data.materials.append(mat_peony if fi % 2 == 0 else mat_gold_flower)
        smooth_object(fl)
        objs.append(fl)
        
    # Export & Render
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    
    glb = os.path.join(MODELS_DIR, "statue_automata_athena.glb")
    bpy.ops.export_scene.gltf(filepath=glb, export_format='GLB', use_selection=True)
    
    render_file = os.path.join(RENDERS_DIR, "statue_automata_athena_render.png")
    bpy.context.scene.render.filepath = render_file
    bpy.ops.render.render(write_still=True)
    print(f"Statue finished: {glb} and {render_file}")

# ==============================================================================
# 3. ACCENT COLUMN & CARVED PEDIMENT (Corinthian Fluting, Arch & Ivy)
# ==============================================================================
def build_column_pediment():
    clear_scene()
    setup_camera_and_lighting(target_z=2.1, ortho_scale=6.2)
    
    mat_marble = make_material("CarraraMarble", (0.9, 0.88, 0.82, 1.0), metallic=0.04, roughness=0.35)
    mat_brass = make_material("AccentBrass", (0.88, 0.68, 0.22, 1.0), metallic=0.92, roughness=0.22)
    mat_gold_flower = make_material("ChrysanthemumGold", (0.95, 0.72, 0.08, 1.0), metallic=0.05, roughness=0.5)
    mat_peony = make_material("PeonyPink", (0.9, 0.38, 0.55, 1.0), metallic=0.0, roughness=0.55)
    mat_ivy = make_material("IvyGreen", (0.18, 0.42, 0.16, 1.0), metallic=0.0, roughness=0.6)
    
    objs = []
    
    # Plinth Base
    bpy.ops.mesh.primitive_cube_add(size=1.2, location=(0, 0, 0.18))
    base = bpy.context.active_object
    base.scale = (1, 1, 0.3)
    base.data.materials.append(mat_marble)
    objs.append(base)
    
    # Main Fluted Corinthian Column Shaft
    bpy.ops.mesh.primitive_cylinder_add(radius=0.38, depth=2.8, vertices=24, location=(0, 0, 1.7))
    col = bpy.context.active_object
    col.data.materials.append(mat_marble)
    smooth_object(col)
    objs.append(col)
    
    # Classical Capital with Acanthus Volutes
    bpy.ops.mesh.primitive_cube_add(size=0.95, location=(0, 0, 3.2))
    cap = bpy.context.active_object
    cap.scale = (1, 1, 0.4)
    cap.data.materials.append(mat_marble)
    objs.append(cap)
    
    # Polished Brass Architrave Reinforcement Ring
    bpy.ops.mesh.primitive_torus_add(major_radius=0.48, minor_radius=0.05, major_segments=32, minor_segments=12, location=(0, 0, 1.7))
    ring = bpy.context.active_object
    ring.data.materials.append(mat_brass)
    smooth_object(ring)
    objs.append(ring)
    
    # Triangular Classical Pediment Cap
    bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=0.85, depth=0.75, location=(0, 0, 3.75))
    ped = bpy.context.active_object
    ped.rotation_euler = (math.radians(90), 0, math.radians(90))
    ped.data.materials.append(mat_marble)
    objs.append(ped)
    
    # Climbing Ivy Vine Spiral
    for step in range(18):
        ang = step * 0.55
        iv_x = math.cos(ang) * 0.42
        iv_y = math.sin(ang) * 0.42
        iv_z = 0.4 + step * 0.15
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(iv_x, iv_y, iv_z))
        leaf = bpy.context.active_object
        leaf.scale = (1, 1, 0.4)
        leaf.data.materials.append(mat_ivy)
        smooth_object(leaf)
        objs.append(leaf)
        
        # Occasional flower bud
        if step % 4 == 0:
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.11, location=(iv_x * 1.15, iv_y * 1.15, iv_z))
            fl = bpy.context.active_object
            fl.data.materials.append(mat_gold_flower if step % 8 == 0 else mat_peony)
            smooth_object(fl)
            objs.append(fl)
            
    # Export & Render
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    
    glb = os.path.join(MODELS_DIR, "accent_column_pediment.glb")
    bpy.ops.export_scene.gltf(filepath=glb, export_format='GLB', use_selection=True)
    
    render_file = os.path.join(RENDERS_DIR, "accent_column_pediment_render.png")
    bpy.context.scene.render.filepath = render_file
    bpy.ops.render.render(write_still=True)
    print(f"Column Pediment finished: {glb} and {render_file}")

if __name__ == "__main__":
    print("=== STARTING GENERATION OF ACCENTS & ART ASSETS ===")
    build_masonry_blocks()
    build_statue_automata()
    build_column_pediment()
    print("=== ALL ACCENTS & ART ASSETS GENERATED AND EXPORTED SUCCESSFULLY ===")
