box_hole_locations=[
  [30,107],
  [80,107],
  [130,107],
  [217,107],

  [30,255],
  [80,255],
  [130,294],
  [217,294],
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
  translate([20,80,120]) GhostBox([70,180,50]);
  translate([115,90,120]) GhostBox([100,200,50]);
}

module Inner() {
  Plate(cap_size=25,$fn=128);
}

module Outer() {
  Plate(cap_size=4.2,$fn=128);
}
