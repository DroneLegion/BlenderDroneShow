import bpy
from bpy.types import Operator
from bpy_extras.object_utils import AddObjectHelper, object_data_add

from ...helpers import aruco as aruco_helpers

__all__ = ("AddAruco", )


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
