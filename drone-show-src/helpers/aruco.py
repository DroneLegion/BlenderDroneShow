import json
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector
from PIL import Image, ImageDraw

with (Path(__file__).parent / Path("aruco_dict.json")).open("r") as f:
    aruco_dict = json.load(f)


aruco_sizes = {
    "aruco": 5,
    "4x4_1000": 4,
    "5x5_1000": 5,
    "6x6_1000": 6,
    "7x7_1000": 7,
}


def get_aruco_objects(context, selected=False) -> list[bpy.types.Object]:
    objects = context.selected_objects if selected else context.scene.objects
    return [obj for obj in objects if obj.aruco.is_aruco]


def generate_marker(
    dict_name: str, marker_id: int, image_size: int = 512
) -> Image.Image:
    aruco_bytes = aruco_dict[dict_name][marker_id]
    aruco_size = aruco_sizes[dict_name]
    bits = []
    bits_count = aruco_size * aruco_size

    # translated from https://github.com/okalachev/arucogen/blob/master/main.js#L53
    for aruco_byte in aruco_bytes:
        start = bits_count - len(bits)
        for i in range(min(7, start - 1), -1, -1):
            bits.append((aruco_byte >> i) & 1)

    out = Image.new("RGB", (image_size, image_size), (0, 0, 0))
    draw = ImageDraw.Draw(out)

    black_rim_offset = 1
    pixel_size = image_size / (aruco_size + 2 * black_rim_offset)

    for i in range(aruco_size):
        for j in range(aruco_size):
            if not bits[i * aruco_size + j]:
                continue

            draw.rectangle(
                (
                    (j + 0 + black_rim_offset) * pixel_size,
                    (i + 0 + black_rim_offset) * pixel_size,
                    (j + 1 + black_rim_offset) * pixel_size,
                    (i + 1 + black_rim_offset) * pixel_size,
                ),
                fill=(255, 255, 255),
            )

    # out.show()
    return out


def get_marker_mesh() -> bpy.types.Mesh:
    name = "Aruco Marker"

    verts = [
        Vector((-1, 1, 0)),
        Vector((1, 1, 0)),
        Vector((1, -1, 0)),
        Vector((-1, -1, 0)),
    ]
    edges = []
    faces = [[0, 1, 2, 3]]

    mesh = bpy.data.meshes.new(name=name)
    mesh.from_pydata(verts, edges, faces)

    return mesh


def get_name(dict_name: str, marker_id: int) -> str:
    return f"Aruco {dict_name} {marker_id}"


def get_aruco_image(dict_name: str, marker_id: int, image_size=256):
    name = get_name(dict_name, marker_id)
    if image := bpy.data.images.get(name):
        return image

    pil_image = generate_marker(dict_name, marker_id, image_size)
    image = bpy.data.images.new(name=name, width=image_size, height=image_size)
    byte_to_normalized = 1.0 / 255.0
    image.pixels[:] = (
        np.asarray(pil_image.convert("RGBA"), dtype=np.float32) * byte_to_normalized
    ).ravel()
    image.pack()
    return image


def get_aruco_material(dict_name: str, marker_id: int) -> bpy.types.Material:
    name = get_name(dict_name, marker_id)
    if material := bpy.data.materials.get(name):
        return material

    material = bpy.data.materials.new(name=name)

    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links

    nodes.clear()

    node_principled = nodes.new(type="ShaderNodeBsdfPrincipled")
    node_principled.inputs["Specular"].default_value = 0.0
    node_principled.inputs["Roughness"].default_value = 1.0
    node_principled.location = 0, 0

    node_tex = nodes.new("ShaderNodeTexImage")
    node_tex.image = get_aruco_image(dict_name, marker_id)
    node_tex.interpolation = "Closest"
    node_tex.location = -400, 0

    node_output = nodes.new(type="ShaderNodeOutputMaterial")
    node_output.location = 400, 0

    link = links.new(node_tex.outputs["Color"], node_principled.inputs["Base Color"])
    link = links.new(node_principled.outputs["BSDF"], node_output.inputs["Surface"])

    return material


def update_aruco_material(obj: bpy.types.Object):
    material = get_aruco_material(obj.aruco.dictionary.lower(), obj.aruco.marker_id)

    if obj.data.materials:
        obj.data.materials[0] = material
    else:
        obj.data.materials.append(material)


def get_rim_material() -> bpy.types.Material:
    name = "Aruco marker white rim"

    if material := bpy.data.materials.get(name):
        return material

    material = bpy.data.materials.new(name=name)

    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links

    nodes.clear()

    node_principled = nodes.new(type="ShaderNodeBsdfPrincipled")
    node_principled.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    node_principled.inputs["Specular"].default_value = 0.0
    node_principled.inputs["Roughness"].default_value = 1.0
    node_principled.location = 0, 0

    node_output = nodes.new(type="ShaderNodeOutputMaterial")
    node_output.location = 400, 0

    link = links.new(node_principled.outputs["BSDF"], node_output.inputs["Surface"])

    return material
