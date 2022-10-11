def draw_check_properties(drone_show, layout):
    # Yes this is a wierd way to do it, but it allows for checkboxes to align properly
    row = layout.row()
    row.prop(drone_show, "detailed_warnings", text="")
    subrow = row.row()
    subrow.enabled = drone_show.detailed_warnings
    subrow.label(text="Show detailed warnings")

    row = layout.row()
    row.prop(drone_show, "check_led", text="")
    subrow = row.row()
    subrow.enabled = drone_show.check_led
    subrow.label(text="Check LEDs")

    row = layout.row()
    row.prop(drone_show, "check_speed", text="")
    subrow = row.row()
    subrow.enabled = drone_show.check_speed
    subrow.prop(drone_show, "speed_limit")

    row = layout.row()
    row.prop(drone_show, "check_distance", text="")
    subrow = row.row()
    subrow.enabled = drone_show.check_distance
    subrow.prop(drone_show, "distance_limit")
