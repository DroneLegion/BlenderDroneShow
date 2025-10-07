# Blender animation export add-on

This add-on allows you to export animations of designated drone objects from Blender to `.csv` files that can be used for drone show software.

Export result is a folder with .csv files where each line  in file represents a sequence with comma delimiter:

* `x, y, z` coordinates of an object in meters
* `yaw` of an object in radians
* `red, green, blue` values of the color of an object, each is integer from 0 to 255

* 
1. Open Blender
2. Go to **Edit > Preferences > Add-ons**
3. Click **Install from File...**
4. Select the `drone-show-src.zip` file
5. Enable the add-on by checking the box next to "Drone Show Animation (.csv)"
