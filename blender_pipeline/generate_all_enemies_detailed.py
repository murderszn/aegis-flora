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

def setup_camera_and_lighting(target_z=2.0, ortho_scale=6.0):
    cam_data = bpy.data.cameras.new(name="IsoCam")
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = ortho_scale
    cam = bpy.data.objects.new("IsoCam", cam_data)
    bpy.context.collection.objects.link(cam)
    
    cam.location = (7.0, -7.0, 5.5 + target_z)
    cam.rotation_euler = (math.radians(54.736), 0, math.radians(45))
    bpy.context.scene.camera = cam
    
    # Key Sun (Warm Diesel Gold)
    sun_data = bpy.data.lights.new("SunKey", 'SUN')
    sun_data.energy = 5.0
    sun_data.color = (1.0, 0.95, 0.85)
    sun = bpy.data.objects.new("SunKey", sun_data)
    sun.rotation_euler = (math.radians(45), math.radians(25), math.radians(35))
    bpy.context.collection.objects.link(sun)
    
    # Fill Sun (Teal Ambient)
    fill_data = bpy.data.lights.new("FillTeal", 'SUN')
    fill_data.energy = 2.5
    fill_data.color = (0.15, 0.55, 0.65)
    fill = bpy.data.objects.new("FillTeal", fill_data)
    fill.rotation_euler = (math.radians(-35), math.radians(-15), math.radians(-130))
    bpy.context.collection.objects.link(fill)
    
    # Rim Light (Intense Amber Hazard Glow)
    rim_data = bpy.data.lights.new("RimAmber", 'POINT')
    rim_data.energy = 300.0
    rim_data.color = (1.0, 0.7, 0.2)
    rim = bpy.data.objects.new("RimAmber", rim_data)
    rim.location = (-5.0, 5.0, target_z + 4.0)
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
# 1. SKITTER SCOUT (Hexapod Arachnid Automata)
# ==============================================================================
def build_skitter_scout():
    clear_scene()
    setup_camera_and_lighting(target_z=1.0, ortho_scale=4.2)
    
    mat_iron = make_material("ScoutIron", (0.28, 0.30, 0.32, 1.0), metallic=0.88, roughness=0.35)
    mat_brass = make_material("ScoutBrass", (0.85, 0.65, 0.22, 1.0), metallic=0.92, roughness=0.25)
    mat_cyan_eye = make_material("CyanSensor", (0.0, 0.98, 0.9, 1.0), emission=(0.0, 0.98, 0.9, 1.0), emission_strength=5.0)
    mat_joint = make_material("DarkJoint", (0.12, 0.12, 0.14, 1.0), metallic=0.95, roughness=0.2)
    
    objs = []
    
    # Cephalothorax (Front Head Chassis)
    bpy.ops.mesh.primitive_cube_add(size=0.7, location=(0, -0.4, 0.65))
    head = bpy.context.active_object
    head.scale = (1.1, 0.9, 0.6)
    head.data.materials.append(mat_iron)
    objs.append(head)
    
    # Front Head Brass Bezel
    bpy.ops.mesh.primitive_cube_add(size=0.6, location=(0, -0.72, 0.65))
    visor = bpy.context.active_object
    visor.scale = (0.9, 0.15, 0.45)
    visor.data.materials.append(mat_brass)
    objs.append(visor)
    
    # Cluster of 4 Glowing Cyan Sensor Eyes
    for ex, ez in [(-0.16, 0.72), (0.16, 0.72), (-0.08, 0.6), (0.08, 0.6)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.15, vertices=12, location=(ex, -0.78, ez))
        eye = bpy.context.active_object
        eye.rotation_euler = (math.radians(90), 0, 0)
        eye.data.materials.append(mat_cyan_eye)
        smooth_object(eye)
        objs.append(eye)
        
    # Abdomen (Rear Spherical Clockwork Carapace)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.65, location=(0, 0.45, 0.8))
    ab = bpy.context.active_object
    ab.scale = (1.0, 1.3, 0.85)
    ab.data.materials.append(mat_iron)
    smooth_object(ab)
    objs.append(ab)
    
    # Abdomen Brass Carapace Ribs
    for r_y in [0.2, 0.5, 0.8]:
        bpy.ops.mesh.primitive_torus_add(major_radius=0.66, minor_radius=0.035, major_segments=24, minor_segments=12, location=(0, r_y, 0.8))
        rib = bpy.context.active_object
        rib.rotation_euler = (math.radians(90), 0, 0)
        rib.data.materials.append(mat_brass)
        smooth_object(rib)
        objs.append(rib)
        
    # Miniature Exhaust Smoke Pipe
    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.5, vertices=12, location=(0, 0.85, 1.35))
    stack = bpy.context.active_object
    stack.rotation_euler = (math.radians(-30), 0, 0)
    stack.data.materials.append(mat_iron)
    smooth_object(stack)
    objs.append(stack)
    
    # 6 Articulated Spider Legs (3 Left, 3 Right)
    leg_offsets = [(-0.45, -0.3), (-0.55, 0.0), (-0.45, 0.35)]
    for side in [-1, 1]:
        for idx, (lx, ly) in enumerate(leg_offsets):
            x_pos = side * abs(lx)
            # Coxa Hip Joint
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(x_pos, ly, 0.6))
            hip = bpy.context.active_object
            hip.data.materials.append(mat_joint)
            objs.append(hip)
            
            # Femur (Upper Leg Segment, arched upward)
            femur_angle = math.radians(side * (45 + idx * 15))
            fx = x_pos + side * 0.4
            fy = ly + (idx - 1) * 0.15
            fz = 0.95
            bpy.ops.mesh.primitive_cylinder_add(radius=0.045, depth=0.8, vertices=8, location=(fx, fy, fz))
            femur = bpy.context.active_object
            femur.rotation_euler = (math.radians(15), math.radians(side * -45), femur_angle)
            femur.data.materials.append(mat_brass)
            smooth_object(femur)
            objs.append(femur)
            
            # Tibia (Lower Leg Segment with Ground Claw)
            tx = x_pos + side * 0.85
            ty = ly + (idx - 1) * 0.3
            tz = 0.35
            bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.04, depth=0.9, location=(tx, ty, tz))
            tibia = bpy.context.active_object
            tibia.rotation_euler = (math.radians(-10), math.radians(side * 35), femur_angle)
            tibia.data.materials.append(mat_iron)
            smooth_object(tibia)
            objs.append(tibia)
            
    # Export & Render
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    
    glb = os.path.join(MODELS_DIR, "enemy_skitter_scout.glb")
    bpy.ops.export_scene.gltf(filepath=glb, export_format='GLB', use_selection=True)
    
    render_file = os.path.join(RENDERS_DIR, "enemy_skitter_scout_render.png")
    bpy.context.scene.render.filepath = render_file
    bpy.ops.render.render(write_still=True)
    print(f"Skitter Scout finished: {glb} and {render_file}")

# ==============================================================================
# 2. TREAD TANK (Heavy Armored Diesel Fortress Tank)
# ==============================================================================
def build_tread_tank():
    clear_scene()
    setup_camera_and_lighting(target_z=1.4, ortho_scale=5.2)
    
    mat_armor = make_material("TankArmor", (0.24, 0.26, 0.28, 1.0), metallic=0.9, roughness=0.38)
    mat_brass = make_material("TankBrass", (0.85, 0.65, 0.22, 1.0), metallic=0.92, roughness=0.25)
    mat_tread = make_material("CaterpillarTread", (0.14, 0.14, 0.15, 1.0), metallic=0.7, roughness=0.6)
    mat_headlight = make_material("AmberHeadlight", (1.0, 0.7, 0.15, 1.0), emission=(1.0, 0.7, 0.15, 1.0), emission_strength=4.5)
    
    objs = []
    
    # Heavy Hull Lower Chassis
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.65))
    chassis = bpy.context.active_object
    chassis.scale = (1.6, 2.4, 0.7)
    chassis.data.materials.append(mat_armor)
    objs.append(chassis)
    
    # Front Wedge Cowcatcher Plow
    bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=0.9, depth=1.6, location=(0, -1.35, 0.45))
    plow = bpy.context.active_object
    plow.rotation_euler = (math.radians(90), 0, math.radians(90))
    plow.data.materials.append(mat_brass)
    objs.append(plow)
    
    # Dual Caterpillar Tread Pods (Left & Right)
    for t_side in [-1, 1]:
        tx = t_side * 0.95
        # Main Tread Loop
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(tx, 0, 0.45))
        tread = bpy.context.active_object
        tread.scale = (0.45, 2.5, 0.65)
        tread.data.materials.append(mat_tread)
        objs.append(tread)
        
        # Armored Track Mudguard Skirt
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(tx, 0, 0.8))
        skirt = bpy.context.active_object
        skirt.scale = (0.52, 2.6, 0.1)
        skirt.data.materials.append(mat_brass)
        objs.append(skirt)
        
        # 5 Road Wheels per side
        for w_i in range(5):
            wy = -0.9 + w_i * 0.45
            bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.48, vertices=16, location=(tx, wy, 0.35))
            wheel = bpy.context.active_object
            wheel.rotation_euler = (0, math.radians(90), 0)
            wheel.data.materials.append(mat_armor)
            smooth_object(wheel)
            objs.append(wheel)
            
    # Revolving Turret Platform
    bpy.ops.mesh.primitive_cylinder_add(radius=0.75, depth=0.55, vertices=20, location=(0, -0.15, 1.25))
    turret = bpy.context.active_object
    turret.data.materials.append(mat_armor)
    smooth_object(turret)
    objs.append(turret)
    
    # Cast Brass Turret Mantlet Ring
    bpy.ops.mesh.primitive_torus_add(major_radius=0.78, minor_radius=0.05, major_segments=24, minor_segments=12, location=(0, -0.15, 1.25))
    t_ring = bpy.context.active_object
    t_ring.data.materials.append(mat_brass)
    smooth_object(t_ring)
    objs.append(t_ring)
    
    # Twin Heavy Rifled Cannons
    for bx in [-0.22, 0.22]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.09, depth=1.8, vertices=16, location=(bx, -1.3, 1.3))
        barrel = bpy.context.active_object
        barrel.rotation_euler = (math.radians(90), 0, 0)
        barrel.data.materials.append(mat_armor)
        smooth_object(barrel)
        objs.append(barrel)
        
        # Brass Muzzle Brake
        bpy.ops.mesh.primitive_cylinder_add(radius=0.13, depth=0.25, vertices=16, location=(bx, -2.15, 1.3))
        brake = bpy.context.active_object
        brake.rotation_euler = (math.radians(90), 0, 0)
        brake.data.materials.append(mat_brass)
        smooth_object(brake)
        objs.append(brake)
        
    # Twin Amber Headlight Lanterns
    for hx in [-0.55, 0.55]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=0.18, vertices=16, location=(hx, -1.25, 0.85))
        lamp = bpy.context.active_object
        lamp.rotation_euler = (math.radians(90), 0, 0)
        lamp.data.materials.append(mat_headlight)
        smooth_object(lamp)
        objs.append(lamp)
        
    # Twin Aft Boiler Smokestacks
    for sx in [-0.35, 0.35]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=1.1, vertices=16, location=(sx, 0.9, 1.4))
        stack = bpy.context.active_object
        stack.data.materials.append(mat_armor)
        smooth_object(stack)
        objs.append(stack)
        
    # Export & Render
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    
    glb = os.path.join(MODELS_DIR, "enemy_tread_tank.glb")
    bpy.ops.export_scene.gltf(filepath=glb, export_format='GLB', use_selection=True)
    
    render_file = os.path.join(RENDERS_DIR, "enemy_tread_tank_render.png")
    bpy.context.scene.render.filepath = render_file
    bpy.ops.render.render(write_still=True)
    print(f"Tread Tank finished: {glb} and {render_file}")

# ==============================================================================
# 3. ROTOR DRONE (Clockwork Aerial Gyrocopter)
# ==============================================================================
def build_rotor_drone():
    clear_scene()
    setup_camera_and_lighting(target_z=1.8, ortho_scale=4.5)
    
    mat_iron = make_material("DroneIron", (0.3, 0.32, 0.35, 1.0), metallic=0.88, roughness=0.35)
    mat_brass = make_material("DroneBrass", (0.85, 0.65, 0.22, 1.0), metallic=0.92, roughness=0.25)
    mat_prop = make_material("PropellerBronze", (0.6, 0.45, 0.2, 1.0), metallic=0.9, roughness=0.22)
    mat_lens = make_material("SearchlightLens", (0.0, 0.95, 0.88, 1.0), emission=(0.0, 0.95, 0.88, 1.0), emission_strength=4.5)
    
    objs = []
    
    # Aerodynamic Tear-Drop Chassis Body
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.55, location=(0, 0, 1.8))
    body = bpy.context.active_object
    body.scale = (0.85, 1.4, 0.85)
    body.data.materials.append(mat_iron)
    smooth_object(body)
    objs.append(body)
    
    # Pointed Brass Tail Cone
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.45, depth=0.8, location=(0, 0.9, 1.8))
    tail = bpy.context.active_object
    tail.rotation_euler = (math.radians(-90), 0, 0)
    tail.data.materials.append(mat_brass)
    smooth_object(tail)
    objs.append(tail)
    
    # Underslung Gimbal Searchlight Lens
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=(0, -0.3, 1.4))
    lens = bpy.context.active_object
    lens.scale = (1, 1, 0.6)
    lens.data.materials.append(mat_lens)
    smooth_object(lens)
    objs.append(lens)
    
    # Searchlight Brass Bezel
    bpy.ops.mesh.primitive_torus_add(major_radius=0.23, minor_radius=0.035, major_segments=24, minor_segments=12, location=(0, -0.3, 1.38))
    l_ring = bpy.context.active_object
    l_ring.data.materials.append(mat_brass)
    smooth_object(l_ring)
    objs.append(l_ring)
    
    # Central Rotor Mast Tower
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.7, vertices=12, location=(0, 0, 2.5))
    mast = bpy.context.active_object
    mast.data.materials.append(mat_brass)
    objs.append(mast)
    
    # Dual Counter-Rotating Rotor Assemblies (Upper & Lower)
    for r_z, r_rot in [(2.6, 15), (2.85, -55)]:
        # Rotor Hub
        bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=0.12, vertices=16, location=(0, 0, r_z))
        hub = bpy.context.active_object
        hub.data.materials.append(mat_iron)
        smooth_object(hub)
        objs.append(hub)
        
        # 3 Rotor Blades
        for b_i in range(3):
            b_ang = math.radians(r_rot + b_i * 120)
            bx = math.cos(b_ang) * 0.9
            by = math.sin(b_ang) * 0.9
            bpy.ops.mesh.primitive_cube_add(size=0.3, location=(bx, by, r_z))
            blade = bpy.context.active_object
            blade.scale = (5.8, 0.45, 0.08)
            blade.rotation_euler = (0, 0, b_ang + math.radians(90))
            blade.data.materials.append(mat_prop)
            objs.append(blade)
            
    # Twin Outrigger Stabilizer Skids
    for s_side in [-1, 1]:
        sx = s_side * 0.55
        bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=1.2, vertices=8, location=(sx, 0, 1.15))
        skid = bpy.context.active_object
        skid.rotation_euler = (math.radians(90), 0, 0)
        skid.data.materials.append(mat_brass)
        objs.append(skid)
        
    # Export & Render
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    
    glb = os.path.join(MODELS_DIR, "enemy_rotor_drone.glb")
    bpy.ops.export_scene.gltf(filepath=glb, export_format='GLB', use_selection=True)
    
    render_file = os.path.join(RENDERS_DIR, "enemy_rotor_drone_render.png")
    bpy.context.scene.render.filepath = render_file
    bpy.ops.render.render(write_still=True)
    print(f"Rotor Drone finished: {glb} and {render_file}")

# ==============================================================================
# 4. DIESEL WALKER (High-Detail Heavy Bipedal War Mech)
# ==============================================================================
def build_diesel_walker_detailed():
    clear_scene()
    setup_camera_and_lighting(target_z=2.2, ortho_scale=5.8)
    
    mat_iron = make_material("WalkerArmor", (0.28, 0.30, 0.32, 1.0), metallic=0.9, roughness=0.36)
    mat_brass = make_material("WalkerBrass", (0.85, 0.65, 0.22, 1.0), metallic=0.92, roughness=0.25)
    mat_joint = make_material("JointHydraulic", (0.12, 0.12, 0.14, 1.0), metallic=0.95, roughness=0.2)
    mat_optic = make_material("AmberOptic", (1.0, 0.65, 0.1, 1.0), emission=(1.0, 0.65, 0.1, 1.0), emission_strength=5.5)
    
    objs = []
    
    # Massive Boiler Chassis Torso
    bpy.ops.mesh.primitive_cylinder_add(radius=0.85, depth=1.4, vertices=24, location=(0, 0, 2.5))
    torso = bpy.context.active_object
    torso.rotation_euler = (0, math.radians(90), 0)
    torso.data.materials.append(mat_iron)
    smooth_object(torso)
    objs.append(torso)
    
    # Cast Brass Riveted Chest Armor Breastplate
    bpy.ops.mesh.primitive_cube_add(size=0.9, location=(0, -0.7, 2.5))
    chest = bpy.context.active_object
    chest.scale = (1.2, 0.3, 0.95)
    chest.data.materials.append(mat_brass)
    objs.append(chest)
    
    # Visor Optic Array (Dual Amber Headlight Lenses)
    for eye_x in [-0.28, 0.28]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.14, depth=0.2, vertices=16, location=(eye_x, -0.88, 2.55))
        eye = bpy.context.active_object
        eye.rotation_euler = (math.radians(90), 0, 0)
        eye.data.materials.append(mat_optic)
        smooth_object(eye)
        objs.append(eye)
        
        # Brass Eyecup Bezel
        bpy.ops.mesh.primitive_torus_add(major_radius=0.16, minor_radius=0.035, major_segments=20, minor_segments=10, location=(eye_x, -0.88, 2.55))
        bezel = bpy.context.active_object
        bezel.rotation_euler = (math.radians(90), 0, 0)
        bezel.data.materials.append(mat_brass)
        smooth_object(bezel)
        objs.append(bezel)
        
    # Twin Aft Exhaust Smokestacks
    for sx in [-0.35, 0.35]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.14, depth=1.3, vertices=16, location=(sx, 0.55, 3.4))
        stack = bpy.context.active_object
        stack.data.materials.append(mat_iron)
        smooth_object(stack)
        objs.append(stack)
        
    # Right Arm: Heavy Rotary Autocannon Arm Pod
    bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.6, vertices=16, location=(1.15, -0.2, 2.3))
    r_arm = bpy.context.active_object
    r_arm.data.materials.append(mat_brass)
    smooth_object(r_arm)
    objs.append(r_arm)
    
    for b_idx in range(4):
        ba = b_idx * (math.pi / 2.0)
        bx = 1.15 + math.cos(ba) * 0.1
        bz = 2.3 + math.sin(ba) * 0.1
        bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=1.1, vertices=12, location=(bx, -0.8, bz))
        b_barrel = bpy.context.active_object
        b_barrel.rotation_euler = (math.radians(90), 0, 0)
        b_barrel.data.materials.append(mat_iron)
        smooth_object(b_barrel)
        objs.append(b_barrel)
        
    # Left Arm: Articulated Hydraulic Siege Claw Pod
    bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.6, vertices=16, location=(-1.15, -0.2, 2.3))
    l_arm = bpy.context.active_object
    l_arm.data.materials.append(mat_brass)
    smooth_object(l_arm)
    objs.append(l_arm)
    
    for c_z in [2.15, 2.45]:
        bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.08, depth=0.8, location=(-1.15, -0.75, c_z))
        claw = bpy.context.active_object
        claw.rotation_euler = (math.radians(-90), 0, 0)
        claw.data.materials.append(mat_iron)
        smooth_object(claw)
        objs.append(claw)
        
    # Pelvis Girder
    bpy.ops.mesh.primitive_cube_add(size=0.8, location=(0, 0, 1.7))
    pelvis = bpy.context.active_object
    pelvis.scale = (1.4, 0.7, 0.4)
    pelvis.data.materials.append(mat_joint)
    objs.append(pelvis)
    
    # Heavy Articulated Hydraulic Legs (Left & Right)
    for leg_side in [-1, 1]:
        lx = leg_side * 0.8
        # Spherical Hip Joint
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25, location=(lx, 0, 1.65))
        hip = bpy.context.active_object
        hip.data.materials.append(mat_joint)
        objs.append(hip)
        
        # Thigh Hydraulic Piston
        bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=1.1, vertices=16, location=(lx, 0.15, 1.2))
        thigh = bpy.context.active_object
        thigh.rotation_euler = (math.radians(22), 0, 0)
        thigh.data.materials.append(mat_brass)
        smooth_object(thigh)
        objs.append(thigh)
        
        # Knee Joint
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=(lx, 0.32, 0.75))
        knee = bpy.context.active_object
        knee.data.materials.append(mat_joint)
        objs.append(knee)
        
        # Armored Lower Shin
        bpy.ops.mesh.primitive_cylinder_add(radius=0.16, depth=1.0, vertices=16, location=(lx, 0.15, 0.35))
        shin = bpy.context.active_object
        shin.rotation_euler = (math.radians(-18), 0, 0)
        shin.data.materials.append(mat_iron)
        smooth_object(shin)
        objs.append(shin)
        
        # Heavy Cleated Tread Foot
        bpy.ops.mesh.primitive_cube_add(size=0.55, location=(lx, 0, 0.1))
        foot = bpy.context.active_object
        foot.scale = (1.1, 1.7, 0.35)
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
    print(f"Detailed Diesel Walker finished: {glb} and {render_file}")

# ==============================================================================
# 5. GOLIATH COLOSSUS (Colossal Multi-Deck Walking Fortress Titan)
# ==============================================================================
def build_goliath_colossus_detailed():
    clear_scene()
    setup_camera_and_lighting(target_z=2.5, ortho_scale=7.5)
    
    mat_armor = make_material("ColossusArmor", (0.22, 0.23, 0.25, 1.0), metallic=0.92, roughness=0.34)
    mat_brass = make_material("ColossusBrass", (0.82, 0.62, 0.18, 1.0), metallic=0.94, roughness=0.24)
    mat_firebox = make_material("FurnaceGlow", (1.0, 0.35, 0.05, 1.0), emission=(1.0, 0.35, 0.05, 1.0), emission_strength=6.0)
    mat_red_eye = make_material("CrimsonEye", (1.0, 0.08, 0.12, 1.0), emission=(1.0, 0.08, 0.12, 1.0), emission_strength=7.0)
    mat_joint = make_material("TitanJoint", (0.1, 0.1, 0.12, 1.0), metallic=0.95, roughness=0.2)
    
    objs = []
    
    # Colossal Boiler Torso (Tiered Chassis)
    bpy.ops.mesh.primitive_cylinder_add(radius=1.5, depth=2.4, vertices=28, location=(0, 0, 3.2))
    torso = bpy.context.active_object
    torso.rotation_euler = (math.radians(90), 0, 0)
    torso.data.materials.append(mat_armor)
    smooth_object(torso)
    objs.append(torso)
    
    # Heavy Cast-Brass Chest Breastplate
    bpy.ops.mesh.primitive_cube_add(size=1.4, location=(0, -1.2, 3.2))
    chest = bpy.context.active_object
    chest.scale = (1.25, 0.45, 1.1)
    chest.data.materials.append(mat_brass)
    objs.append(chest)
    
    # Cyclopean Crimson Optic Eye Core
    bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=0.3, vertices=24, location=(0, -1.55, 3.35))
    eye = bpy.context.active_object
    eye.rotation_euler = (math.radians(90), 0, 0)
    eye.data.materials.append(mat_red_eye)
    smooth_object(eye)
    objs.append(eye)
    
    # Multi-Tier Geared Brass Eye Bezel
    for b_rad, b_depth in [(0.52, 0.08), (0.62, 0.06)]:
        bpy.ops.mesh.primitive_torus_add(major_radius=b_rad, minor_radius=b_depth, major_segments=24, minor_segments=12, location=(0, -1.58, 3.35))
        bezel = bpy.context.active_object
        bezel.rotation_euler = (math.radians(90), 0, 0)
        bezel.data.materials.append(mat_brass)
        smooth_object(bezel)
        objs.append(bezel)
        
    # Burning Furnace Firebox Grate Underneath
    bpy.ops.mesh.primitive_cube_add(size=0.8, location=(0, -0.6, 2.2))
    fire = bpy.context.active_object
    fire.scale = (1.1, 0.6, 0.5)
    fire.data.materials.append(mat_firebox)
    objs.append(fire)
    
    # Quad Exhaust Smokestacks (Aft Boiler)
    for sx, sy in [(-0.7, 0.6), (0.7, 0.6), (-0.4, 1.0), (0.4, 1.0)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=1.7, vertices=16, location=(sx, sy, 4.6))
        pipe = bpy.context.active_object
        pipe.data.materials.append(mat_armor)
        smooth_object(pipe)
        objs.append(pipe)
        
    # Fortress Pauldron Armor (Shoulders)
    for p_side in [-1, 1]:
        px = p_side * 2.1
        # Dome Pauldron
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.95, location=(px, 0, 3.7))
        paul = bpy.context.active_object
        paul.scale = (0.75, 1.3, 0.95)
        paul.data.materials.append(mat_brass)
        smooth_object(paul)
        objs.append(paul)
        
        # Dual Fortress Siege Cannons per Arm
        for cz in [2.6, 2.2]:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=2.2, vertices=16, location=(px, -0.8, cz))
            cannon = bpy.context.active_object
            cannon.rotation_euler = (math.radians(35), 0, 0)
            cannon.data.materials.append(mat_armor)
            smooth_object(cannon)
            objs.append(cannon)
            
    # Colossal Pelvis & Hydraulic Legs
    bpy.ops.mesh.primitive_cube_add(size=1.2, location=(0, 0, 2.0))
    pelvis = bpy.context.active_object
    pelvis.scale = (1.8, 0.9, 0.6)
    pelvis.data.materials.append(mat_joint)
    objs.append(pelvis)
    
    for l_side in [-1, 1]:
        lx = l_side * 1.3
        # Massive Spherical Hip
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.45, location=(lx, 0, 1.85))
        hip = bpy.context.active_object
        hip.data.materials.append(mat_joint)
        objs.append(hip)
        
        # Heavy Thigh Cylinder
        bpy.ops.mesh.primitive_cylinder_add(radius=0.35, depth=1.5, vertices=20, location=(lx, 0.2, 1.3))
        thigh = bpy.context.active_object
        thigh.rotation_euler = (math.radians(25), 0, 0)
        thigh.data.materials.append(mat_brass)
        smooth_object(thigh)
        objs.append(thigh)
        
        # Massive Knee Joint
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.42, location=(lx, 0.45, 0.75))
        knee = bpy.context.active_object
        knee.data.materials.append(mat_joint)
        objs.append(knee)
        
        # Lower Shin & Tread Foot
        bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=1.3, vertices=20, location=(lx, 0.2, 0.35))
        shin = bpy.context.active_object
        shin.rotation_euler = (math.radians(-20), 0, 0)
        shin.data.materials.append(mat_armor)
        smooth_object(shin)
        objs.append(shin)
        
        bpy.ops.mesh.primitive_cube_add(size=0.9, location=(lx, 0, 0.1))
        foot = bpy.context.active_object
        foot.scale = (1.2, 2.0, 0.4)
        foot.data.materials.append(mat_brass)
        objs.append(foot)
        
    # Export & Render
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    
    glb = os.path.join(MODELS_DIR, "enemy_goliath_colossus.glb")
    bpy.ops.export_scene.gltf(filepath=glb, export_format='GLB', use_selection=True)
    
    render_file = os.path.join(RENDERS_DIR, "enemy_goliath_colossus_render.png")
    bpy.context.scene.render.filepath = render_file
    bpy.ops.render.render(write_still=True)
    print(f"Colossal Goliath Boss finished: {glb} and {render_file}")

# ==============================================================================
# 6. ZEPPELIN SKY-HULL (Detailed Armored War-Dirigible)
# ==============================================================================
def build_zeppelin_sky_hull_detailed():
    clear_scene()
    setup_camera_and_lighting(target_z=2.0, ortho_scale=8.5)
    
    mat_hull_iron = make_material("HullIron", (0.34, 0.36, 0.38, 1.0), metallic=0.88, roughness=0.36)
    mat_brass_ribs = make_material("BrassRibs", (0.85, 0.65, 0.22, 1.0), metallic=0.92, roughness=0.25)
    mat_bronze_prop = make_material("PropBronze", (0.6, 0.45, 0.2, 1.0), metallic=0.9, roughness=0.22)
    mat_window = make_material("GondolaWindow", (1.0, 0.85, 0.4, 1.0), emission=(1.0, 0.85, 0.4, 1.0), emission_strength=4.0)
    
    objs = []
    
    # Streamlined Main Gasbag Hull
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.3, location=(0, 0, 2.2))
    hull = bpy.context.active_object
    hull.scale = (1.15, 2.6, 1.15)
    hull.data.materials.append(mat_hull_iron)
    smooth_object(hull)
    objs.append(hull)
    
    # Pointed Brass Nose Cone
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=1.1, depth=1.1, location=(0, -3.2, 2.2))
    nose = bpy.context.active_object
    nose.rotation_euler = (math.radians(-90), 0, 0)
    nose.data.materials.append(mat_brass_ribs)
    smooth_object(nose)
    objs.append(nose)
    
    # 5 Armored Brass Girdle Rings
    for ring_y in [-2.0, -1.0, 0.0, 1.0, 2.0]:
        bpy.ops.mesh.primitive_torus_add(major_radius=1.45, minor_radius=0.065, major_segments=32, minor_segments=12, location=(0, ring_y, 2.2))
        girdle = bpy.context.active_object
        girdle.rotation_euler = (math.radians(90), 0, 0)
        girdle.data.materials.append(mat_brass_ribs)
        smooth_object(girdle)
        objs.append(girdle)
        
    # Multi-Deck Suspended Command Gondola
    bpy.ops.mesh.primitive_cube_add(size=0.9, location=(0, -0.6, 0.8))
    gondola = bpy.context.active_object
    gondola.scale = (0.75, 2.3, 0.75)
    gondola.data.materials.append(mat_hull_iron)
    objs.append(gondola)
    
    # Forward Bridge Observation Bay Windows
    bpy.ops.mesh.primitive_cube_add(size=0.7, location=(0, -1.6, 0.8))
    bridge = bpy.context.active_object
    bridge.scale = (0.78, 0.28, 0.45)
    bridge.data.materials.append(mat_window)
    objs.append(bridge)
    
    # Top Deck Observation Cupola
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.45, location=(0, 0, 3.55))
    dome = bpy.context.active_object
    dome.scale = (1, 1.5, 0.6)
    dome.data.materials.append(mat_brass_ribs)
    smooth_object(dome)
    objs.append(dome)
    
    # Twin Heavy Aft Smokestacks
    for pipe_x in [-0.32, 0.32]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.13, depth=1.3, vertices=16, location=(pipe_x, 1.5, 3.6))
        pipe = bpy.context.active_object
        pipe.data.materials.append(mat_hull_iron)
        smooth_object(pipe)
        objs.append(pipe)
        
    # Twin Outrigger Propeller Engines (Left and Right)
    for prop_sign in [-1, 1]:
        px = prop_sign * 1.6
        # Engine Nacelle
        bpy.ops.mesh.primitive_cylinder_add(radius=0.26, depth=0.9, vertices=16, location=(px, 0.2, 1.8))
        nacelle = bpy.context.active_object
        nacelle.rotation_euler = (math.radians(90), 0, 0)
        nacelle.data.materials.append(mat_brass_ribs)
        smooth_object(nacelle)
        objs.append(nacelle)
        
        # 4-Blade Propeller
        bpy.ops.mesh.primitive_cylinder_add(radius=0.65, depth=0.04, vertices=8, location=(px, -0.3, 1.8))
        prop = bpy.context.active_object
        prop.rotation_euler = (math.radians(90), 0, 0)
        prop.data.materials.append(mat_bronze_prop)
        objs.append(prop)
        
    # Clockwork Empennage Tail Fins (Vertical and Horizontal)
    bpy.ops.mesh.primitive_cube_add(size=0.6, location=(0, 3.1, 2.2))
    v_fin = bpy.context.active_object
    v_fin.scale = (0.1, 1.5, 2.4)
    v_fin.data.materials.append(mat_brass_ribs)
    objs.append(v_fin)
    
    bpy.ops.mesh.primitive_cube_add(size=0.6, location=(0, 3.1, 2.2))
    h_fin = bpy.context.active_object
    h_fin.scale = (2.4, 1.5, 0.1)
    h_fin.data.materials.append(mat_brass_ribs)
    objs.append(h_fin)
    
    # Export & Render
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    
    glb = os.path.join(MODELS_DIR, "enemy_zeppelin_sky_hull.glb")
    bpy.ops.export_scene.gltf(filepath=glb, export_format='GLB', use_selection=True)
    
    render_file = os.path.join(RENDERS_DIR, "enemy_zeppelin_sky_hull_render.png")
    bpy.context.scene.render.filepath = render_file
    bpy.ops.render.render(write_still=True)
    print(f"Detailed Zeppelin finished: {glb} and {render_file}")

if __name__ == "__main__":
    print("=== STARTING GENERATION OF ALL DETAILED ENEMIES ===")
    build_skitter_scout()
    build_tread_tank()
    build_rotor_drone()
    build_diesel_walker_detailed()
    build_goliath_colossus_detailed()
    build_zeppelin_sky_hull_detailed()
    print("=== ALL 6 DETAILED ENEMIES GENERATED AND EXPORTED SUCCESSFULLY ===")
