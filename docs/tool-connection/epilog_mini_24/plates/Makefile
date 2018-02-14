OPENSCAD:=/usr/bin/openscad

# Depends on both libs as a hack
%.svg: %.scad one_box_mount_lib.scad two_box_mount_lib.scad
	"$(OPENSCAD)" -o "$@" "$<"
	sed -i.bak 's/svg width="\([^"]*\)" height="\([^"]*\)"/svg width="\1mm" height="\2mm"/' $@

%_demo.png: %_demo.scad %_lib.scad
	"$(OPENSCAD)" -o "$@" --imgsize=2048,2048 --camera=0,-25,95,60,0,54,1300 "$<"
	convert "$@" -transparent '#ffffe5' -trim +repage "$@"

.PHONY: all
all: two_box_mount_inner.svg two_box_mount_outer.svg one_box_mount_inner.svg one_box_mount_outer.svg one_box_mount_hole_template.svg one_box_mount_demo.png two_box_mount_demo.png