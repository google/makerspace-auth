include <one_box_mount_lib.scad>

Inner();
translate([plate_width*2+3,plate_height]) rotate([0,0,180]) Outer();
