from bpy.types import Panel

from ..helpers import led as led_helpers


class LedPanel(Panel):
    bl_idname = "MATERIAL_PT_led"
    bl_label = "Drone show LED"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        return (
            context.object.drone.is_drone
            and context.material is not None
            and not context.material.grease_pencil
        )

    def draw_header(self, context):
        self.layout.prop(context.material.led, "is_led", text="")

    def draw(self, context):
        layout = self.layout
        layout.enabled = context.material.led.is_led

        row = layout.row()
        if not context.material.led.is_led:
            row.label(text="Not a designated LED material")
            return

        try:
            r, g, b = led_helpers.get_material_color(context.material)
        except led_helpers.LedError as e:
            row.label(text=str(e), icon="ERROR")
        else:
            row.label(text=f"R = {r:03d}")
            row.label(text=f"G = {g:03d}")
            row.label(text=f"B = {b:03d}")
