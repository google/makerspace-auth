OPENSCAD:=/usr/bin/openscad

# TODO: convert to binary for smaller size
%.stl: %.scad bracket_lib.scad
	"$(OPENSCAD)" -o "$@" "$<"

%.png: %.scad bracket_lib.scad
	"$(OPENSCAD)" -o "$@" --imgsize=2048,2048 --camera=-16,-32,18,62,0,45,325 "$<"
	convert "$@" -transparent '#ffffe5' -trim +repage "$@"

.PHONY: all
all: bracket_both.stl bracket_both.png bracket_main.stl bracket_clip.stl
