"""Build and render the Chrome Strider as a consistent low-poly sprite atlas."""

import math
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[2]
FRAMES = ROOT / "tools" / "blender" / "strider_frames"
FRAMES.mkdir(parents=True, exist_ok=True)


def material(name, color, metallic=0.0, roughness=0.45, emission=None, strength=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1)
        bsdf.inputs["Emission Strength"].default_value = strength
    return mat


def ico(name, radius, location, mat, subdivisions=1):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivisions, radius=radius, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    return obj


def blade(name, length, width, mat):
    # A six-sided tapered shard, elongated along local Z.
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=width, radius2=width * 0.46, depth=length)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    return obj


def key(obj, frame, location=None, rotation=None, scale=None):
    if location is not None:
        obj.location = location
        obj.keyframe_insert("location", frame=frame)
    if rotation is not None:
        obj.rotation_euler = rotation
        obj.keyframe_insert("rotation_euler", frame=frame)
    if scale is not None:
        obj.scale = scale
        obj.keyframe_insert("scale", frame=frame)


def cage_points(frame, arm):
    state, step = divmod(frame - 1, 8)
    phase = step / 8 * math.tau
    # Unevenly spaced, curling limbs form a broken cage rather than a literal spider.
    bases = (2.72, 1.92, .76, -.28, -1.33, -2.42)
    angle = bases[arm] + math.sin(phase + arm * 1.31) * .035
    curl = (.52, -.46, .6, -.55, .48, -.62)[arm]
    radii = [.58, 1.02, 1.46, 1.88]
    spread = 1.0
    if state == 1:
        spread = (1, .91, .8, .72, .79, 1.14, 1.28, 1.06)[step]
    elif state == 2:
        spread = (1, 1.2, 1.13, .88, .94, 1.04, 1, 1)[step]
        angle += (.18 if arm % 2 else -.18) * math.sin(step / 7 * math.pi)
    elif state == 3:
        spread = max(.18, 1 - step * .11)
        angle += (arm - 2.5) * step * .035
    points = []
    for index, radius in enumerate(radii):
        bend = curl * (index / 3) ** 1.25
        wobble = math.sin(phase + arm * .8 + index) * .025 * index
        r = radius * spread
        points.append(Vector((math.cos(angle + bend + wobble) * r,
                              .1 - index * .055,
                              math.sin(angle + bend + wobble) * r)))
    return points


def between(a, b):
    vector = b - a
    midpoint = (a + b) * .5
    rotation = vector.to_track_quat("Z", "Y").to_euler()
    return midpoint, rotation, (1, 1, vector.length)


# Reset scene.
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

chrome = material("Cold chrome", (.33, .42, .57), metallic=.92, roughness=.2)
chrome_bright = material("Chrome edge", (.72, .82, .98), metallic=.86, roughness=.16)
red = material("Faceted core", (.62, .015, .025), metallic=.18, roughness=.3)
dark = material("Backdrop", (.004, .003, .012), roughness=1)
floor_mat = material("Floor", (.008, .012, .055), metallic=.1, roughness=.65)
pink = material("Horizon", (.75, .015, .28), roughness=.35, emission=(1, .01, .24), strength=5)

# Background, floor and luminous horizon.
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 2.3, 0), rotation=(math.pi / 2, 0, 0))
bpy.context.object.data.materials.append(dark)
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, -2.15))
bpy.context.object.data.materials.append(floor_mat)
bpy.ops.mesh.primitive_cube_add(location=(0, 1.8, -1.28), scale=(6, .03, .025))
bpy.context.object.data.materials.append(pink)

core = ico("Red core", .73, (0, 0, 0), red, subdivisions=2)
core.rotation_euler = (0.3, 0.2, 0.1)
inner = ico("Core highlight", .52, (0, -.16, .08), red, subdivisions=1)

limbs = []
joint_objects = []
for arm in range(6):
    for segment in range(3):
        obj = blade(f"Cage claw {arm + 1}.{segment + 1}", 1, .17 - segment * .018,
                    chrome_bright if segment == 2 else chrome)
        limbs.append((arm, segment, obj))
    for point_index in (1, 2):
        joint = ico(f"Knuckle {arm + 1}.{point_index}", .13 - point_index * .012,
                    (0, 0, 0), chrome_bright, subdivisions=1)
        joint_objects.append((arm, point_index, joint))

for frame in range(1, 33):
    state, step = divmod(frame - 1, 8)
    pulse = 1 + (math.sin(step / 8 * math.tau) * .055 if state == 0 else 0)
    if state == 1:
        pulse *= [1, .94, .88, .84, .92, 1.14, 1.22, 1.05][step]
    elif state == 2:
        pulse *= [1, .9, .82, .9, .96, 1.02, 1, 1][step]
    elif state == 3:
        pulse *= max(.08, 1 - step * .125)
    key(core, frame, rotation=(.3 + frame * .025, .2 + frame * .035, .1),
        scale=(pulse * .92, pulse, pulse * 1.08))
    key(inner, frame, location=(0, -.16, .08 - (.08 * step if state == 3 else 0)),
        rotation=(0, frame * -.05, frame * .03), scale=(pulse,) * 3)
    points_by_leg = [cage_points(frame, leg) for leg in range(6)]
    for leg, segment, obj in limbs:
        loc, rot, scl = between(points_by_leg[leg][segment], points_by_leg[leg][segment + 1])
        key(obj, frame, loc, rot, scl)
    for leg, point_index, obj in joint_objects:
        scale = max(.18, 1 - step * .105) if state == 3 else 1
        key(obj, frame, points_by_leg[leg][point_index], scale=(scale,) * 3)

# Force stepped frame changes in the source animation.
for action in bpy.data.actions:
    for curve in action.fcurves:
        for point in curve.keyframe_points:
            point.interpolation = "LINEAR"

# Camera and lights.
bpy.ops.object.camera_add(location=(0, -10.5, .12))
camera = bpy.context.object
camera.data.type = "ORTHO"
camera.data.ortho_scale = 5.4
camera.rotation_euler = (math.pi / 2, 0, 0)
bpy.context.scene.camera = camera

bpy.ops.object.light_add(type="AREA", location=(-3.6, -4.0, 4.8))
bpy.context.object.data.energy = 900
bpy.context.object.data.color = (.55, .68, 1)
bpy.context.object.data.shape = "DISK"
bpy.context.object.data.size = 4
bpy.ops.object.light_add(type="AREA", location=(3.5, 1.2, -0.3))
bpy.context.object.data.energy = 650
bpy.context.object.data.color = (1, .02, .18)
bpy.context.object.data.size = 3

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 240
scene.render.resolution_y = 170
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.render.image_settings.color_mode = "RGB"
scene.render.filepath = str(FRAMES / "frame_")
scene.render.use_file_extension = True
scene.render.film_transparent = False
scene.render.image_settings.color_depth = "8"
scene.render.resolution_percentage = 100
scene.world.color = (0, 0, 0)
scene.frame_start = 1
scene.frame_end = 32

# Avoid smooth modern output; retain hard facets and crisp sprite edges.
scene.render.image_settings.compression = 40
scene.render.film_transparent = False
scene.render.engine = "BLENDER_EEVEE"
scene.render.filepath = str(FRAMES / "frame_####.png")

bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "tools" / "blender" / "chrome_strider.blend"))
bpy.ops.render.render(animation=True)
