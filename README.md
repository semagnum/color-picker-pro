# Color Picker Pro
This Blender addon extends functionality of the software's color picker.

Please consider contributing by buying from the [Blender Market](https://blendermarket.com/products/color-picker-pro) (which funds Blender) or directly to me via Paypal.

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donate_SM.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=LLDQGZ94K3ZUW&currency_code=USD&source=url)


## Average Color Picker
Allows you to color pick anywhere in the Blender window in a 3x3 or 5x5 tile around your cursor.
As you hover your cursor, the panels will update with the tile's max, min, mean, and median colors. 
Left mouse click to save the colors and stop the color picker.
Press the right mouse button or the escape button to stop the color picker without saving the colors.

## Rectangle Color Picker
Left click to pin one "corner" of the rectangle. 
Afterwards, right click to pin the opposite "corner" of the rectangle (you can go in any direction). 
After pinning both corners, the operator will extract the rectangle's max, min, mean, and median.
Press escape (or right click, if you haven't left-clicked yet) to cancel.

**Note**: these values are gamma corrected, so they reflect the values you see on the screen, *not* the true values in Blender before the colorspace conversion.

## Update Color Properties

Beside each of the color picker results,
there is now a button to update other data properties in the file.
Once the user provides a data path
(which can be found by right-clicking a color property and selecting "Copy Full Data Path"),
the add-on will automatically update the color property as the picker's color gets updated.

**NOTE**: Since Blender gamma-corrects some color properties,
results may not be as expected in some cases.
But it seems like most painting tools (vertex paint, texture paint)
does not have this conversion, and colors should match one-to-one.