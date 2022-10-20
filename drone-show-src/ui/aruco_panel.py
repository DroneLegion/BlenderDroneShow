from bpy.types import Panel


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
