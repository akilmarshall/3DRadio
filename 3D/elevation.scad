include <BOSL2/std.scad>
include <parameters.scad>
include <lazy_susan.scad>


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

ES_STANDOFF_HEIGHT = 20;
ES_STANDOFF_DIAM = 8;
ES_STANDOFF_HOLE_DIAM = 5;
module elevation_structure_standoff() {
    for (i = [0, 90, 180, 270]) {
        zrot(i)
        right(LS_MOUNT_DIAM_2 / 2)
        difference() {
            color("linen")
            cylinder(h=ES_STANDOFF_HEIGHT, d=ES_STANDOFF_DIAM, center=true);
            color("steelblue")
            cylinder(h=ES_STANDOFF_HEIGHT + 2, d = ES_STANDOFF_HOLE_DIAM, center=true);
        }
    }
}

ES_BASE_THICK = 5;
ES_BASE_EXTRA = 10;
ES_BASE_DIAM = LS_DIAM_3 + ES_BASE_EXTRA;
ES_BASE_CENTER_HOLE_DIAM = 32; 
ES_BASE_MOUNT_HOLE_DIAM = 5.5;
RPI_MOUNT_X = 58;
RPI_MOUNT_Y = 39;
RPI_MOUNT_HOLE_DIAM = 2.75;
RPI_MOUNT_STANDOFF_DIAM = 6;
RPI_MOUNT_STANDOFF_HEIGHT = 3;
COMPASS_MOUNT_X = 20;
COMPASS_MOUNT_Y = 10;
COMPASS_MOUNT_HOLE_DIAM = 2.75;
COMPASS_MOUNT_STANDOFF_DIAM = 6;
COMPASS_MOUNT_STANDOFF_HEIGHT = 3;
module elevation_structure_base() {
    module rpi_mount() {
        x = RPI_MOUNT_X / 2;
        y = RPI_MOUNT_Y / 2;
        up((ES_THICK + RPI_MOUNT_STANDOFF_HEIGHT) / 2) {
            for (i = [[1, 1], [-1, 1], [-1, -1], [1, -1]]) {
                right(i.x * x)
                fwd(i.y * y)
                difference() {
                    color("linen")
                    cylinder(h=RPI_MOUNT_STANDOFF_HEIGHT, d=RPI_MOUNT_STANDOFF_DIAM, center=true);
                    color("steelblue")
                    cylinder(h=RPI_MOUNT_STANDOFF_HEIGHT+2, d=RPI_MOUNT_HOLE_DIAM, center=true);
                }
            }
        }
    }
    module compass_mount() {
        x = COMPASS_MOUNT_X / 2;
        y = COMPASS_MOUNT_Y / 2;
        up((ES_THICK + COMPASS_MOUNT_STANDOFF_HEIGHT) / 2) {
            for (i = [[1, 1], [-1, 1], [-1, -1], [1, -1]]) {
                right(i.x * x)
                fwd(i.y * y)
                difference() {
                    color("linen")
                    cylinder(h=COMPASS_MOUNT_STANDOFF_HEIGHT, d=COMPASS_MOUNT_STANDOFF_DIAM, center=true);
                    color("steelblue")
                    cylinder(h=COMPASS_MOUNT_STANDOFF_HEIGHT+2, d=COMPASS_MOUNT_HOLE_DIAM, center=true);
                }
            }
        }
    }

    difference() {
        color("linen")
        cylinder(h=ES_BASE_THICK, d=ES_BASE_DIAM, center=true);
        color("steelblue")
        cylinder(h=ES_BASE_THICK + 2, d=ES_BASE_CENTER_HOLE_DIAM, center=true);
        for (i = [0, 90, 180, 270]) {
            color("steelblue")
            zrot(i)
            right(LS_MOUNT_DIAM_2 / 2)
            cylinder(h=ES_BASE_THICK + 2, d=ES_BASE_MOUNT_HOLE_DIAM, center=true);
        }
    }
    zrot(-45)
    right((RPI_MOUNT_X) / 2)
    rpi_mount();

    zrot(90)
    right(3.75 * COMPASS_MOUNT_Y)
    compass_mount();
}
