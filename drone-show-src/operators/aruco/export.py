from pathlib import Path

import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper

from ...helpers import aruco as aruco_helpers

__all__ = ("ExportAruco",)


class ExportAruco(Operator, ExportHelper):
    bl_idname = "drone_show.export_aruco"
    bl_label = "Export Aruco map"
    bl_description = "Export Aruco markers map for drones"
    filename_ext = ".txt"

    filepath: bpy.props.StringProperty(
        name="File Path",
        description="Path to the file",
        maxlen=1024,
        subtype="DIR_PATH",
        default="",
    )

    filter_glob: bpy.props.StringProperty(
        default="*.txt",
        options={"HIDDEN"},
        maxlen=255,
    )

    def draw(self, context):
        layout = self.layout

    def execute(self, context):
        path = Path(self.filepath)

        aruco_objects = aruco_helpers.get_aruco_objects(context)
        if not aruco_objects:
            self.report({"ERROR"}, "No Aruco marker objects found")
            return {"CANCELLED"}

        markers = []
        for aruco_object in aruco_objects:
            size = aruco_object.dimensions[0]
            x, y, z = aruco_object.matrix_world.to_translation()
            rot_x, rot_y, rot_z = aruco_object.matrix_world.to_euler("XYZ")

            marker_id = aruco_object.aruco.marker_id
            data = (round(item, 3) for item in (size, x, y, z, rot_z, rot_y, rot_x))
            markers.append((marker_id,) + tuple(data))

        markers.sort(key=lambda item: item[0])

        headers = ("# id", "length", "x", "y", "z", "rot_z", "rot_y", "rot_x")
        with path.open("w") as f:
            f.write("".join([f"{item: <8}" for item in headers]) + "\n")
            for marker in markers:
                f.write("".join([f"{item: <8}" for item in marker]) + "\n")

        return {"FINISHED"}
