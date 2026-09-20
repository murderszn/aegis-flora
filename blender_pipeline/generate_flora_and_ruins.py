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

def setup_camera_and_lighting(target_z=2.0, ortho_scale=5.5):
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
# 1. COLUMNAR CYPRESS TREE (Mediterranean Slender Conifer + Clockwork Rings)
# ==============================================================================
def build_cypress_tree():
    clear_scene()
    setup_camera_and_lighting(target_z=2.8, ortho_scale=8.5)
    
    mat_wood = make_material("CypressBark", (0.35, 0.28, 0.22, 1.0), metallic=0.05, roughness=0.7)
    mat_leaves = make_material("CypressNeedles", (0.12, 0.32, 0.18, 1.0), metallic=0.0, roughness=0.55)
    mat_leaves_light = make_material("CypressTip", (0.18, 0.42, 0.22, 1.0), metallic=0.0, roughness=0.55)
    mat_brass = make_material("ArborBrass", (0.85, 0.65, 0.22, 1.0), metallic=0.92, roughness=0.25)
    mat_gold_flower = make_material("GoldChrysanthemum", (0.95, 0.72, 0.08, 1.0), metallic=0.05, roughness=0.5)
    mat_peony = make_material("PeonyPink", (0.9, 0.38, 0.55, 1.0), metallic=0.0, roughness=0.55)
    mat_stone = make_material("MarblePaver", (0.88, 0.86, 0.80, 1.0), metallic=0.04, roughness=0.35)
    
    objs = []
    
    # Octagonal Stone Planter Plinth
    bpy.ops.mesh.primitive_cylinder_add(radius=1.1, depth=0.3, vertices=8, location=(0, 0, 0.15))
    plinth = bpy.context.active_object
    plinth.data.materials.append(mat_stone)
    objs.append(plinth)
    
    # Tree Trunk
    bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=1.6, vertices=16, location=(0, 0, 0.9))
    trunk = bpy.context.active_object
    trunk.data.materials.append(mat_wood)
    smooth_object(trunk)
    objs.append(trunk)
    
    # Brass Tree Collar Clamp
    bpy.ops.mesh.primitive_torus_add(major_radius=0.25, minor_radius=0.04, major_segments=24, minor_segments=12, location=(0, 0, 0.6))
    collar = bpy.context.active_object
    collar.data.materials.append(mat_brass)
    smooth_object(collar)
    objs.append(collar)
    
    # Tiered Columnar Foliage (3 tapered stacking ellipsoids)
    tiers = [
        (1.0, 0.75, 1.8, 1.9, mat_leaves),
        (0.85, 0.65, 1.9, 3.1, mat_leaves),
        (0.65, 0.45, 1.8, 4.2, mat_leaves_light)
    ]
    for rx, ry, rz, z_pos, mat in tiers:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=(0, 0, z_pos))
        tier = bpy.context.active_object
        tier.scale = (rx, ry, rz)
        tier.data.materials.append(mat)
        smooth_object(tier)
        objs.append(tier)
        
    # Cypress Spire Tip
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.38, depth=1.1, location=(0, 0, 5.3))
    tip = bpy.context.active_object
    tip.data.materials.append(mat_leaves_light)
    smooth_object(tip)
    objs.append(tip)
    
    # Flower Mound at Base (Chrysanthemums & Peonies)
    for fi in range(10):
        ang = fi * (math.pi / 5.0)
        fx = math.cos(ang) * 0.75
        fy = math.sin(ang) * 0.75
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(fx, fy, 0.32))
        fl = bpy.context.active_object
        fl.scale = (1, 1, 0.6)
        fl.data.materials.append(mat_gold_flower if fi % 2 == 0 else mat_peony)
        smooth_object(fl)
        objs.append(fl)
        
    # Export & Render
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    
    glb = os.path.join(MODELS_DIR, "flora_cypress_tree.glb")
    bpy.ops.export_scene.gltf(filepath=glb, export_format='GLB', use_selection=True)
    
    render_file = os.path.join(RENDERS_DIR, "flora_cypress_tree_render.png")
    bpy.context.scene.render.filepath = render_file
    bpy.ops.render.render(write_still=True)
    print(f"Cypress Tree finished: {glb} and {render_file}")

# ==============================================================================
# 2. GNARLED OLIVE TREE (Ancient Twisted Boughs + Trailing Wisteria)
# ==============================================================================
def build_olive_tree():
    clear_scene()
    setup_camera_and_lighting(target_z=2.1, ortho_scale=5.8)
    
    mat_gnarled = make_material("OliveBark", (0.32, 0.28, 0.24, 1.0), metallic=0.08, roughness=0.75)
    mat_canopy = make_material("OliveSilverGreen", (0.38, 0.46, 0.32, 1.0), metallic=0.0, roughness=0.5)
    mat_brass = make_material("BoughBrass", (0.85, 0.65, 0.22, 1.0), metallic=0.92, roughness=0.25)
    mat_wisteria = make_material("WisteriaLilac", (0.65, 0.42, 0.78, 1.0), metallic=0.0, roughness=0.55)
    mat_gold_flower = make_material("GoldChrysanthemum", (0.95, 0.72, 0.08, 1.0), metallic=0.05, roughness=0.5)
    mat_marble = make_material("MarblePaver", (0.88, 0.86, 0.80, 1.0), metallic=0.04, roughness=0.35)
    
    objs = []
    
    # Low Stone Paver Base
    bpy.ops.mesh.primitive_cylinder_add(radius=1.4, depth=0.2, vertices=24, location=(0, 0, 0.1))
    base = bpy.context.active_object
    base.data.materials.append(mat_marble)
    smooth_object(base)
    objs.append(base)
    
    # Twisted Main Trunk
    bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=1.4, vertices=16, location=(0, 0, 0.8))
    trunk = bpy.context.active_object
    trunk.scale = (1.2, 0.8, 1.0)
    trunk.rotation_euler = (math.radians(10), math.radians(-12), math.radians(25))
    trunk.data.materials.append(mat_gnarled)
    smooth_object(trunk)
    objs.append(trunk)
    
    # Clockwork Graft Plate on Trunk
    bpy.ops.mesh.primitive_cube_add(size=0.35, location=(0.35, -0.15, 0.9))
    plate = bpy.context.active_object
    plate.scale = (0.2, 1.2, 1.2)
    plate.data.materials.append(mat_brass)
    objs.append(plate)
    
    # Spreading Gnarled Boughs (3 branches)
    branches = [
        (-0.7, 0.4, 1.7, 35, -40, 20),
        (0.8, -0.3, 1.8, -25, 45, -30),
        (-0.2, -0.8, 1.7, 45, 15, 60)
    ]
    for bx, by, bz, rx, ry, rz in branches:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=1.3, vertices=12, location=(bx, by, bz))
        bough = bpy.context.active_object
        bough.rotation_euler = (math.radians(rx), math.radians(ry), math.radians(rz))
        bough.data.materials.append(mat_gnarled)
        smooth_object(bough)
        objs.append(bough)
        
    # Spreading Cloud Canopies (Billowing foliage clumps)
    clumps = [
        (-0.9, 0.7, 2.3, 1.1, 0.9, 0.65),
        (1.1, -0.5, 2.4, 1.2, 1.0, 0.7),
        (-0.3, -1.1, 2.2, 1.0, 1.1, 0.6),
        (0.1, 0.1, 2.7, 1.3, 1.2, 0.8)
    ]
    for cx, cy, cz, sx, sy, sz in clumps:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.85, location=(cx, cy, cz))
        cl = bpy.context.active_object
        cl.scale = (sx, sy, sz)
        cl.data.materials.append(mat_canopy)
        smooth_object(cl)
        objs.append(cl)
        
    # Weeping Wisteria Hanging Clusters
    wist_pos = [(-1.2, 0.5, 1.8), (1.3, -0.2, 1.9), (-0.4, -1.3, 1.7), (0.7, 0.8, 2.0)]
    for wx, wy, wz in wist_pos:
        bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.22, depth=0.8, location=(wx, wy, wz))
        wist = bpy.context.active_object
        wist.rotation_euler = (math.radians(180), 0, 0)
        wist.data.materials.append(mat_wisteria)
        smooth_object(wist)
        objs.append(wist)
        
    # Golden Chrysanthemum Base Flowers
    for fi in range(8):
        fa = fi * (math.pi / 4.0)
        fx = math.cos(fa) * 0.9
        fy = math.sin(fa) * 0.9
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.14, location=(fx, fy, 0.25))
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
    
    glb = os.path.join(MODELS_DIR, "flora_olive_tree.glb")
    bpy.ops.export_scene.gltf(filepath=glb, export_format='GLB', use_selection=True)
    
    render_file = os.path.join(RENDERS_DIR, "flora_olive_tree_render.png")
    bpy.context.scene.render.filepath = render_file
    bpy.ops.render.render(write_still=True)
    print(f"Olive Tree finished: {glb} and {render_file}")

# ==============================================================================
# 3. GRAND COLONNADE RUIN (Curved Colonnade + Corinthian Archway + Flora)
# ==============================================================================
def build_grand_colonnade():
    clear_scene()
    setup_camera_and_lighting(target_z=2.3, ortho_scale=8.4)
    
    mat_marble = make_material("CarraraMarble", (0.9, 0.88, 0.82, 1.0), metallic=0.04, roughness=0.35)
    mat_brass = make_material("ArchBrass", (0.88, 0.68, 0.22, 1.0), metallic=0.92, roughness=0.22)
    mat_gold_flower = make_material("ChrysanthemumGold", (0.95, 0.72, 0.08, 1.0), metallic=0.05, roughness=0.5)
    mat_peony = make_material("PeonyPink", (0.9, 0.38, 0.55, 1.0), metallic=0.0, roughness=0.55)
    mat_ivy = make_material("IvyGreen", (0.18, 0.42, 0.16, 1.0), metallic=0.0, roughness=0.6)
    
    objs = []
    
    # Curved Stepped Plinth Foundation
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.15))
    found = bpy.context.active_object
    found.scale = (4.4, 1.4, 0.3)
    found.data.materials.append(mat_marble)
    objs.append(found)
    
    # 4 Corinthian Fluted Columns in Arch Colonnade
    col_x_list = [-1.6, -0.6, 0.6, 1.6]
    for c_i, cx in enumerate(col_x_list):
        # Column Base
        bpy.ops.mesh.primitive_cube_add(size=0.6, location=(cx, 0, 0.4))
        cbase = bpy.context.active_object
        cbase.scale = (1, 1, 0.3)
        cbase.data.materials.append(mat_marble)
        objs.append(cbase)
        
        # Fluted Column (One broken on right for ruin aesthetic!)
        col_height = 2.4 if c_i != 3 else 1.2
        col_z = 0.55 + col_height * 0.5
        bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=col_height, vertices=20, location=(cx, 0, col_z))
        col = bpy.context.active_object
        col.data.materials.append(mat_marble)
        smooth_object(col)
        objs.append(col)
        
        # Capital (for standing columns)
        if c_i != 3:
            bpy.ops.mesh.primitive_cube_add(size=0.55, location=(cx, 0, 2.9))
            ccap = bpy.context.active_object
            ccap.scale = (1, 1, 0.4)
            ccap.data.materials.append(mat_marble)
            objs.append(ccap)
        else:
            # Fallen Column Drum on Ground
            bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.7, vertices=16, location=(cx + 0.4, 0.4, 0.3))
            fdrum = bpy.context.active_object
            fdrum.rotation_euler = (math.radians(90), 0, math.radians(35))
            fdrum.data.materials.append(mat_marble)
            smooth_object(fdrum)
            objs.append(fdrum)
            
    # Spanning Architrave Beam Across First 3 Columns
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.5, 0, 3.25))
    beam = bpy.context.active_object
    beam.scale = (3.0, 0.65, 0.35)
    beam.data.materials.append(mat_marble)
    objs.append(beam)
    
    # Classical Triangular Pediment Center
    bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=1.2, depth=0.65, location=(-0.5, 0, 3.8))
    ped = bpy.context.active_object
    ped.rotation_euler = (math.radians(90), 0, math.radians(90))
    ped.data.materials.append(mat_marble)
    objs.append(ped)
    
    # Antique Brass Relief Bracket Under Architrave
    for bx in [-1.1, 0.1]:
        bpy.ops.mesh.primitive_cube_add(size=0.25, location=(bx, 0.28, 3.05))
        b_brk = bpy.context.active_object
        b_brk.scale = (0.6, 0.1, 0.6)
        b_brk.data.materials.append(mat_brass)
        objs.append(b_brk)
        
    # Peonies and Chrysanthemums Growing Around Base and Fallen Drum
    for f_i in range(16):
        fx = -2.0 + f_i * 0.26
        fy = 0.4 + (f_i % 3) * 0.18
        fz = 0.35 + (f_i % 2) * 0.1
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.14, location=(fx, fy, fz))
        fl = bpy.context.active_object
        fl.scale = (1, 1, 0.6)
        fl.data.materials.append(mat_peony if f_i % 2 == 0 else mat_gold_flower)
        smooth_object(fl)
        objs.append(fl)
        
    # Climbing Ivy Tendrils on Leftmost Column
    for step in range(12):
        ang = step * 0.6
        ix = -1.6 + math.cos(ang) * 0.25
        iy = math.sin(ang) * 0.25
        iz = 0.6 + step * 0.18
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.07, location=(ix, iy, iz))
        leaf = bpy.context.active_object
        leaf.scale = (1, 1, 0.4)
        leaf.data.materials.append(mat_ivy)
        smooth_object(leaf)
        objs.append(leaf)
        
    # Export & Render
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    
    glb = os.path.join(MODELS_DIR, "ruin_grand_colonnade.glb")
    bpy.ops.export_scene.gltf(filepath=glb, export_format='GLB', use_selection=True)
    
    render_file = os.path.join(RENDERS_DIR, "ruin_grand_colonnade_render.png")
    bpy.context.scene.render.filepath = render_file
    bpy.ops.render.render(write_still=True)
    print(f"Grand Colonnade finished: {glb} and {render_file}")

# ==============================================================================
# 4. WILDFLOWER MEADOW CLUSTER (Multi-Layered Botanical Accents)
# ==============================================================================
def build_wildflower_cluster():
    clear_scene()
    setup_camera_and_lighting(target_z=1.0, ortho_scale=3.8)
    
    mat_moss = make_material("MossyPaver", (0.24, 0.44, 0.20, 1.0), metallic=0.0, roughness=0.6)
    mat_gold_flower = make_material("GoldChrysanthemum", (0.95, 0.72, 0.08, 1.0), metallic=0.05, roughness=0.5)
    mat_peony = make_material("PeonyPink", (0.9, 0.38, 0.55, 1.0), metallic=0.0, roughness=0.55)
    mat_lavender = make_material("AlpineLavender", (0.58, 0.45, 0.82, 1.0), metallic=0.0, roughness=0.6)
    mat_brass_seed = make_material("BrassClockworkSeed", (0.88, 0.68, 0.22, 1.0), metallic=0.92, roughness=0.22)
    mat_cyan_spore = make_material("CyanManaSpore", (0.0, 0.95, 0.88, 1.0), emission=(0.0, 0.95, 0.88, 1.0), emission_strength=4.5)
    
    objs = []
    
    # Mossy Turf Paver Mound
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.2, location=(0, 0, -0.4))
    mound = bpy.context.active_object
    mound.scale = (1.4, 1.2, 0.45)
    mound.data.materials.append(mat_moss)
    smooth_object(mound)
    objs.append(mound)
    
    # Golden Chrysanthemums Clump
    for c_i in range(8):
        ca = c_i * (math.pi / 4.0) + 0.2
        cx = math.cos(ca) * (0.35 + (c_i % 3) * 0.15)
        cy = math.sin(ca) * (0.35 + (c_i % 3) * 0.15)
        cz = 0.3 + (c_i % 2) * 0.15
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(cx, cy, cz))
        chrys = bpy.context.active_object
        chrys.scale = (1, 1, 0.55)
        chrys.data.materials.append(mat_gold_flower)
        smooth_object(chrys)
        objs.append(chrys)
        
    # Lush Blooming Peonies
    for p_i in range(5):
        pa = p_i * (math.pi / 2.5) + 0.6
        px = math.cos(pa) * 0.75
        py = math.sin(pa) * 0.65
        pz = 0.25 + (p_i % 2) * 0.12
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=(px, py, pz))
        peon = bpy.context.active_object
        peon.scale = (1.1, 1.1, 0.65)
        peon.data.materials.append(mat_peony)
        smooth_object(peon)
        objs.append(peon)
        
    # Tall Spikes of Alpine Lavender
    for l_i in range(9):
        la = l_i * (math.pi / 4.5)
        lx = math.cos(la) * 0.95
        ly = math.sin(la) * 0.85
        lz = 0.55 + (l_i % 3) * 0.15
        bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.7, vertices=8, location=(lx, ly, lz))
        lav = bpy.context.active_object
        lav.data.materials.append(mat_lavender)
        smooth_object(lav)
        objs.append(lav)
        
    # Clockwork Brass Seed Pod in Center
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.14, location=(0, 0, 0.45))
    seed = bpy.context.active_object
    seed.data.materials.append(mat_brass_seed)
    smooth_object(seed)
    objs.append(seed)
    
    # Glowing Cyan Mana Pollen Spores Hovering
    for s_i in range(6):
        sa = s_i * (math.pi / 3.0)
        sx = math.cos(sa) * 0.45
        sy = math.sin(sa) * 0.45
        sz = 0.65 + (s_i % 3) * 0.2
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.06, location=(sx, sy, sz))
        spore = bpy.context.active_object
        spore.data.materials.append(mat_cyan_spore)
        objs.append(spore)
        
    # Export & Render
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    
    glb = os.path.join(MODELS_DIR, "flora_wildflower_cluster.glb")
    bpy.ops.export_scene.gltf(filepath=glb, export_format='GLB', use_selection=True)
    
    render_file = os.path.join(RENDERS_DIR, "flora_wildflower_cluster_render.png")
    bpy.context.scene.render.filepath = render_file
    bpy.ops.render.render(write_still=True)
    print(f"Wildflower Cluster finished: {glb} and {render_file}")

if __name__ == "__main__":
    print("=== STARTING GENERATION OF FLORA, TREES & RUIN ASSETS ===")
    build_cypress_tree()
    build_olive_tree()
    build_grand_colonnade()
    build_wildflower_cluster()
    print("=== ALL FLORA, TREES & RUIN ASSETS GENERATED AND EXPORTED SUCCESSFULLY ===")
