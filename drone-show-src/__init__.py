import bpy

bl_info = {
    "name": "Drone show animation (.csv)",
    "author": "Artem Vasiunik & Arthur Golubtsov",
    "version": (1, 2, 0),
    "blender": (3, 2, 2),
    "location": "File > Export > Drone show animation (.csv)",
    "description": "Export > Drone show animation (.csv)",
    "doc_url": "https://github.com/DroneLegion/BlenderDroneShow/blob/master/README.md",
    "tracker_url": "https://github.com/DroneLegion/BlenderDroneShow/issues",
    "category": "Import-Export",
}


def ensure_site_packages(packages):
    if not packages:
        return

    import importlib.util
    import os
    import site
    import sys

    user_site_packages = site.getusersitepackages()
    os.makedirs(user_site_packages, exist_ok=True)
    sys.path.append(user_site_packages)

    modules_to_install = [
        module[1] for module in packages if not importlib.util.find_spec(module[0])
    ]

    if modules_to_install:
        import subprocess

        python_binary = sys.executable

        subprocess.run([python_binary, "-m", "ensurepip"], check=True)
        subprocess.run(
            [python_binary, "-m", "pip", "install", *modules_to_install, "--user"],
            check=True,
        )


ensure_site_packages(
    [
        ("numpy", "numpy"),
        ("PIL", "Pillow"),
    ]
)

from . import operators, ui
from .properties import (
    ArucoObjectProperties,
    DroneLedProperties,
    DroneObjectProperties,
    DroneShowProperties,
)

classes = (
    DroneShowProperties,
    DroneObjectProperties,
    DroneLedProperties,
    ArucoObjectProperties,
    operators.ExportAnimation,
    operators.ExportAnimationChecksPanel,
    operators.CheckSwarmAnimation,
    operators.AssignDrones,
    operators.SelectDrones,
    operators.SetLedColor,
    operators.AddAruco,
    operators.ExportAruco,
    operators.GenerateArucoMap,
    operators.ImportAruco,
    ui.DronePanel,
    ui.DroneCoordsPanel,
    ui.DroneLedPanel,
    ui.LedPanel,
    ui.ArucoPanel,
    ui.ArucoCoordsPanel,
    ui.DroneOperatorsPanel,
    ui.LedOperatorsPanel,
    ui.AnimationPanel,
    ui.ArucoOperatorsPanel,
)


def export_animation_menu(self, context):
    self.layout.operator(
        operators.ExportAnimation.bl_idname, text="Drone show animation (.csv)"
    )


def export_aruco_menu(self, context):
    self.layout.operator(
        operators.ExportAruco.bl_idname, text="Aruco markers map (.txt)"
    )


def import_aruco_menu(self, context):
    self.layout.operator(
        operators.ImportAruco.bl_idname, text="Aruco markers map (.txt)"
    )


# noinspection PyNoneFunctionAssignment
def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)

    bpy.types.Scene.drone_show = bpy.props.PointerProperty(type=DroneShowProperties)

    bpy.types.Object.drone = bpy.props.PointerProperty(type=DroneObjectProperties)
    bpy.types.Material.led = bpy.props.PointerProperty(type=DroneLedProperties)

    bpy.types.Object.aruco = bpy.props.PointerProperty(type=ArucoObjectProperties)

    bpy.types.TOPBAR_MT_file_export.append(export_animation_menu)
    bpy.types.TOPBAR_MT_file_export.append(export_aruco_menu)

    bpy.types.TOPBAR_MT_file_import.append(import_aruco_menu)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)

    del bpy.types.Scene.drone_show

    del bpy.types.Object.drone
    del bpy.types.Material.led

    del bpy.types.Object.aruco

    bpy.types.TOPBAR_MT_file_export.remove(export_animation_menu)
    bpy.types.TOPBAR_MT_file_export.remove(export_aruco_menu)

    bpy.types.TOPBAR_MT_file_import.remove(import_aruco_menu)


if __name__ == "__main__":
    register()
