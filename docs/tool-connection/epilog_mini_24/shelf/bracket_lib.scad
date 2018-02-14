Thickness = 5;
BaseHeight = 11;
Height = 58;
ToAngle = 18;
AngleHeight = 2;
AfterAngle = 3;
InnerRadius = 0.5;

HolePositions = [
  [3,-10],
  [3,-35],
  [3,-75],
];

module SideProfile() {
  difference() {
    union() {
      translate([-Thickness,0]) square([Thickness+1, BaseHeight+Height]);
      translate([-0.01,0]) square([ToAngle+AngleHeight+AfterAngle, BaseHeight+AngleHeight]);
    }
    hull() {
      for(yo=[InnerRadius, InnerRadius+Height])
        translate([InnerRadius, BaseHeight+yo]) circle(r=InnerRadius, $fn=32);
      translate([ToAngle-1,BaseHeight]) square([1,1]);
      translate([ToAngle+AngleHeight-1, BaseHeight+AngleHeight]) square([1,1]);
    }
  }
}

module CountersunkHole() {
  // bottom
  difference() {
    translate([0,0,-1]) cylinder(d=8,h=7.4,$fn=128);
    translate([3,0,5+6]) cube([3,10,10], center=true);
    translate([-3,0,5+6]) cube([3,10,10], center=true);
  }
  // middle
  cylinder(d=3,h=100,$fn=32);
  // top
  translate([0,0,BaseHeight-3]) cylinder(d=6,h=10,$fn=128);
}

module CountersunkHoles() {
  for(p=HolePositions) {
    translate(p) CountersunkHole();
  }
}

module Tab() {
  rotate([90,0,0]) linear_extrude(height=4.5) polygon(points=[[0,0], [10,0], [10,5], [5,5]]);
}

module NegativeFillet(r) {
  linear_extrude(height=100,convexity=4)
  difference() {
    translate([-1,-1]) square([r+1,r+1]);
    translate([r,r]) circle(r=r,$fn=32);
  }
}

module Clip() {
  difference() {
    linear_extrude(height=6) offset(r=1,$fn=32) offset(delta=-1) square([13,7.5]);
    hull() {
      translate([-3.8,-0.25,3]) cube([13,10,6]);
      translate([-0.8,-0.25,6.01]) cube([13,10,6]);
    }
    translate([3,7.5/2,-1]) cylinder(d=3.2,h=10,$fn=32);
    translate([3,7.5/2,-2]) cylinder(d=6.2,h=3,$fn=32);
  }
}

module Main() {
  difference() {
    rotate([90,0,0]) linear_extrude(height=86, convexity=4) SideProfile();
    CountersunkHoles();
    translate([-Thickness/2,-61,BaseHeight+Height-12]) cylinder(d=2.7,h=13,$fn=32);
    // Base fillets
    translate([ToAngle+AngleHeight+AfterAngle,-86,-1]) rotate([0,0,90]) NegativeFillet(2);
    translate([ToAngle+AngleHeight+AfterAngle,0,-1]) rotate([0,0,180]) NegativeFillet(2);
    // Top fillets
    translate([-50,-86,BaseHeight+Height]) rotate([0,90,0]) NegativeFillet(2);
    translate([-50,0,BaseHeight+Height]) rotate([-90,0,0]) rotate([0,90,0]) NegativeFillet(2);
  }
  translate([5,0,BaseHeight-0.01]) Tab();
  translate([5,-61.5,BaseHeight-0.01]) Tab();
}

module MainClip() {
  translate([0,-95,0]) Clip();
}
