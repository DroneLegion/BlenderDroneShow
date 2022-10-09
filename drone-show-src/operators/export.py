import csv
from pathlib import Path

import bpy
from bpy.props import BoolProperty, FloatProperty, IntProperty, StringProperty
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper

from ..helpers import animation as animation_helpers
from ..helpers import drone as drone_helpers
from ..helpers import led as led_helpers


class ExportSwarmAnimation(Operator, ExportHelper):
    bl_idname = "drone_show.export"
    bl_label = "Export drone show animation"
    filename_ext = ""
    use_filter_folder = True

    filepath: StringProperty(
        name="File Path",
        description="Directory path used for exporting CSV files",
        maxlen=1024,
        subtype="DIR_PATH",
        default="",
    )

    perform_checks: bpy.props.BoolProperty(
        name="Perform checks",
        description="Perform checks during export",
        default=True,
    )

    def draw(self, context):
        drone_show = context.scene.drone_show

        layout = self.layout
        col = layout.column()
        col.prop(self, "perform_checks")
        if self.perform_checks:
            col.prop(drone_show, "detailed_warnings")
            col.separator()
            col.prop(drone_show, "speed_limit")
            col.prop(drone_show, "distance_limit")
        col.separator()

    def execute(self, context):
        base_dir = Path(self.filepath)
        base_dir.mkdir(exist_ok=True)

        drone_objects = drone_helpers.get_drone_objects(context)
        frame_start = context.scene.frame_start
        frame_end = context.scene.frame_end

        for drone_num, drone_obj in enumerate(drone_objects):
            filepath = base_dir / f"{drone_obj.name}.csv"
            with open(filepath, "w") as csv_file:
                animation_writer = csv.writer(
                    csv_file, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL
                )
                animation_writer.writerow([Path(bpy.data.filepath).stem])

                try:
                    led_material = led_helpers.get_led_material(drone_obj)
                    led_helpers.get_material_color(
                        led_material
                    )  # try getting material color to probe for errors
                except led_helpers.LedError as e:
                    led_material = None
                    self.report({"WARNING"}, f"Drone '{drone_obj.name}': {str(e)}")

                frames = animation_helpers.extract_animation(
                    context.scene, drone_obj, led_material
                )
                for frame in frames:
                    animation_writer.writerow(
                        (
                            frame.number,
                            *frame.position_round,
                            frame.yaw_round,
                            *frame.led_color_export,
                        )
                    )

            self.report(
                {"INFO"},
                f"Animation file exported for drone '{drone_obj.name}' ({drone_num}/{len(drone_objects)})",
            )

        self.report(
            {"INFO"},
            f"Exported animation for {len(drone_objects)} drones ({frame_end - frame_start + 1} frames)",
        )
        return {"FINISHED"}
