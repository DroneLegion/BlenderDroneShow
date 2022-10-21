from pathlib import Path

import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
from bpy_extras.object_utils import AddObjectHelper, object_data_add

from ..helpers import aruco as aruco_helpers


class AddAruco(Operator, AddObjectHelper):
    bl_idname = "drone_show.add_aruco"
    bl_label = "Add Aruco"
    bl_description = "Create singular Aruco marker object"
    bl_options = {"REGISTER", "UNDO"}

    size: bpy.props.FloatProperty(
        name="Size",
        description="Size of the Aruco marker",
        unit="LENGTH",
        default=0.22,
        min=0,
        soft_min=0.05,
        soft_max=10,
        step=10,
    )

    dictionary: bpy.props.EnumProperty(
        name="Dictionary",
        description="Dictionary of the Aruco marker",
        items=[
            ("aruco", "Aruco", "Standard Aruco dictionary"),
            ("4x4_1000", "4x4", "4x4 dictionary (default)"),
            ("5x5_1000", "5x5", "5x5 dictionary"),
            ("6x6_1000", "6x6", "6x6 dictionary"),
            ("7x7_1000", "7x7", "7x7 dictionary"),
        ],
        default="4x4_1000",
    )

    marker_id: bpy.props.IntProperty(
        name="Aruco ID",
        description="Aruco ID of the marker",
        default=0,
        min=0,
        max=1000,
    )

    @classmethod
    def poll(cls, context):
        if not super().poll(context):
            return False
        if context.active_object:
            return context.object.mode == "OBJECT"
        return True

    def execute(self, context):
        mesh = aruco_helpers.get_marker_mesh()
        aruco_object = object_data_add(context, mesh, operator=self)
        aruco_object.name = f"Aruco {self.marker_id}"
        aruco_object.show_name = True

        _, _, current_z = aruco_object.dimensions
        aruco_object.dimensions = [self.size, self.size, current_z]

        uv_layer = aruco_object.data.uv_layers.new(name="Aruco")
        uv_layer.data[0].uv = (0, 0)
        uv_layer.data[1].uv = (1, 0)
        uv_layer.data[2].uv = (1, 1)
        uv_layer.data[3].uv = (0, 1)

        aruco_object.aruco.is_aruco = True
        aruco_object.aruco.dictionary = self.dictionary
        aruco_object.aruco.marker_id = self.marker_id

        return {"FINISHED"}


class ExportAruco(Operator, ExportHelper):
    bl_idname = "drone_show.export_aruco"
    bl_label = "Export Aruco map"
    bl_description = "Export Aruco markers map"
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
        maxlen=255,  # Max internal buffer length, longer would be clamped.
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
            markers.append((marker_id, ) + tuple(data))

        headers = ("id", "length", "x", "y", "z", "rot_z", "rot_y", "rot_x")
        with path.open("w") as f:
            f.write("".join([f"{item: <8}" for item in headers])+"\n")
            for marker in markers:
                f.write("".join([f"{item: <8}" for item in marker])+"\n")

        return {"FINISHED"}
