from dataclasses import dataclass
from typing import Optional

from bpy.types import Material, Object, Scene
from mathutils import Vector

from ..helpers import led as led_helpers


@dataclass()
class Frame:
    number: int
    position: Vector
    yaw: float
    led_color: Optional[tuple[int, int, int]] = None

    @property
    def position_round(self) -> tuple[float, ...]:
        return tuple(round(coord, 3) for coord in self.position)

    @property
    def yaw_round(self) -> float:
        return round(self.yaw, 3)

    @property
    def led_color_export(self) -> tuple[int, int, int]:
        if self.led_color is None:
            return 0, 0, 0
        return self.led_color

    def shift(self, other: "Frame") -> None:
        self.position -= other.position
        self.yaw -= other.yaw


def extract_animation(
    scene: Scene,
    drone_obj: Object,
    led_material: Optional[Material],
    local_coordinates=False,
):
    if local_coordinates:
        scene.frame_set(scene.frame_start)
        origin_frame = extract_frame(scene.frame_start, drone_obj)
    else:
        origin_frame = None

    for frame_number in range(scene.frame_start, scene.frame_end + 1):
        scene.frame_set(frame_number)
        frame = extract_frame(frame_number, drone_obj, led_material, shift_frame=origin_frame)
        yield frame


def extract_frame(
    frame_number, drone_obj: Object, led_material: Optional[Material] = None, shift_frame: Optional[Frame] = None
) -> Frame:
    number = frame_number
    position = drone_obj.matrix_world.to_translation()
    yaw = drone_obj.matrix_world.to_euler("XYZ")[2]

    frame = Frame(number=number, position=position, yaw=yaw)
    if shift_frame:
        frame.shift(shift_frame)

    if led_material is not None:
        frame.led_color = led_helpers.get_material_color(led_material)

    return frame
