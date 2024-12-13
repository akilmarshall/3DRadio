include <parameters.scad>
ES_THICK = 5;
ES_Y = D / 3;
ES_Z = L / 2;
module elevation_structure_surface() {
    color("darkcyan")
    translate([0, -ES_Y/2, 0])
    union() {
        translate([D / 2, 0, 0])
        cube([ES_THICK, ES_Y, ES_Z]);
        translate([-ES_THICK- (D / 2), 0, 0])
        cube([ES_THICK, ES_Y, ES_Z]);
    }
}

EM_Y = D / 4;
EM_THICK = 5;
EM_CUT_STOP_DEPTH = 2;
EM_DIST_FROM_BASE = 30;
EM_HOLE_R = 3;
EM_SMALL_HOLE_R = 1;
EM_SMALL_HOLE_OFFSET = 6;

module elevation_mount() {
    /* Y = D/4; */
    /* thickness = 5; */
    /* cut_stop_depth = 2; // leave how much */
    /* distance_from_base = 30; */
    /* hole_radius = 3; */
    /* small_hole_radius = 1; */
    /* small_hole_offset = 6; // distance from center */
    module arms() {
        Z = 0.01 + L /2;
        color("coral")
        translate([0, -EM_Y/2, -EM_DIST_FROM_BASE])
        union() {
            translate([(D / 2) + EM_CUT_STOP_DEPTH, 0, 0])
            cube([EM_THICK, EM_Y, Z + EM_DIST_FROM_BASE - 0.02]);
            translate([-EM_THICK- (D / 2) - EM_CUT_STOP_DEPTH, 0, 0])
            cube([EM_THICK, EM_Y, Z + EM_DIST_FROM_BASE - 0.02]);
        }
    }
    module bottom() {
        color("coral")
        translate([-D/2-EM_CUT_STOP_DEPTH, -EM_Y/2, -0])
        union() {
            translate([0, 0, -EM_THICK- 0.02])
            cube([2 * EM_CUT_STOP_DEPTH + D, EM_Y, EM_THICK]);
            translate([0, 0, -EM_DIST_FROM_BASE])
            cube([2 * EM_CUT_STOP_DEPTH + D, EM_Y, EM_THICK]);
        }
    }
    module hole() {
        X = D + EM_CUT_STOP_DEPTH + (4 * EM_THICK);
        t_x = -X/2;
        t_y = 0;
        t_z = -EM_DIST_FROM_BASE / 2;
        color("aquamarine")
        translate([t_x, t_y, t_z])
        rotate([0, 90, 0])
        cylinder(h=X, r=EM_HOLE_R);

        color("aquamarine")
        translate([t_x, t_y + EM_SMALL_HOLE_OFFSET, t_z])
        rotate([0, 90, 0])
        cylinder(h=X, r=EM_SMALL_HOLE_R);

        color("aquamarine")
        translate([t_x, t_y - EM_SMALL_HOLE_OFFSET, t_z])
        rotate([0, 90, 0])
        cylinder(h=X, r=EM_SMALL_HOLE_R);

        color("aquamarine")
        translate([t_x, t_y, t_z - EM_SMALL_HOLE_OFFSET])
        rotate([0, 90, 0])
        cylinder(h=X, r=EM_SMALL_HOLE_R);

        color("aquamarine")
        translate([t_x, t_y, t_z + EM_SMALL_HOLE_OFFSET])
        rotate([0, 90, 0])
        cylinder(h=X, r=EM_SMALL_HOLE_R);
    }
    difference() {
        union() {
            arms();
            bottom();
        }
        hole();
    }
}
