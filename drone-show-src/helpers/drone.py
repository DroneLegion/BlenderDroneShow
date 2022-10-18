from bpy.types import Object


def get_drone_objects(context, selected=False) -> list[Object]:
    objects = context.selected_objects if selected else context.scene.objects
    return [obj for obj in objects if obj.drone.is_drone]
