# Blender animation export add-on

This add-on allows you to export animations of designated drone objects from Blender to `.csv` files that can be used for drone show software.

Export result is a folder with .csv files where each line  in file represents a sequence with comma delimiter:

* `x, y, z` coordinates of an object in meters
* `yaw` of an object in radians
* `red, green, blue` values of the color of an object, each is integer from 0 to 255

