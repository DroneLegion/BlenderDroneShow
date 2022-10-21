import bpy
from bpy.types import Operator
from bpy_extras.object_utils import AddObjectHelper, object_data_add, add_object_align_init
from mathutils import Vector, Euler, Matrix

from ...helpers import aruco as aruco_helpers

__all__ = ("GenerateArucoMap", )


class GenerateArucoMap(Operator, AddObjectHelper):
    bl_idname = "drone_show.generate_aruco_map"
    bl_label = "Generate Aruco map"
    bl_description = "Generates a map of Aruco marker objects"
    bl_options = {"REGISTER", "UNDO"}

    z_rotation: bpy.props.FloatProperty(
        name="Z Rotation",
        description="Individual rotation of markers",
        unit="ROTATION",
        default=0,
    )

    size: bpy.props.FloatProperty(
        name="Marker size",
        description="Size of Aruco markers",
        unit="LENGTH",
        default=0.22,
        min=0,
        soft_min=0.05,
        soft_max=10,
        step=10,
    )

    dictionary: bpy.props.EnumProperty(
        name="Dictionary",
        description="Dictionary of Aruco markers",
        items=[
            ("aruco", "Aruco", "Standard Aruco dictionary"),
            ("4x4_1000", "4x4", "4x4 dictionary (default)"),
            ("5x5_1000", "5x5", "5x5 dictionary"),
            ("6x6_1000", "6x6", "6x6 dictionary"),
            ("7x7_1000", "7x7", "7x7 dictionary"),
        ],
        default="4x4_1000",
    )

    first_id: bpy.props.IntProperty(
        name="First ID",
        description="Aruco ID of the first marker",
        default=0,
        min=0,
        max=1000,
    )

    add_rim: bpy.props.BoolProperty(
        name="Add white rim",
        description="Add white rim around markers",
        default=True,
    )

    rim_size: bpy.props.FloatProperty(
        name="Rim size",
        description="Size of the white rim around markers",
        unit="LENGTH",
        default=0.05,
        min=0,
        soft_min=0.01,
        soft_max=1,
        step=1,
    )

    markers_x: bpy.props.IntProperty(
        name="Markers X",
        description="Number of markers in X direction (rows)",
        min=1,
        soft_max=10,
        default=5
    )

    markers_y: bpy.props.IntProperty(
        name="Markers Y",
        description="Number of markers in Y direction (columns)",
        min=1,
        soft_max=10,
        default=5
    )

    x_gap: bpy.props.FloatProperty(
        name="X gap",
        description="Gap between markers in X direction",
        unit="LENGTH",
        min=0,
        soft_max=10,
        default=1,
        step=10,
    )

    y_gap: bpy.props.FloatProperty(
        name="Y gap",
        description="Gap between markers in Y direction",
        unit="LENGTH",
        min=0,
        soft_max=10,
        default=1,
        step=10,
    )

    first_corner: bpy.props.EnumProperty(
        name="First corner",
        description="Corner of the first marker",
        items=[
            ("TOP_LEFT", "Top left", "Top left corner"),
            ("BOTTOM_LEFT", "Bottom left", "Bottom left corner"),
            ("TOP_RIGHT", "Top right", "Top right corner"),
            ("BOTTOM_RIGHT", "Bottom right", "Bottom right corner"),
        ],
        default="TOP_LEFT",
    )

    direction: bpy.props.EnumProperty(
        name="Direction",
        description="Direction of markers enumeration",
        items=[
            ("HORIZONTAL", "Horizontal", "Horizontal direction (along rows)"),
            ("VERTICAL", "Vertical", "Vertical direction (along columns)"),
        ],
        default="VERTICAL",
    )

    origin: bpy.props.EnumProperty(
        name="Origin",
        description="Origin of the marker",
        items=[
            ("TOP_LEFT", "Top left", "Top left corner"),
            ("BOTTOM_LEFT", "Bottom left", "Bottom left corner"),
            ("TOP_RIGHT", "Top right", "Top right corner"),
            ("BOTTOM_RIGHT", "Bottom right", "Bottom right corner"),
            ("CENTER", "Center", "Center of map"),
            ("CENTER_LEFT", "Center left", "Center of the left side of the map"),
            ("CENTER_RIGHT", "Center right", "Center of the right side of the map"),
            ("CENTER_TOP", "Center top", "Center of the top side of the map"),
            ("CENTER_BOTTOM", "Center bottom", "Center of the bottom side of the map"),
        ],
        default="BOTTOM_LEFT",
    )

    @classmethod
    def poll(cls, context):
        if not super().poll(context):
            return False
        if context.active_object:
            return context.object.mode == "OBJECT"
        return True

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.prop(self, "align")
        layout.prop(self, "location")
        layout.prop(self, "rotation")
        layout.prop(self, "z_rotation")
        layout.prop(self, "size")
        layout.prop(self, "markers_x")
        layout.prop(self, "markers_y")
        layout.prop(self, "x_gap")
        layout.prop(self, "y_gap")
        layout.prop(self, "first_id")
        layout.prop(self, "first_corner")
        layout.prop(self, "direction")
        layout.prop(self, "origin")

        row = layout.row(heading="White rim")
        row.prop(self, "add_rim", text="")
        subrow = row.row()
        subrow.enabled = self.add_rim
        subrow.prop(self, "rim_size", text="Size")

        layout.prop(self, "dictionary")

    def execute(self, context):
        total_x = (self.markers_x-1) * self.x_gap
        total_y = (self.markers_y-1) * self.y_gap

        empty_object = object_data_add(context, None, operator=self)
        empty_object.name = "Aruco map"
        empty_object.empty_display_type = "PLAIN_AXES"
        empty_object.empty_display_size = 0.5

        if self.origin == "TOP_LEFT":
            offset_x = 0
            offset_y = -total_y
        elif self.origin == "BOTTOM_LEFT":
            offset_x = 0
            offset_y = 0
        elif self.origin == "TOP_RIGHT":
            offset_x = -total_x
            offset_y = -total_y
        elif self.origin == "BOTTOM_RIGHT":
            offset_x = -total_x
            offset_y = 0
        elif self.origin == "CENTER":
            offset_x = -total_x / 2
            offset_y = -total_y / 2
        elif self.origin == "CENTER_LEFT":
            offset_x = 0
            offset_y = -total_y / 2
        elif self.origin == "CENTER_RIGHT":
            offset_x = -total_x
            offset_y = -total_y / 2
        elif self.origin == "CENTER_TOP":
            offset_x = -total_x / 2
            offset_y = -total_y
        elif self.origin == "CENTER_BOTTOM":
            offset_x = -total_x / 2
            offset_y = 0
        else:
            offset_x = 0
            offset_y = 0

        origin = add_object_align_init(context, self)

        for y in range(self.markers_y):
            for x in range(self.markers_x):
                if self.first_corner == "BOTTOM_LEFT":
                    id_offset_x = x
                    id_offset_y = y
                elif self.first_corner == "TOP_LEFT":
                    id_offset_x = x
                    id_offset_y = self.markers_y - y - 1
                elif self.first_corner == "BOTTOM_RIGHT":
                    id_offset_x = self.markers_x - x - 1
                    id_offset_y = y
                elif self.first_corner == "TOP_RIGHT":
                    id_offset_x = self.markers_x - x - 1
                    id_offset_y = self.markers_y - y - 1
                else:
                    id_offset_x = 0
                    id_offset_y = 0

                if self.direction == "HORIZONTAL":
                    marker_id = self.first_id + id_offset_y * self.markers_x + id_offset_x
                else:
                    marker_id = self.first_id + id_offset_x * self.markers_y + id_offset_y

                pos_x = x * self.x_gap + offset_x
                pos_y = y * self.y_gap + offset_y

                pos = self.location + (Vector((pos_x, pos_y, 0)) @ origin.inverted())
                rot = self.rotation.copy()
                rot.rotate_axis("Z", self.z_rotation)

                bpy.ops.drone_show.add_aruco(
                    align=self.align,
                    location=pos,
                    rotation=rot,
                    size=self.size,
                    dictionary=self.dictionary,
                    marker_id=marker_id,
                    add_rim=self.add_rim,
                    rim_size=self.rim_size,
                )
                aruco_object = context.active_object
                aruco_object.parent = empty_object
                aruco_object.matrix_parent_inverse = empty_object.matrix_world.inverted()
                aruco_object.select_set(False)

        empty_object.select_set(True)
        bpy.context.view_layer.objects.active = empty_object

        return {"FINISHED"}
