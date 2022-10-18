import bpy
from bpy.types import Operator

from ..helpers import drone as drone_helpers
from ..helpers import led as led_helpers


class SetLedColor(Operator):
    bl_idname = "drone_show.set_leds"
    bl_label = "Set LEDs color"
    bl_description = "Set color of LED material of the selected drones (or all drones if nothing is selected)"

    def execute(self, context):
        drone_show = context.scene.drone_show
        drone_objects = drone_helpers.get_drone_objects(context, selected=bool(context.selected_objects))
        if not drone_objects:
            self.report({"WARNING"}, "No drones selected or available")
            return {'CANCELLED'}

        count = 0
        for drone_obj in drone_objects:
            try:
                led_material = led_helpers.get_led_material(drone_obj)
            except led_helpers.LedError as e:
                self.report({"WARNING"}, f"Drone '{drone_obj.name}': {str(e)}")
                continue
            else:
                led_helpers.set_material_color(led_material, drone_show.led_color, context.scene.frame_current)
                count += 1

        self.report({"INFO"}, f"Set LED color to {count} drones")
        return {"FINISHED"}
