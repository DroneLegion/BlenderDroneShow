from bpy.types import Panel

from .checks import draw_check_properties


class DroneOperatorsPanel(Panel):
    bl_idname = "VIEW3D_PT_drone_operators"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Drone show"
    bl_label = "Drones operators"

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.operator("drone_show.assign")
        col.operator("drone_show.select")


class CheckPanel(Panel):
    bl_idname = "VIEW3D_PT_drone_check"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Drone show"
    bl_label = "Pre-flight checks"

    def draw(self, context):
        layout = self.layout
        drone_show = context.scene.drone_show

        draw_check_properties(drone_show, layout)
        layout.separator()
        col = layout.column(align=True)
        col.operator("drone_show.check")
