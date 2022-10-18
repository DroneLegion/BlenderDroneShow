from bpy.types import Panel

from ..helpers import led as led_helpers


class DronePanel(Panel):
    bl_idname = "OBJECT_PT_drone"
    bl_label = "Swarm Drone"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def draw_header(self, context):
        self.layout.prop(context.object.drone, "is_drone", text="")

    def draw(self, context):
        layout = self.layout
        drone = context.object.drone
        layout.enabled = drone.is_drone


class DroneCoordsPanel(Panel):
    bl_idname = "OBJECT_PT_drone_coords"
    bl_label = "Global coordinates"
    bl_parent_id = "OBJECT_PT_drone"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        drone = context.object.drone
        layout.enabled = drone.is_drone

        x, y, z = context.object.matrix_world.to_translation()
        yaw = context.object.matrix_world.to_euler("XYZ")[2]

        row = layout.row()
        row.label(text=f"X = {x:.2f}")
        row.label(text=f"Y = {y:.2f}")
        row.label(text=f"Z = {z:.2f}")

        row = layout.row()
        row.label(text=f"yaw = {yaw:.2f} rad")


class DroneLedPanel(Panel):
    bl_idname = "OBJECT_PT_drone_led"
    bl_label = "LED info"
    bl_parent_id = "OBJECT_PT_drone"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        drone = context.object.drone
        layout.enabled = drone.is_drone

        row = layout.row()

        try:
            led_material = led_helpers.get_led_material(context.object)
            r, g, b = led_helpers.get_material_color(led_material)
        except led_helpers.LedError as e:
            row.label(text=str(e), icon="ERROR")
        else:
            row.label(text=f"R = {r:03d}")
            row.label(text=f"G = {g:03d}")
            row.label(text=f"B = {b:03d}")
