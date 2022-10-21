from pathlib import Path

import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from bpy_extras.object_utils import object_data_add

from ...helpers import aruco as aruco_helpers

__all__ = ("ImportAruco",)


class ImportAruco(Operator, ImportHelper):
    bl_idname = "drone_show.import_aruco"
    bl_label = "Import Aruco map"
    bl_description = "Import Aruco map file as marker objects"
    filename_ext = ".txt"

    bl_options = {"REGISTER", "UNDO"}

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

    add_rim: bpy.props.BoolProperty(
        name="Add white rim",
        description="Add white rim around the marker",
        default=True,
    )

    rim_size: bpy.props.FloatProperty(
        name="Rim size",
        description="Size of the white rim around the marker",
        unit="LENGTH",
        default=0.05,
        min=0,
        soft_min=0.01,
        soft_max=1,
        step=1,
    )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        row = layout.row()
        row.prop(self, "dictionary")

        row = layout.row(heading="White rim")
        row.prop(self, "add_rim", text="")
        subrow = row.row()
        subrow.enabled = self.add_rim
        subrow.prop(self, "rim_size", text="Size")

    def execute(self, context):
        path = Path(self.filepath)
        if not path.exists():
            self.report({"ERROR"}, f"File {path} does not exist")
            return {"CANCELLED"}

        with path.open("r") as f:
            lines = f.readlines()

        aruco_objects = []

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
                add_rim=self.add_rim,
                rim_size=self.rim_size,
            )

            aruco_objects.append(context.active_object)

        if not aruco_objects:
            self.report({"WARNING"}, "No Aruco markers found in the file")
            return {"CANCELLED"}

        empty_object = object_data_add(context, None)
        empty_object.name = path.stem
        empty_object.empty_display_type = "PLAIN_AXES"
        empty_object.empty_display_size = 0.5

        empty_object.location = bpy.context.scene.cursor.location

        for aruco_object in aruco_objects:
            aruco_object.parent = empty_object
            aruco_object.matrix_parent_inverse = empty_object.matrix_world.inverted()

            aruco_object.select_set(False)

        empty_object.select_set(True)
        context.view_layer.objects.active = empty_object

        return {"FINISHED"}
