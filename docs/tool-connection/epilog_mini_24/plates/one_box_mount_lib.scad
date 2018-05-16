box_center = [120,160];
box_size = [192,188];
box_front_size = [100,188];

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
  [20,7.5],
  [62,292.5],
];

plate_width=235;
plate_height=300;

arcade_button_hole_size=24;
arcade_button_pos = [18+27,15+42];
badge_reader_hole_size=17;

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

module Slot(d, dist) {
  hull() for(y=[dist/2,-dist/2]) translate([0,y]) circle(d=d);
}

module ZiptieMount() {
  for(x=[200,210]) translate([x,30]) Slot(3, 7, $fn=16);
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
    translate([-90,0]) text("A", halign="left", size=5);
    translate([90,0]) text("B", halign="right", size=5);
    translate([0,60]) text("4x 4.2mm", halign="center", size=5);
    translate([80,40]) text("Front ->", halign="right", size=5);
    translate([-80,40]) text("<- Back", halign="left", size=5);
    translate([0,10]) text("(place on back of box)", halign="center", size=8);
    translate([0,-10]) text("(verify interior 5 holes at sides)", halign="center", size=8);
  }
}

module CrosshairCircle(d) {
  difference() {
    circle(d=d);
    square([1,d*0.7], center=true);
    square([d*0.7, 1], center=true);
  }
}

module LidHoleTemplate() {
  $fn=32;
  difference() {
    square(box_size, center=true);
    translate([-box_size[0]/2+3,0]) text("C", halign="left", size=5);
    translate([box_size[0]/2-3,0]) text("D", halign="right", size=5);
    for(y_scale=[1,-1])
      scale([1,y_scale])
        translate([-box_size[0]/2+arcade_button_pos[0],
                   -box_size[1]/2+arcade_button_pos[1]])
          CrosshairCircle(arcade_button_hole_size);
  }
}

module FrontHoleTemplate() {
  $fn=32;
  difference() {
    square(box_front_size, center=true);
    translate([box_front_size[0]/2-20, 0]) square([1,box_front_size[1]-2], center=true);
    text("Front", halign="center", size=5);
    translate([-box_front_size[0]/2+3,0]) text("B", halign="left", size=5);
    translate([box_front_size[0]/2-3,0]) text("C", halign="right", size=5);
    translate([0,60]) CrosshairCircle(badge_reader_hole_size);
  }
}

module BackHoleTemplate() {
  $fn=32;
  difference() {
    square(box_front_size, center=true);
    translate([-box_front_size[0]/2+20, 0]) square([1,box_front_size[1]-2], center=true);
    text("Back", halign="center", size=5);
    translate([box_front_size[0]/2-3,0]) text("A", halign="right", size=5);
    translate([-box_front_size[0]/2+3,0]) text("D", halign="left", size=5);
    translate([box_front_size[0]/2-35,box_front_size[1]/2-35])
      CrosshairCircle(8);  // power
    translate([box_front_size[0]/2-50,box_front_size[1]/2-35])
      CrosshairCircle(8);  // actuator cables
    translate([box_front_size[0]/2-80+4,box_front_size[1]/2-35])
      CrosshairCircle(8);  // actuator cables
  }
}
