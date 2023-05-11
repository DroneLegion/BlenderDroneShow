import bpy
from bpy.types import Operator
from mathutils import Color

from ...helpers import drone as drone_helpers
from ...helpers import led as led_helpers

__all__ = ("SetLedColor", "SetLedRainbow")


class SetLedColor(Operator):
    bl_idname = "drone_show.set_leds"
    bl_label = "Set LEDs color"
    bl_description = "Set color of LED material of the selected drones (or all drones if nothing is selected)"

    def execute(self, context):
        drone_show = context.scene.drone_show
        drone_objects = drone_helpers.get_drone_objects(
            context, selected=bool(context.selected_objects)
        )
        if not drone_objects:
            self.report({"WARNING"}, "No drones selected or available")
            return {"CANCELLED"}

        count = 0
        for drone_obj in drone_objects:
            try:
                led_material = led_helpers.get_led_material(drone_obj)
            except led_helpers.LedError as e:
                self.report({"WARNING"}, f"Drone '{drone_obj.name}': {str(e)}")
                continue
            else:
                led_helpers.set_material_color(
                    led_material, drone_show.led_color, context.scene.frame_current
                )
                count += 1

        self.report({"INFO"}, f"Set LED color to {count} drones")
        return {"FINISHED"}


class SetLedRainbow(Operator):
    bl_idname = "drone_show.set_leds_rainbow"
    bl_label = "Set LEDs rainbow"
    bl_description = "Set rainbow animation of LED material of the selected drones (or all drones if nothing is selected)"

    staggered: bpy.props.BoolProperty(
        name="Staggered",
        description="Stagger the rainbow animation between drones",
        default=True,
    )

    stagger_offset: bpy.props.FloatProperty(
        name="Stagger offset",
        description="Offset the staggered rainbow animation",
        default=0,
        min=0,
        max=1,
        step=1,
    )

    duration: bpy.props.IntProperty(
        name="Duration",
        description="Duration of the rainbow animation",
        default=200,
        min=1,
    )

    frequency: bpy.props.IntProperty(
        name="Keyframe frequency",
        description="Frequency of keyframes",
        default=10,
        min=1,
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=200)

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        layout.prop(self, "staggered")
        layout.prop(self, "stagger_offset")

        layout.separator()
        layout.prop(self, "duration")
        layout.prop(self, "frequency")

    def execute(self, context):
        drone_show = context.scene.drone_show
        drone_objects = drone_helpers.get_drone_objects(
            context, selected=bool(context.selected_objects)
        )
        drone_objects = sorted(drone_objects, key=lambda obj: obj.name)

        if not drone_objects:
            self.report({"WARNING"}, "No drones selected or available")
            return {"CANCELLED"}

        count = 0
        start_frame = context.scene.frame_current

        for drone_obj in drone_objects:
            try:
                led_material = led_helpers.get_led_material(drone_obj)
            except led_helpers.LedError as e:
                self.report({"WARNING"}, f"Drone '{drone_obj.name}': {str(e)}")
                continue
            else:
                frame_range = range(
                    start_frame,
                    start_frame + self.duration + self.frequency,
                    self.frequency
                )
                for frame_number in frame_range:
                    hue_stagger = count / len(drone_objects) if self.staggered else 0
                    hue = (frame_number - start_frame) / self.duration + hue_stagger + self.stagger_offset

                    color = Color()
                    color.hsv = (hue % 1, 1, 1)
                    rgb = (color.r, color.g, color.b, 1)

                    led_helpers.set_material_color(
                        led_material, rgb, frame_number
                    )
                count += 1

        self.report({"INFO"}, f"Set LED rainbow to {count} drones")
        return {"FINISHED"}
