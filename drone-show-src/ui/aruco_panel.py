from bpy.types import Panel

__all__ = ("ArucoPanel", "ArucoCoordsPanel")


class ArucoPanel(Panel):
    bl_idname = "OBJECT_PT_aruco"
    bl_label = "Aruco marker"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return context.object is not None and not context.object.drone.is_drone

    def draw_header(self, context):
        self.layout.prop(context.object.aruco, "is_aruco", text="")

    def draw(self, context):
        layout = self.layout
        aruco = context.object.aruco
        layout.enabled = aruco.is_aruco
        layout.use_property_split = True

        layout.prop(aruco, "dictionary")
        layout.prop(aruco, "marker_id")


class ArucoCoordsPanel(Panel):
    bl_idname = "OBJECT_PT_aruco_coords"
    bl_label = "Global coordinates"
    bl_parent_id = "OBJECT_PT_aruco"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        aruco = context.object.aruco
        layout.enabled = aruco.is_aruco

        x, y, z = context.object.matrix_world.to_translation()
        rot_x, rot_y, rot_z = context.object.matrix_world.to_euler("XYZ")

        col = layout.column()
        col.label(text="Position (meters)")
        row = col.row()
        row.label(text=f"X = {x:.3f}")
        row.label(text=f"Y = {y:.3f}")
        row.label(text=f"Z = {z:.3f}")

        layout.separator()

        col = layout.column()
        col.label(text="Rotation (radians)")
        row = col.row()
        row.label(text=f"Z = {rot_z:.3f}")
        row.label(text=f"Y = {rot_y:.3f}")
        row.label(text=f"X = {rot_x:.3f}")
