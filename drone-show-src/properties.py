import bpy
from bpy.types import PropertyGroup

from .helpers import aruco as aruco_helpers


class DroneShowProperties(PropertyGroup):
    # Check properties
    check_led: bpy.props.BoolProperty(
        name="Check LEDs",
        description="Check LEDs material on drones",
        default=True,
        options=set(),
    )

    check_speed: bpy.props.BoolProperty(
        name="Check speed",
        description="Check maximum drone movement speed",
        default=True,
        options=set(),
    )

    speed_limit: bpy.props.FloatProperty(
        name="Speed limit",
        description="Limit of maximum drone movement speed (m/s)",
        unit="VELOCITY",
        default=3,
        min=0,
        soft_min=0.5,
        soft_max=20,
        step=50,
    )

    check_distance: bpy.props.BoolProperty(
        name="Check distance",
        description="Check distance between drones",
        default=True,
        options=set(),
    )

    distance_limit: bpy.props.FloatProperty(
        name="Distance limit",
        description="Closest possible distance between drones (m)",
        unit="LENGTH",
        default=1.5,
        min=0,
        soft_min=0.5,
        soft_max=10,
        step=50,
    )

    detailed_warnings: bpy.props.BoolProperty(
        name="Show detailed warnings",
        description="Show detailed animation check warnings",
        default=True,
        options=set(),
    )

    # Led properties
    led_color: bpy.props.FloatVectorProperty(
        name="LED color",
        description="Color of the LED to set",
        subtype="COLOR",
        size=4,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0, 1.0),
    )


class DroneObjectProperties(PropertyGroup):
    is_drone: bpy.props.BoolProperty(
        name="Is drone",
        default=False,
        options=set(),
    )


class DroneLedProperties(PropertyGroup):
    is_led: bpy.props.BoolProperty(
        name="Is LED color",
        default=False,
        options=set(),
    )


class ArucoObjectProperties(PropertyGroup):
    def aruco_updated(self, context):
        if not self.is_aruco:
            return
        aruco_helpers.update_aruco_material(self.id_data)
        self.id_data.name = f"Aruco {self.marker_id}"

    is_aruco: bpy.props.BoolProperty(
        name="Is Aruco",
        default=False,
        options=set(),
    )

    dictionary: bpy.props.EnumProperty(
        name="Dictionary",
        description="Dictionary of the Aruco marker",
        items=[
            ("aruco", "Aruco", "Standard Aruco dictionary"),
            ("4x4_1000", "4x4", "4x4 dictionary (default)"),
            ("5x5_1000", "5x5", "5x5 dictionary"),
            ("6x6_1000", "6x6", "6x6 dictionary"),
            ("7x7_1000", "7x7", "7x7 dictionary"),
        ],
        default="4x4_1000",
        update=aruco_updated,
        options=set(),
    )

    marker_id: bpy.props.IntProperty(
        name="Marker ID",
        description="Aruco marker ID",
        default=0,
        min=0,
        max=1000,
        update=aruco_updated,
        options=set(),
    )
