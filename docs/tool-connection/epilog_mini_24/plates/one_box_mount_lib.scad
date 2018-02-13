box_center = [120,160];
box_size = [188,192];


// Non-square pattern intentional; avoid colliding with pi bracket and reduce
// number of possible wrong orientations by half.
box_hole_pattern = [
  [70, 60],
  [70, -60],
  [-70, 60],
  [-70, -60],
];

box_hole_locations=[
  for (p = box_hole_pattern) box_center + p
];

frame_hole_locations=[
  [20,20],
  [62,305],
];

plate_width=235;
plate_height=325;

module Plate(cap_size) {
  difference() {
    square([plate_width, plate_height]);
    translate([0,plate_height-30]) rotate(atan2(30, 40)) square([100,100]);
    for(p = box_hole_locations)
      translate(p) circle(d=cap_size);
    for(p = frame_hole_locations)
      translate(p) circle(d=4.5);
  }
}

module Main() {
  Plate(cap_size=25,$fn=128);
  translate([plate_width+4,0])
    Plate(cap_size=4.2,$fn=128);
}

module CapHead(d,h) {
  color([0.8,0.5,0.5]) {
    translate([0,0,-h]) cylinder(d=d,h=h);
    cylinder(d=d*1.5,h=d);
  }
}

module Leader(h) {
  color([0.5,0.5,0.5,0.3]) cylinder(d=1,h=h);
}

module GhostBox(dims) {
  color([0.5,0.5,0.5,0.3]) cube(dims);
}

module Exploded() {
  linear_extrude(height=6) Inner();
  translate([0,0,80]) linear_extrude(height=6) Outer();
  for(p = box_hole_locations) {
    translate(p) {
      translate([0,0,-60]) scale([1,1,-1]) CapHead(4,20,$fn=32);
      translate([0,0,-40]) Leader(160);
    }
  }
  for(p = frame_hole_locations) {
    translate(p) {
      translate([0,0,130]) CapHead(4,20,$fn=32);
      translate([0,0,-20]) Leader(130);
    }
  }
  translate([box_center[0],box_center[1],120]) translate([-100,-100]) GhostBox([box_size[0],box_size[1],90]);
}

module ZiptieMount() {
  for(x=[200,210]) translate([x,30]) square([3,6.5], center=true);
}

module Inner() {
  difference() {
    Plate(cap_size=25,$fn=128);
    hull() ZiptieMount();
  }
}

module Outer() {
  difference() {
    Plate(cap_size=4.2,$fn=128);
    ZiptieMount();
  }
}

module HoleTemplate() {
  $fn=32;
  difference() {
    square(box_size, center=true);
    for(p = box_hole_pattern) {
      translate(p) circle(d=3);
    }
    translate([0,60]) text("4x 4.2mm", halign="center", size=5);
    translate([80,40]) text("Badge reader (17mm) ->", halign="right", size=5);
    translate([0,10]) text("(place on back of box)", halign="center", size=8);
    translate([0,-10]) text("(verify 5 holes at bottom)", halign="center", size=8);
    translate([-80,-40]) text("<- Power (8mm), actuators (??mm)", halign="left", size=5);
    translate([-80,-50]) text("<- Ethernet (U notch)", halign="left", size=5);
  }
}
