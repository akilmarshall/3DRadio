$fn = 120;
include <elevation.scad>


part = "";

if (part == "") {
    echo("define the part to be generated with <part>");
} else if (part == "elevation mount") {
    elevation_mount();
} else if (part == "elevation standoff") {
    elevation_structure_standoff();
} else if (part == "elevation base") {
    elevation_structure_base();
}
