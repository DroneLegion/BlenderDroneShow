from pathlib import Path

import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper

from ...helpers import aruco as aruco_helpers

__all__ = ("ImportAruco", )


class ImportAruco(Operator, ImportHelper):
    bl_idname = "drone_show.import_aruco"
    bl_label = "Import Aruco map"
    bl_description = "Import Aruco map file as marker objects"
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
        options={'HIDDEN'},
        maxlen=255,
    )

    dictionary: bpy.props.EnumProperty(
        name="Dictionary",
        description="Dictionary of the Aruco markers",
        items=[
            ("aruco", "Aruco", "Standard Aruco dictionary"),
            ("4x4_1000", "4x4", "4x4 dictionary (default)"),
            ("5x5_1000", "5x5", "5x5 dictionary"),
            ("6x6_1000", "6x6", "6x6 dictionary"),
            ("7x7_1000", "7x7", "7x7 dictionary"),
        ],
        default="4x4_1000",
    )

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(self, "dictionary")

    def execute(self, context):
        path = Path(self.filepath)
        if not path.exists():
            self.report({"ERROR"}, f"File {path} does not exist")
            return {"CANCELLED"}

        with path.open("r") as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):
                continue

            items = iter(line.split())
            marker_id = int(next(items))
            size = float(next(items))
            x, y, z = (float(next(items, 0)) for _ in range(3))
            rot_z, rot_y, rot_x = (float(next(items, 0)) for _ in range(3))

            bpy.ops.drone_show.add_aruco(
                size=size,
                marker_id=marker_id,
                dictionary=self.dictionary,
                location=(x, y, z),
                rotation=(rot_x, rot_y, rot_z),
            )

        return {"FINISHED"}