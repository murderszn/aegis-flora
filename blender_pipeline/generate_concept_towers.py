"""Concept-art towers for Aegis Florae — Heliostat Orchid + Mycelium Bell.

Builds two game-ready tower meshes from assets/concepts/*.png, following the
established blender_pipeline conventions (palette, export_and_render, EEVEE
ortho preview renders). Run headless:

    Blender --background --python blender_pipeline/generate_concept_towers.py

Outputs (models/*.glb + renders/*.png):
    tower_heliostat_orchid, tower_mycelium_bell
"""
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

    # Cool Rim (Teal)
    rim_data = bpy.data.lights.new("RimCool", 'SUN')
    rim_data.energy = 2.2
    rim_data.color = (0.45, 0.75, 0.85)
    rim = bpy.data.objects.new("RimCool", rim_data)
    rim.rotation_euler = (math.radians(60), 0, math.radians(-135))
    bpy.context.collection.objects.link(rim)

    # Fill
    fill_data = bpy.data.lights.new("FillSoft", 'SUN')
    fill_data.energy = 0.9
    fill_data.color = (0.9, 0.9, 0.95)
    fill = bpy.data.objects.new("FillSoft", fill_data)
    fill.rotation_euler = (math.radians(30), 0, math.radians(150))
    bpy.context.collection.objects.link(fill)

    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024
    scene.render.film_transparent = True


def smooth_object(obj):
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
    print(f"  DONE {model_name}: {glb}")
    print(f"  DONE {render_name}: {render_file}")


def palette():
    """Canonical Aegis Florae PBR materials needed by the concept towers."""
    return {
        "marble":   make_material("ConceptMarble",     (0.90, 0.88, 0.82, 1.0), metallic=0.04, roughness=0.35),
        "marble_old": make_material("ConceptAgedMarble", (0.76, 0.73, 0.66, 1.0), metallic=0.04, roughness=0.55),
        "brass":    make_material("ConceptBrass",       (0.88, 0.68, 0.22, 1.0), metallic=0.92, roughness=0.22),
        "iron":     make_material("ConceptIron",        (0.18, 0.20, 0.22, 1.0), metallic=0.88, roughness=0.45),
        "ivory":    make_material("OrchidIvory",        (0.94, 0.90, 0.80, 1.0), metallic=0.00, roughness=0.42),
        "gold_leaf": make_material("GoldLeaf",          (0.95, 0.78, 0.30, 1.0), metallic=0.85, roughness=0.30),
        "mirror":   make_material("HeliostatGlass",     (0.75, 0.90, 0.95, 1.0), metallic=0.10, roughness=0.05),
        "crystal":  make_material("ManaCrystal",        (0.05, 0.85, 0.80, 1.0),
                                  emission=(0.0, 0.95, 0.85, 1.0), emission_strength=5.0),
        "spore":    make_material("SporeGlow",          (0.0, 0.95, 0.88, 1.0),
                                  emission=(0.0, 0.95, 0.88, 1.0), emission_strength=3.5),
        "cap":      make_material("MyceliumCap",        (0.82, 0.64, 0.86, 1.0), metallic=0.00, roughness=0.55),
        "stem":     make_material("MyceliumStem",       (0.88, 0.82, 0.70, 1.0), metallic=0.00, roughness=0.60),
        "chrys":    make_material("ConceptChrys",       (0.95, 0.72, 0.08, 1.0), metallic=0.05, roughness=0.50),
        "peony":    make_material("ConceptPeony",       (0.90, 0.38, 0.55, 1.0), metallic=0.00, roughness=0.55),
        "ivy":      make_material("ConceptIvy",         (0.18, 0.42, 0.16, 1.0), metallic=0.00, roughness=0.60),
    }


def _add_chrysanthemum(objs, mat, x, y, z, scale=0.18):
    """Dense multi-layered chrysanthemum flower head."""
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=scale * 0.85,
                                         location=(x, y, z))
    core = bpy.context.active_object
    core.scale = (1.0, 1.0, 0.6)
    core.data.materials.append(mat)
    smooth_object(core)
    objs.append(core)
    for p in range(8):
        pa = p * (math.pi / 4)
        px = x + math.cos(pa) * scale * 1.1
        py = y + math.sin(pa) * scale * 1.1
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=scale * 0.35, depth=scale * 1.8,
                                            location=(px, py, z - scale * 0.1))
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
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=scale,
                                         location=(x, y, z))
    bloom = bpy.context.active_object
    bloom.scale = (1.1, 1.1, 0.65)
    bloom.data.materials.append(mat)
    smooth_object(bloom)
    objs.append(bloom)
    for p in range(6):
        pa = p * (math.pi / 3) + 0.15
        px = x + math.cos(pa) * scale * 1.2
        py = y + math.sin(pa) * scale * 1.2
        bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=6, radius=scale * 0.55,
                                             location=(px, py, z - scale * 0.15))
        ruf = bpy.context.active_object
        ruf.scale = (1.0, 0.5, 0.4)
        ruf.rotation_euler = (0, 0, pa)
        ruf.data.materials.append(mat)
        smooth_object(ruf)
        objs.append(ruf)


def _add_ivy_trail(objs, mat, cx, cy, start_z, steps=10, radius=0.35, climb=0.15):
    """Spiral of small ivy leaves climbing up from (cx, cy, start_z)."""
    for i in range(steps):
        ang = i * 0.6
        ix = cx + math.cos(ang) * radius
        iy = cy + math.sin(ang) * radius
        iz = start_z + i * climb
        bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.06,
                                             location=(ix, iy, iz))
        leaf = bpy.context.active_object
        leaf.scale = (1.0, 1.0, 0.35)
        leaf.data.materials.append(mat)
        smooth_object(leaf)
        objs.append(leaf)


def _add_fluted_plinth(objs, P, base_xy=0.95, base_h=0.22, drum_r=0.32, drum_h=0.85, cap_xy=0.85):
    """Marble plinth: square footing + fluted drum + square capital. Returns top z."""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, base_h / 2))
    foot = bpy.context.active_object
    foot.scale = (base_xy, base_xy, base_h)
    foot.data.materials.append(P["marble_old"])
    objs.append(foot)

    z0 = base_h
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=drum_r, depth=drum_h,
                                        location=(0, 0, z0 + drum_h / 2))
    drum = bpy.context.active_object
    drum.data.materials.append(P["marble"])
    smooth_object(drum)
    objs.append(drum)
    # Fluting suggestion: 12 thin inset grooves (dark thin boxes hugging the drum)
    for f in range(12):
        fa = f * (math.pi / 6)
        fx = math.cos(fa) * (drum_r - 0.005)
        fy = math.sin(fa) * (drum_r - 0.005)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(fx, fy, z0 + drum_h / 2))
        groove = bpy.context.active_object
        groove.scale = (0.03, 0.03, drum_h * 0.96)
        groove.rotation_euler = (0, 0, fa)
        groove.data.materials.append(P["marble_old"])
        objs.append(groove)

    # Carved volute hints: two small scroll spheres on the capital front
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, z0 + drum_h + 0.09))
    cap = bpy.context.active_object
    cap.scale = (cap_xy, cap_xy, 0.18)
    cap.data.materials.append(P["marble"])
    objs.append(cap)
    for sx in (-1, 1):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.11,
                                             location=(sx * cap_xy * 0.32, cap_xy * 0.42,
                                                       z0 + drum_h + 0.10))
        scroll = bpy.context.active_object
        scroll.scale = (1.0, 0.55, 0.8)
        scroll.data.materials.append(P["marble_old"])
        smooth_object(scroll)
        objs.append(scroll)
    return z0 + drum_h + 0.18


# ==============================================================================
# 1. HELIOSTAT ORCHID (brass beam tower on marble plinth, mirror petals)
# ==============================================================================

def build_heliostat_orchid():
    clear_scene()
    setup_camera_and_lighting(target_z=1.1, ortho_scale=5.2)
    P = palette()
    objs = []

    top_z = _add_fluted_plinth(objs, P)

    # Brass turntable ring
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.40, depth=0.12,
                                        location=(0, 0, top_z + 0.06))
    table = bpy.context.active_object
    table.data.materials.append(P["brass"])
    smooth_object(table)
    objs.append(table)

    # Central brass housing
    hz = top_z + 0.42
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=0.30,
                                         location=(0, 0, hz))
    housing = bpy.context.active_object
    housing.scale = (1.0, 1.0, 0.9)
    housing.data.materials.append(P["brass"])
    smooth_object(housing)
    objs.append(housing)
    # Housing ribs: 3 brass tori around the sphere
    for i, tilt in enumerate((0.0, math.pi / 3, -math.pi / 3)):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.30, minor_radius=0.035,
                                         major_segments=24, minor_segments=8,
                                         location=(0, 0, hz))
        rib = bpy.context.active_object
        rib.rotation_euler = (tilt, 0, i * math.pi / 3)
        rib.data.materials.append(P["gold_leaf"])
        smooth_object(rib)
        objs.append(rib)

    # Faceted mana crystal lens — faces the iso camera diagonal (+X,-Y,up)
    from mathutils import Vector
    face_dir = Vector((0.62, -0.62, 0.38)).normalized()
    face_euler = face_dir.to_track_quat('Z', 'Y').to_euler()
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.22,
                                          location=(face_dir.x * 0.38, face_dir.y * 0.38,
                                                    hz + 0.15))
    crystal = bpy.context.active_object
    crystal.scale = (1.0, 1.0, 0.75)
    crystal.rotation_euler = face_euler
    crystal.data.materials.append(P["crystal"])
    objs.append(crystal)
    # Brass bezel around the crystal
    bpy.ops.mesh.primitive_torus_add(major_radius=0.23, minor_radius=0.045,
                                     major_segments=20, minor_segments=8,
                                     location=(face_dir.x * 0.36, face_dir.y * 0.36,
                                               hz + 0.14))
    bezel = bpy.context.active_object
    bezel.rotation_euler = face_euler
    bezel.data.materials.append(P["brass"])
    smooth_object(bezel)
    objs.append(bezel)

    # Five ivory petals with gold midrib, splayed open around the housing
    for p in range(5):
        pa = p * (2 * math.pi / 5) + math.pi / 5
        px = math.cos(pa) * 0.72
        py = math.sin(pa) * 0.72
        bpy.ops.mesh.primitive_uv_sphere_add(segments=14, ring_count=8, radius=0.42,
                                             location=(px, py, hz + 0.10))
        petal = bpy.context.active_object
        petal.scale = (0.55, 0.16, 1.05)
        petal.rotation_euler = (math.radians(52) * math.sin(pa),
                                -math.radians(52) * math.cos(pa),
                                pa + math.pi / 2)
        petal.data.materials.append(P["ivory"])
        smooth_object(petal)
        objs.append(petal)
        # Gold midrib (thin raised box along the petal)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(px * 1.02, py * 1.02, hz + 0.16))
        rib_g = bpy.context.active_object
        rib_g.scale = (0.035, 0.02, 0.62)
        rib_g.rotation_euler = petal.rotation_euler
        rib_g.data.materials.append(P["gold_leaf"])
        objs.append(rib_g)

    # Five heliostat mirror dishes on curved brass arms
    for p in range(5):
        pa = p * (2 * math.pi / 5)
        # Arm: quarter-torus from housing to dish
        ax, ay = math.cos(pa) * 0.55, math.sin(pa) * 0.55
        bpy.ops.mesh.primitive_torus_add(major_radius=0.30, minor_radius=0.04,
                                         major_segments=12, minor_segments=8,
                                         location=(ax, ay, hz - 0.05))
        arm = bpy.context.active_object
        arm.rotation_euler = (0, 0, pa)
        arm.data.materials.append(P["brass"])
        smooth_object(arm)
        objs.append(arm)
        # Dish
        dx, dy = math.cos(pa) * 0.88, math.sin(pa) * 0.88
        bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.24, depth=0.045,
                                            location=(dx, dy, hz + 0.22))
        dish = bpy.context.active_object
        dish.rotation_euler = (math.radians(62) * math.sin(pa + 0.4),
                               -math.radians(62) * math.cos(pa + 0.4), pa)
        dish.data.materials.append(P["mirror"])
        smooth_object(dish)
        objs.append(dish)
        # Dish rim
        bpy.ops.mesh.primitive_torus_add(major_radius=0.24, minor_radius=0.03,
                                         major_segments=20, minor_segments=8,
                                         location=(dx, dy, hz + 0.22))
        rim = bpy.context.active_object
        rim.rotation_euler = dish.rotation_euler
        rim.data.materials.append(P["brass"])
        smooth_object(rim)
        objs.append(rim)

    # Base accents: ivy + chrysanthemums
    _add_ivy_trail(objs, P["ivy"], 0, 0, 0.15, steps=8, radius=0.36, climb=0.12)
    _add_chrysanthemum(objs, P["chrys"], 0.55, 0.26, 0.11, scale=0.11)
    _add_chrysanthemum(objs, P["chrys"], -0.52, -0.30, 0.10, scale=0.10)

    export_and_render(objs, "tower_heliostat_orchid", "tower_heliostat_orchid_render")


# ==============================================================================
# 2. MYCELIUM BELL (brass arch + hanging bell + mushroom shelves)
# ==============================================================================

def _add_mushroom(objs, P, x, y, z, scale=0.22, tilt=0.0, facing=0.0):
    """Shelf mushroom: bent stem + lavender cap."""
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=scale * 0.34, depth=scale * 1.4,
                                        location=(x, y, z))
    stem = bpy.context.active_object
    stem.rotation_euler = (tilt, 0, facing)
    stem.data.materials.append(P["stem"])
    smooth_object(stem)
    objs.append(stem)
    cap_z = z + scale * 0.75
    bpy.ops.mesh.primitive_uv_sphere_add(segments=14, ring_count=8, radius=scale,
                                         location=(x + math.sin(tilt) * scale * 0.3, y, cap_z))
    cap = bpy.context.active_object
    cap.scale = (1.15, 1.15, 0.45)
    cap.data.materials.append(P["cap"])
    smooth_object(cap)
    objs.append(cap)


def build_mycelium_bell():
    clear_scene()
    setup_camera_and_lighting(target_z=1.3, ortho_scale=4.3)
    P = palette()
    objs = []

    top_z = _add_fluted_plinth(objs, P, base_xy=1.0, drum_r=0.30, drum_h=0.80, cap_xy=0.68)

    # Brass arch: vertical ring, lower half sunk into the plinth
    arch_z = top_z + 0.75
    bpy.ops.mesh.primitive_torus_add(major_radius=0.62, minor_radius=0.07,
                                     major_segments=28, minor_segments=10,
                                     location=(0, 0, arch_z))
    arch = bpy.context.active_object
    arch.rotation_euler = (math.radians(90), 0, 0)
    arch.data.materials.append(P["brass"])
    smooth_object(arch)
    objs.append(arch)
    # Crown finial
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.12,
                                         location=(0, 0, arch_z + 0.68))
    finial = bpy.context.active_object
    finial.data.materials.append(P["gold_leaf"])
    smooth_object(finial)
    objs.append(finial)
    # Yoke bar across the arch
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.05, depth=0.7,
                                        location=(0, 0, arch_z + 0.32))
    yoke = bpy.context.active_object
    yoke.rotation_euler = (math.radians(90), 0, 0)
    yoke.data.materials.append(P["iron"])
    objs.append(yoke)

    # Hanging bell: crown + flared body + lip + clapper + spore orb
    bell_top = arch_z + 0.30
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.09,
                                         location=(0, 0, bell_top - 0.05))
    crown = bpy.context.active_object
    crown.data.materials.append(P["brass"])
    smooth_object(crown)
    objs.append(crown)
    bpy.ops.mesh.primitive_cone_add(vertices=20, radius1=0.34, radius2=0.12, depth=0.55,
                                    location=(0, 0, bell_top - 0.38))
    body = bpy.context.active_object
    body.data.materials.append(P["brass"])
    smooth_object(body)
    objs.append(body)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.34, minor_radius=0.05,
                                     major_segments=24, minor_segments=8,
                                     location=(0, 0, bell_top - 0.65))
    lip = bpy.context.active_object
    lip.data.materials.append(P["gold_leaf"])
    smooth_object(lip)
    objs.append(lip)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=6, radius=0.06,
                                         location=(0, 0, bell_top - 0.69))
    clapper = bpy.context.active_object
    clapper.data.materials.append(P["iron"])
    smooth_object(clapper)
    objs.append(clapper)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.12,
                                          location=(0.10, -0.10, bell_top - 0.88))
    orb = bpy.context.active_object
    orb.data.materials.append(P["spore"])
    objs.append(orb)

    # Mushroom shelves climbing the column
    _add_mushroom(objs, P, 0.34, 0.10, 0.55, scale=0.24, tilt=0.5, facing=0.3)
    _add_mushroom(objs, P, -0.32, -0.12, 0.78, scale=0.28, tilt=-0.45, facing=2.8)
    _add_mushroom(objs, P, 0.10, -0.34, 1.00, scale=0.22, tilt=0.4, facing=4.4)
    _add_mushroom(objs, P, -0.12, 0.34, 0.38, scale=0.18, tilt=-0.35, facing=1.2)
    _add_mushroom(objs, P, 0.30, -0.22, 1.18, scale=0.26, tilt=0.55, facing=5.5)

    # Base accents: peony + chrysanthemum + ivy
    _add_peony(objs, P["peony"], 0.66, 0.28, 0.16, scale=0.18)
    _add_chrysanthemum(objs, P["chrys"], -0.62, 0.30, 0.13, scale=0.14)
    _add_ivy_trail(objs, P["ivy"], 0, 0, 0.15, steps=8, radius=0.34, climb=0.12)

    export_and_render(objs, "tower_mycelium_bell", "tower_mycelium_bell_render")


if __name__ == "__main__":
    print("=== STARTING GENERATION OF CONCEPT-ART TOWERS ===")
    build_heliostat_orchid()
    build_mycelium_bell()
    print("=== CONCEPT-ART TOWERS GENERATED AND EXPORTED SUCCESSFULLY ===")
