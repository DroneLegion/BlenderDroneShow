from bpy.types import Object


def get_drone_objects(context) -> list[Object]:
    return [obj for obj in context.scene.objects if obj.drone.is_drone]
