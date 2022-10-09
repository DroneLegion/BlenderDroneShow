from bpy.types import Panel


class DroneOperatorsPanel(Panel):
    bl_idname = "VIEW3D_drone_operators"
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
    bl_idname = "VIEW3D_drone_check"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Drone show"
    bl_label = "Pre-flight checks"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(context.scene.drone_show, "check_led", text="")
        subrow = row.row()
        subrow.enabled = context.scene.drone_show.check_led
        subrow.label(text="Check LEDs")

        row = layout.row()
        row.prop(context.scene.drone_show, "check_speed", text="")
        subrow = row.row()
        subrow.enabled = context.scene.drone_show.check_speed
        subrow.prop(context.scene.drone_show, "speed_limit")

        row = layout.row()
        row.prop(context.scene.drone_show, "check_distance", text="")
        subrow = row.row()
        subrow.enabled = context.scene.drone_show.check_distance
        subrow.prop(context.scene.drone_show, "distance_limit")

        col = layout.column(align=True)
        col.operator("drone_show.check")
