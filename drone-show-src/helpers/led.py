from typing import Optional, cast

from bpy.types import Material, Object


class LedError(RuntimeError):
    pass


def get_led_material(obj: Object) -> Material:
    for slot in obj.material_slots:
        material = slot.material
        if material.led.is_led:
            return material
    raise LedError("Could not find LED material")


def get_material_color(material: Material) -> tuple[int, int, int]:
    if material.use_nodes:
        value = _get_node_color(material)
    else:
        value = material.diffuse_color

    alpha = value[3]
    color = tuple(int(value[component] * alpha * 255) for component in range(3))
    return cast(tuple[int, int, int], color)


def _get_node_color(material: Material):
    supported_nodes = ("EMISSION", "BSDF_DIFFUSE", "BSDF_PRINCIPLED")
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    out = nodes.get("Material Output")
    for link in links:
        if link.from_node.type in supported_nodes and link.to_node == out:
            input_name = (
                "Base Color" if link.from_node.type == "BSDF_PRINCIPLED" else "Color"
            )
            return link.from_node.inputs[input_name].default_value
    raise LedError(
        f"Could not detect color of the node system for LED material '{material.name}'"
    )
