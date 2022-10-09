import itertools
import math
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Iterable, Iterator

import bpy
from bpy.types import Object, Operator

from ..helpers import animation
from ..helpers import drone as drone_helpers
from ..helpers import led as led_helpers


def neighbour_pairs(sequence):
    iterable = iter(sequence)
    try:
        prev = next(iterable)
    except StopIteration:
        return ()
    for item in iterable:
        yield prev, item
        prev = item


def compress_warnings_frames(
    warnings: Iterable[tuple[int, Any]]
) -> Iterator[tuple[tuple[int, int], list[Any]]]:
    for key, group in itertools.groupby(
        enumerate(warnings),
        lambda x: x[0] - x[1][0],
    ):
        group = [warning for _, warning in group]
        values = [warning[1] for warning in group]
        yield (group[0][0], group[-1][0]), values


def compress_warnings_drones(
    warnings: Iterable[tuple[tuple[int, int], tuple[Object, ...], list[Any]]]
) -> Iterator[tuple[tuple[int, int], set[Object], list[Any]]]:
    warnings = sorted(warnings, key=lambda x: x[0])
    for key, group in itertools.groupby(warnings, lambda x: x[0]):
        group = list(group)
        drones = set(drone for _, drones, _ in group for drone in drones)
        values = [value for _, _, value in group]
        yield key, drones, values


def check_speed(
    frames: list[animation.Frame], limit: float, frame_rate: int
) -> Iterator[tuple[int, float]]:
    for previous_frame, frame in neighbour_pairs(frames):
        distance = math.dist(previous_frame.position, frame.position)
        speed = distance * frame_rate
        if speed > limit:
            yield frame.number, speed


def check_distance_all(
    drones: dict[Object, list[animation.Frame]], limit: float
) -> Iterator[tuple[tuple[Object], Iterator[tuple[int, float]]]]:
    pairs = itertools.combinations(drones.items(), 2)
    for (drone1, frames1), (drone2, frames2) in pairs:
        yield (drone1, drone2), check_distance(frames1, frames2, limit)
        # for frame1, frame2 in zip(frames1, frames2):
        #     distance = math.dist(frame1.position, frame2.position)
        #     if distance < limit:
        #         yield frame1.number, (drone1, drone2), distance


def check_distance(frames1, frames2, limit: float) -> Iterator[tuple[int, float]]:
    for frame1, frame2 in zip(frames1, frames2):
        distance = math.dist(frame1.position, frame2.position)
        if distance < limit:
            yield frame1.number, distance


def format_drones(drone_objs: Iterable[Object]) -> str:
    drones = [drone.name for drone in drone_objs]
    return f"in {len(drones)} drone{'s' if len(drones)>1 else ''}: {', '.join(drones)}"


def format_frame_range(frame_range: tuple[int, int]) -> str:
    if frame_range[0] != frame_range[1]:
        frames = f"Frames {frame_range[0]}-{frame_range[1]}"
    else:
        frames = f"Frame {frame_range[0]}"
    return frames


class CheckSwarmAnimation(Operator):
    bl_idname = "drone_show.check"
    bl_label = "Check animation"
    bl_description = "Check drone show animation for errors"

    def execute(self, context):
        drone_show = context.scene.drone_show
        drone_objects = drone_helpers.get_drone_objects(context)

        if not drone_objects:
            self.report({"ERROR"}, "No drone objects found")
            return {"CANCELLED"}

        if (
            not drone_show.check_led
            and not drone_show.check_speed
            and not drone_show.check_distance
        ):
            self.report({"ERROR"}, "No checks enabled")
            return {"CANCELLED"}

        led_warnings = list()
        speed_warnings = list()
        distance_warnings = list()

        drones = dict()

        for drone_obj in drone_objects:
            try:
                led_material = led_helpers.get_led_material(drone_obj)
                led_helpers.get_material_color(
                    led_material
                )  # try getting material color to probe for errors
            except led_helpers.LedError as e:
                led_material = None
                if drone_show.check_led:
                    led_warnings.append((drone_obj, str(e)))

            if drone_show.check_speed or drone_show.check_distance:
                frames = list(
                    animation.extract_animation(context.scene, drone_obj, led_material)
                )
                drones[drone_obj] = frames

            if drone_show.check_speed:
                s_warn = check_speed(
                    frames, drone_show.speed_limit, context.scene.render.fps
                )
                s_warn = compress_warnings_frames(s_warn)
                s_warn = (
                    (frame_range, (drone_obj,), max(values))
                    for frame_range, values in s_warn
                )
                speed_warnings.extend(s_warn)

        if drone_show.check_distance:
            d_warns = check_distance_all(drones, drone_show.distance_limit)
            for drones, warnings in d_warns:
                warnings = compress_warnings_frames(warnings)
                d_warn = (
                    (frame_range, drones, min(values))
                    for frame_range, values in warnings
                )
                distance_warnings.extend(d_warn)

        no_warnings = True

        max_speed = 0
        if speed_warnings:
            no_warnings = False
            for frame_range, drones, speeds in compress_warnings_drones(speed_warnings):
                range_max = max(speeds)
                max_speed = max(max_speed, range_max)

                self.report(
                    {"WARNING"},
                    f"{format_frame_range(frame_range)}: "
                    f"Speed exceeds {drone_show.speed_limit:.1f}m/s "
                    f"(max {range_max:.1f}m/s) {format_drones(drones)}",
                )

        min_distance = float("inf")
        if distance_warnings:
            no_warnings = False
            for frame_range, drones, distances in compress_warnings_drones(
                distance_warnings
            ):
                range_min = max(distances)
                min_distance = min(min_distance, range_min)

                self.report(
                    {"WARNING"},
                    f"{format_frame_range(frame_range)}: "
                    f"Distance is less than {drone_show.distance_limit:.1f}m "
                    f"(min {range_min:.1f}m) {format_drones(drones)}",
                )

        if led_warnings:
            no_warnings = False
            for key, group in itertools.groupby(
                led_warnings, lambda warning: warning[1]
            ):  # group by error message
                self.report(
                    {"WARNING"},
                    f"LED: {key} {format_drones(drone for drone, _ in group)}",
                )

        # Summary reports

        if max_speed > 0:
            self.report(
                {"WARNING"},
                f"Max speed was exceeded: {max_speed:.1f}m/s (allowed {drone_show.speed_limit:.1f}m/s)",
            )

        if min_distance < float("inf"):
            self.report(
                {"WARNING"},
                f"Min distance was exceeded: {min_distance:.1f}m (allowed {drone_show.distance_limit:.1f}m)",
            )

        self.report(
            {"INFO"},
            f"Performed checks for {len(drone_objects)} drones ({'no warnings' if no_warnings else 'click for details'})",
        )
        return {"FINISHED"}
