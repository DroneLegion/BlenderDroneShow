import bpy
from bpy.types import Operator

from ...helpers import drone as drone_helpers

__all__ = ("AssignDrones", )


class AssignDrones(Operator):
    bl_idname = "drone_show.assign"
    bl_label = "Assign drones"
    bl_description = "Assign selected objects as drones"

    def execute(self, context):
        for drone_obj in context.selected_objects:
            drone_obj.drone.is_drone = True

        bpy.ops.object.select_all(action="DESELECT")
        return {"FINISHED"}
