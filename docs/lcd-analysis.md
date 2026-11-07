# Aftermarket LCD investigation

The replacement LCD working in Android implies there is an initialization path,
but does not identify its controller. A compatible original-panel protocol, altered
firmware/driver, bridge/converter or different controller are all unresolved.
Touch working does not prove it shares the panel's controller or power sequencing.

The inspected Linux reference has `panel-l2-38-0c-0a-dsc.c` with DSI command writes,
DSC setup, GPIO reset and regulator dependencies. Its DTS describes original
1440x3200 panel/touch data from another device. It explicitly leaves supply rails
unverified and has attribution FIXME markers. None of those timings, commands or
GPIO numbers has been copied into our target.

The read-only collector first gathers reported modes, available panel-compatible
strings/node names, display-driver binding names, touch axis ranges/controller
candidates, backlight numeric metadata, selected firmware properties and bounded
display-log keyword counts. It reports inaccessible paths rather than requesting root.
It deliberately does not publish full kernel logs or `dumpsys` output because
they can contain unrelated private data. Full DSI timings/DSC PPS and reset/power
dependencies require matching the active DT/DTBO and exact firmware source later.

`drivers/display` accepts a caller-provided mapping and validates stride, capacity,
coordinates and overflow before RGBX/BGRX writes. It cannot establish that a physical
address is mapped, writable or being scanned by the panel. Power, brightness, mode,
suspend and resume operations return UNSUPPORTED until a backend exists. Tests use
allocated host RAM. The touch module validates contact bounds and down/move/up
transitions; it does not pretend to be an SPI/I2C driver.

First visual hardware milestone, after separate authorization, should use a
verified retained framebuffer. Cache maintenance, scanout ownership and firmware
shutdown behavior must be established before relying on it across kernel handoff.
An XNU display driver then needs IOKit/user-client/IOSurface integration in addition
to panel transport; a Linux DRM driver cannot be linked unchanged into XNU.
