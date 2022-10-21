from bpy.types import Panel

from .checks import draw_check_properties


class DroneOperatorsPanel(Panel):
    bl_idname = "VIEW3D_PT_drone"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Drone show"
    bl_label = "Drones operators"

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.operator("drone_show.assign")
        col.operator("drone_show.select")


class LedOperatorsPanel(Panel):
    bl_idname = "VIEW3D_PT_led"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Drone show"
    bl_label = "LEDs operators"

    def draw(self, context):
        layout = self.layout
        drone_show = context.scene.drone_show

        col = layout.column(align=True)
        col.prop(drone_show, "led_color", text="")
        col.operator("drone_show.set_leds")


class AnimationPanel(Panel):
    bl_idname = "VIEW3D_PT_animation"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Drone show"
    bl_label = "Animation operators"

    def draw(self, context):
        layout = self.layout
        drone_show = context.scene.drone_show

        draw_check_properties(drone_show, layout)

        layout.separator()

        col = layout.column(align=True)
        col.operator("drone_show.check")
        col.operator("drone_show.export_animation")


class ArucoOperatorsPanel(Panel):
    bl_idname = "VIEW3D_PT_aruco"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Drone show"
    bl_label = "Aruco operators"

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.operator("drone_show.add_aruco")
        col.operator("drone_show.generate_aruco_map")

        col = layout.column(align=True)
        col.operator("drone_show.import_aruco")
        col.operator("drone_show.export_aruco")
