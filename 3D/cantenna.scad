// httpsp//3g-aerial.biz/en/online-calculations/antenna-calculations/cantenna-online-calculator
// Can diameter = 150
// Working frequency = 1420 MHz
include <parameters.scad>
include <elevation.scad>
include <azimuth.scad>

// how will the inside of the can be made conductive?

ANT_WALL_THICK = 5;
ANT_BASE_THICK = 7;
ANT_SIDE_HOLE_R = 1;


module antenna() {
    color("grey")
    translate([0, -ANT_WALL_THICK -D / 2, ANT_WALL_THICK + d])
    rotate([90, 0, 90 + 90])
    cylinder(h=h + (2 * ANT_WALL_THICK) + 0.01, r=ANT_SIDE_HOLE_R);
}

module wave_guide() {
    difference() {
        color("orange")
        cylinder(h=L+ANT_BASE_THICK, d=D+ANT_WALL_THICK);
        color("cyan")
        translate([0, 0, ANT_BASE_THICK])
        cylinder(h=L*1.2, d=D);
    }
}

module horn() {
    translate([0, 0, L])
    difference() {
        /* cylinder(h=h, r1=R1, r2=R2); */
        difference() {
            cylinder(h=d, r1=R1+ANT_WALL_THICK, r2=R2+ANT_WALL_THICK);
            translate([0, 0, ANT_WALL_THICK])
            cylinder(h=d, r1=R1, r2=R2);
        }

        /* W = 5; */
        color("blue")
        /* translate([0, 0, -W]) */
        /* /1* rotate([0, 0, 180]) *1/ */
        translate([0, 0, -0.01])
        cylinder(h=d, r=R1);
    }
}

PANEL_X = 25;
PANEL_Y = 2;
PANEL_Z = 25;
module panel(mode="show") {
    //panel for the port that the antenna is mounted to inside of the waveguide (can)
    // https://i.ebayimg.com/images/g/1ycAAOSwEDdjGA7z/s-l1600.webp
    t_X = -PANEL_X / 2;
    t_Y = -ANT_WALL_THICK / 2 - D / 2;
    t_Z = ANT_WALL_THICK + d - (PANEL_Z / 2);

    module base() {
        color("purple")
        translate([t_X, t_Y, t_Z])
        union() {
            cube([PANEL_X, PANEL_Y, PANEL_Z]);
            translate([-t_X, 6 + 2, PANEL_Z/2])
            rotate([90, 0, 0])
            cylinder(h=6.02, d=13.3);
        }
    }


    module holes() {
        corner = 3;
        length = 18;
        translate([t_X, t_Y, t_Z])
        union() {
        color("green")
        translate([corner , 6 + 2, corner])
        rotate([90, 0, 0])
        cylinder(h=2 * 6, d=3.5);

        color("green")
        translate([corner + length , 6 + 2, corner])
        rotate([90, 0, 0])
        cylinder(h=2 * 6, d=3.5);

        color("green")
        translate([corner + length , 6 + 2, corner + length])
        rotate([90, 0, 0])
        cylinder(h=2 * 6, d=3.5);

        color("green")
        translate([corner, 6 + 2, corner + length])
        rotate([90, 0, 0])
        cylinder(h=2 * 6, d=3.5);
        }
    }
    if (mode == "show") {
        difference() {
        base();
        holes();
        }
    } else {
        base();
        holes();
    }
}

module cantenna() {
    difference() {
        union() {
            wave_guide();
            elevation_structure_surface();
        }
        antenna();
        elevation_mount();
        panel(mode="cut");
    }
}

module elevation_structure() {
    difference() {
        elevation_mount();
        elevation_structure_surface();
    }
}

module cantenna_render() {
    azimuth_render();
    /*
    up(EM_DIST_FROM_BASE + SB_HEIGHT + LS_THICK + DG_THICKNESS + 3) {
        wave_guide();
        antenna();
        panel();
        elevation_structure_surface();
        elevation_mount();
    }
    */
}
