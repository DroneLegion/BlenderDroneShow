import bpy
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
)
from bpy.types import PropertyGroup

from . import operators, ui

bl_info = {
    "name": "Drone show animation (.csv)",
    "author": "Artem Vasiunik & Arthur Golubtsov",
    "version": (1, 0, 0),
    "blender": (3, 2, 2),
    "location": "File > Export > Drone show animation (.csv)",
    "description": "Export > Drone show animation (.csv)",
    "doc_url": "https://github.com/DroneLegion/BlenderDroneShow/blob/master/README.md",
    "tracker_url": "https://github.com/DroneLegion/BlenderDroneShow/issues",
    "category": "Import-Export",
}


class DroneShowProperties(PropertyGroup):
    # Check properties
    check_led: BoolProperty(
        name="Check LEDs",
        description="Check LEDs material on drones",
        default=True,
    )

    check_speed: BoolProperty(
        name="Check speed",
        description="Check maximum drone movement speed",
        default=True,
    )

    speed_limit: FloatProperty(
        name="Speed limit",
        description="Limit of maximum drone movement speed (m/s)",
        unit="VELOCITY",
        default=3,
        min=0,
        soft_min=0.5,
        soft_max=20,
        step=50,
    )

    check_distance: BoolProperty(
        name="Check distance",
        description="Check distance between drones",
        default=True,
    )

    distance_limit: FloatProperty(
        name="Distance limit",
        description="Closest possible distance between drones (m)",
        unit="LENGTH",
        default=1.5,
        min=0,
        soft_min=0.5,
        soft_max=10,
        step=50,
    )

    detailed_warnings: bpy.props.BoolProperty(
        name="Show detailed warnings",
        description="Show detailed animation check warnings",
        default=True,
    )


class DroneObjectProperties(PropertyGroup):
    is_drone: BoolProperty(
        name="Is drone",
        default=False,
    )


class DroneLedProperties(PropertyGroup):
    is_led: BoolProperty(
        name="Is LED color",
        default=False,
    )


classes = (
    DroneShowProperties,
    DroneObjectProperties,
    DroneLedProperties,
    operators.ExportSwarmAnimation,
    operators.CheckSwarmAnimation,
    operators.AssignDrones,
    operators.SelectDrones,
    ui.DronePanel,
    ui.DroneCoordsPanel,
    ui.DroneLedPanel,
    ui.LedPanel,
    ui.DroneOperatorsPanel,
    ui.CheckPanel,
)


def menu_func(self, context):
    self.layout.operator(
        operators.ExportSwarmAnimation.bl_idname, text="Drone show animation (.csv)"
    )


# noinspection PyNoneFunctionAssignment
def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)

    bpy.types.Scene.drone_show = PointerProperty(type=DroneShowProperties)
    bpy.types.Object.drone = PointerProperty(type=DroneObjectProperties)
    bpy.types.Material.led = PointerProperty(type=DroneLedProperties)

    bpy.types.TOPBAR_MT_file_export.append(menu_func)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)

    del bpy.types.Scene.drone_show
    del bpy.types.Object.drone
    del bpy.types.Material.led

    bpy.types.TOPBAR_MT_file_export.remove(menu_func)


if __name__ == "__main__":
    register()
