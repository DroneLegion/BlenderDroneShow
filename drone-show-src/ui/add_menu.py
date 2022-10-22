import bpy
from bpy.types import Menu

__all__ = ("AddMenu",)


class AddMenu(Menu):
    bl_idname = "OBJECT_MT_drone_show"
    bl_label = "Drone show"

    def draw(self, context):
        layout = self.layout

        layout.operator("drone_show.add_aruco", text="Aruco marker")
        layout.operator("drone_show.generate_aruco_map", text="Aruco markers map")
