"""
Aegis Flora: High-Resolution Concept Image Sheets Generator
Renders multi-asset concept sheets in image format (.png) using Blender 5.1
1. assets/treasure_showcase_sheet.png: Treasure chests, Relic Amphoras, Mana Crystals, Gold Coins & Gears on courtyard pavers.
2. assets/flora_showcase_sheet.png: Clockwork Lotus Basin, Golden Chrysanthemum, Cypress, Olive Tree & Wildflower meadow.
3. assets/ruins_showcase_sheet.png: Grand Colonnade, Athena Automata Statue, Corinthian Columns & Ruined Pediments.
"""

import bpy
import math
import os

OUTPUT_DIR = "/Users/jahflyx/towers/assets"
os.makedirs(OUTPUT_DIR, exist_ok=True)

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

def setup_lighting_and_camera(ortho_scale=10.5, target_z=1.5):
    # Key Sun: Warm Golden Sunlight
    sun_data = bpy.data.lights.new(name="KeySun", type='SUN')
    sun_data.energy = 3.8
    sun_data.color = (1.0, 0.95, 0.85)
    sun_obj = bpy.data.objects.new(name="KeySun", object_data=sun_data)
    bpy.context.collection.objects.link(sun_obj)
    sun_obj.rotation_euler = (math.radians(52), math.radians(18), math.radians(45))

    # Fill Light: Cerulean Sky Fill
    fill_data = bpy.data.lights.new(name="FillLight", type='SUN')
    fill_data.energy = 1.3
    fill_data.color = (0.28, 0.48, 0.58)
    fill_obj = bpy.data.objects.new(name="FillLight", object_data=fill_data)
    bpy.context.collection.objects.link(fill_obj)
    fill_obj.rotation_euler = (math.radians(45), math.radians(-30), math.radians(-135))

    # Rim Light: Amber Edge Accent
    rim_data = bpy.data.lights.new(name="RimLight", type='POINT')
    rim_data.energy = 800.0
    rim_data.color = (1.0, 0.68, 0.28)
    rim_obj = bpy.data.objects.new(name="RimLight", object_data=rim_data)
    bpy.context.collection.objects.link(rim_obj)
    rim_obj.location = (-6.0, -5.5, target_z + 4.5)

    # Isometric Camera
    cam_data = bpy.data.cameras.new(name="IsoCamera")
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = ortho_scale
    cam_obj = bpy.data.objects.new(name="IsoCamera", object_data=cam_data)
    bpy.context.collection.objects.link(cam_obj)
    cam_obj.location = (14.0, -14.0, target_z + 11.43)
    cam_obj.rotation_euler = (math.radians(54.736), 0, math.radians(45))
    bpy.context.scene.camera = cam_obj

def setup_render_engine():
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 1440
    scene.render.resolution_y = 1440
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'

def import_glb_model(glb_path, location=(0,0,0), scale=(1,1,1), rotation=(0,0,0)):
    if not os.path.exists(glb_path):
        print(f"Warning: {glb_path} not found")
        return None
    bpy.ops.import_scene.gltf(filepath=glb_path)
    imported_objects = bpy.context.selected_objects
    grp = bpy.data.objects.new(name=os.path.basename(glb_path), object_data=None)
    bpy.context.collection.objects.link(grp)
    grp.location = location
    grp.scale = scale
    grp.rotation_euler = rotation
    for obj in imported_objects:
        obj.parent = grp
    return grp

def build_stone_courtyard(size=9.0):
    m_stone = create_pbr_material("CourtyardStone", (0.86, 0.83, 0.76, 1.0), roughness=0.65)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, -0.15))
    floor = bpy.context.active_object
    floor.scale = (size, size, 0.3)
    floor.data.materials.append(m_stone)

    # Inlaid brass line
    m_brass = create_pbr_material("InlaidBrass", (0.88, 0.72, 0.22, 1.0), metallic=0.92, roughness=0.25)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.01))
    line = bpy.context.active_object
    line.scale = (size * 0.95, 0.08, 0.02)
    line.data.materials.append(m_brass)

# ==============================================================================
# SHEET 1: TREASURE, RELICS & MANA CRYSTAL VAULT
# ==============================================================================
def render_treasure_sheet():
    clear_scene()
    setup_render_engine()
    setup_lighting_and_camera(ortho_scale=8.5, target_z=1.2)
    build_stone_courtyard(size=8.5)

    models_dir = "/Users/jahflyx/towers/blender_pipeline/models"

    # 1. Main Open Treasure Chest (Center-Left)
    import_glb_model(os.path.join(models_dir, "prop_treasure_chest.glb"),
                     location=(-1.2, -0.6, 0.0), scale=(1.25, 1.25, 1.25), rotation=(0, 0, math.radians(-15)))

    # 2. Relic Amphora Urn (Right)
    import_glb_model(os.path.join(models_dir, "prop_relic_urn.glb"),
                     location=(1.8, -0.4, 0.0), scale=(1.15, 1.15, 1.15), rotation=(0, 0, math.radians(20)))

    # 3. Second Relic Urn on pedestal (Rear Right)
    import_glb_model(os.path.join(models_dir, "prop_relic_urn.glb"),
                     location=(1.2, 1.8, 0.0), scale=(0.95, 0.95, 0.95), rotation=(0, 0, math.radians(-40)))

    # 4. Inlaid Conduits & Blocks (Rear Left)
    import_glb_model(os.path.join(models_dir, "accent_masonry_blocks.glb"),
                     location=(-1.8, 1.6, 0.0), scale=(0.85, 0.85, 0.85), rotation=(0, 0, math.radians(45)))

    # 5. Wildflower cluster accent
    import_glb_model(os.path.join(models_dir, "flora_wildflower_cluster.glb"),
                     location=(0.2, 0.8, 0.0), scale=(0.8, 0.8, 0.8), rotation=(0, 0, 0))

    # Direct Render
    render_out = os.path.join(OUTPUT_DIR, "treasure_showcase_sheet.png")
    bpy.context.scene.render.filepath = render_out
    bpy.ops.render.render(write_still=True)
    print(f"Treasure Sheet rendered: {render_out}")

# ==============================================================================
# SHEET 2: BOTANICAL FLORA & CLOCKWORK GARDEN
# ==============================================================================
def render_flora_sheet():
    clear_scene()
    setup_render_engine()
    setup_lighting_and_camera(ortho_scale=10.5, target_z=2.0)
    build_stone_courtyard(size=10.5)

    models_dir = "/Users/jahflyx/towers/blender_pipeline/models"

    # 1. Columnar Cypress Tree (Rear Left)
    import_glb_model(os.path.join(models_dir, "flora_cypress_tree.glb"),
                     location=(-2.8, 1.8, 0.0), scale=(1.1, 1.1, 1.1), rotation=(0, 0, math.radians(30)))

    # 2. Ancient Olive Tree (Rear Right)
    import_glb_model(os.path.join(models_dir, "flora_olive_tree.glb"),
                     location=(2.4, 1.6, 0.0), scale=(1.05, 1.05, 1.05), rotation=(0, 0, math.radians(-25)))

    # 3. Hero Clockwork Lotus Water Basin (Front Center)
    import_glb_model(os.path.join(models_dir, "flora_clockwork_lotus.glb"),
                     location=(0.0, -1.2, 0.0), scale=(1.35, 1.35, 1.35), rotation=(0, 0, 0))

    # 4. Hero Golden Chrysanthemum Planters (Flanking)
    import_glb_model(os.path.join(models_dir, "flora_golden_chrysanthemum.glb"),
                     location=(-2.4, -0.6, 0.0), scale=(1.1, 1.1, 1.1), rotation=(0, 0, math.radians(15)))
    import_glb_model(os.path.join(models_dir, "flora_golden_chrysanthemum.glb"),
                     location=(2.4, -0.6, 0.0), scale=(1.1, 1.1, 1.1), rotation=(0, 0, math.radians(-20)))

    # 5. Wildflower Meadow Clusters (Midground)
    import_glb_model(os.path.join(models_dir, "flora_wildflower_cluster.glb"),
                     location=(-0.8, 1.0, 0.0), scale=(0.95, 0.95, 0.95), rotation=(0, 0, math.radians(60)))
    import_glb_model(os.path.join(models_dir, "flora_wildflower_cluster.glb"),
                     location=(1.0, 0.9, 0.0), scale=(0.85, 0.85, 0.85), rotation=(0, 0, math.radians(-30)))

    # Direct Render
    render_out = os.path.join(OUTPUT_DIR, "flora_showcase_sheet.png")
    bpy.context.scene.render.filepath = render_out
    bpy.ops.render.render(write_still=True)
    print(f"Flora Sheet rendered: {render_out}")

# ==============================================================================
# SHEET 3: ANCIENT RUINS & MONUMENTAL ARCHITECTURE
# ==============================================================================
def render_ruins_sheet():
    clear_scene()
    setup_render_engine()
    setup_lighting_and_camera(ortho_scale=11.5, target_z=2.5)
    build_stone_courtyard(size=11.5)

    models_dir = "/Users/jahflyx/towers/blender_pipeline/models"

    # 1. Grand Colonnade Ruin (Rear Center)
    import_glb_model(os.path.join(models_dir, "ruin_grand_colonnade.glb"),
                     location=(0.0, 2.0, 0.0), scale=(1.15, 1.15, 1.15), rotation=(0, 0, 0))

    # 2. Statue of Athena Automata (Front Center-Right)
    import_glb_model(os.path.join(models_dir, "statue_automata_athena.glb"),
                     location=(1.8, -0.8, 0.0), scale=(1.25, 1.25, 1.25), rotation=(0, 0, math.radians(-45)))

    # 3. Fluted Column & Pediment (Front Center-Left)
    import_glb_model(os.path.join(models_dir, "accent_column_pediment.glb"),
                     location=(-2.2, -0.6, 0.0), scale=(1.1, 1.1, 1.1), rotation=(0, 0, math.radians(35)))

    # 4. Masonry Blocks & Conduits (Foreground Left)
    import_glb_model(os.path.join(models_dir, "accent_masonry_blocks.glb"),
                     location=(-1.5, -2.4, 0.0), scale=(0.95, 0.95, 0.95), rotation=(0, 0, math.radians(10)))

    # 5. Relic Urn on plinth (Foreground Right)
    import_glb_model(os.path.join(models_dir, "prop_relic_urn.glb"),
                     location=(2.2, -2.2, 0.0), scale=(0.9, 0.9, 0.9), rotation=(0, 0, math.radians(-15)))

    # 6. Wildflower clusters
    import_glb_model(os.path.join(models_dir, "flora_wildflower_cluster.glb"),
                     location=(0.0, -1.8, 0.0), scale=(0.9, 0.9, 0.9), rotation=(0, 0, 0))

    # Direct Render
    render_out = os.path.join(OUTPUT_DIR, "ruins_showcase_sheet.png")
    bpy.context.scene.render.filepath = render_out
    bpy.ops.render.render(write_still=True)
    print(f"Ruins Sheet rendered: {render_out}")

if __name__ == "__main__":
    print("Rendering Treasure Showcase Sheet...")
    render_treasure_sheet()
    print("Rendering Flora Showcase Sheet...")
    render_flora_sheet()
    print("Rendering Ruins Showcase Sheet...")
    render_ruins_sheet()
    print("=== ALL CONCEPT IMAGE SHEETS RENDERED SUCCESSFULLY ===")
