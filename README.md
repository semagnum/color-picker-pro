# Color Picker Pro
This Blender addon extends functionality of the software's color picker.

Please consider contributing by buying from the [Blender Market](https://blendermarket.com/products/color-picker-pro) (which funds Blender) or directly to me via Paypal.

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donate_SM.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=LLDQGZ94K3ZUW&currency_code=USD&source=url)


## Average Color Picker
Color pick anywhere in the Blender window.  Based on the button you press, the operator will either extract a 3x3 or 5x5 square of pixels and update the panels with the square's max, min, mean, and median.  Left mouse click to save the colors and close.  Press the right mouse button or the escape button to cancel the changes.

## Rectangle Color Picker
Left click to pin one "corner" of the rectangle.  Afterwards, right click to pin the opposite "corner" of the rectangle (you can go in any direction).  After pinning these corners, the operator will extract the rectangle's max, min, mean, and median.  Press escape (or right click if you haven't left clicked yet) to cancel.

**Note**: these values are gamma corrected, so they reflect the values you see on the screen, *not* the true values in Blender before the colorspace conversion.
