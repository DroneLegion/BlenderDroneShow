import bpy
from bpy.types import Operator

from ...helpers import drone as drone_helpers

__all__ = ("SelectDrones", )


class SelectDrones(Operator):
    bl_idname = "drone_show.select"
    bl_label = "Select drones"
    bl_description = "Select all drone objects"

    def execute(self, context):
        bpy.ops.object.select_all(action="DESELECT")

        drones = drone_helpers.get_drone_objects(context)
        first = True
        for drone_obj in drones:
            drone_obj.select_set(True)
            if first:
                first = False
                bpy.context.view_layer.objects.active = drone_obj

        return {"FINISHED"}
