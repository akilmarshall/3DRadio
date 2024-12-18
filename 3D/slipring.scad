include <BOSL2/std.scad>

include <lazy_susan.scad>


SR_THICKNESS = 6;
SR_DIAM_1 = 22.1;
SR_DIAM_2 = 35;
SR_DIAM_3 = 45;
SR_MOUNT_HOLE_DIAM = 5.5;
SR_ARM_WIDTH = 14;
SR_ARM_RADIUS = (SR_MOUNT_HOLE_DIAM + LS_MOUNT_DIAM_1) / 2;
SR_ARM_PADDING = 5;  // extra length on the arm after the hole
SR_CS_DIAM = 9;
SR_CS_DEPTH = 3;
SR_MAGNET_DIAM = 5.5;
SR_MAGNET_HEIGHT = 2.5;
module slipring_mount() {
    module cylindrical_body() {
        cylinder(SR_THICKNESS, d=SR_DIAM_3, center=true);
    }

    module arms() {
            for(i = [0, 90, 180, 270]) {
                zrot(i)
                right(SR_ARM_RADIUS / 2)
                cube([SR_ARM_RADIUS + SR_ARM_PADDING, SR_ARM_WIDTH, SR_THICKNESS], center=true);
            }
    }

    module center_cavity() {
        cylinder(0.2 + SR_THICKNESS, d=SR_DIAM_1, center=true);
    }

    module slipring_mount_holes() {
        for(i = [0, 120, 240]) {
            zrot(i)
            right(SR_DIAM_2 / 2)
            cylinder(0.2 + SR_THICKNESS, d=SR_MOUNT_HOLE_DIAM, center=true);
        }
    }

    module static_base_mount_holes() {
        for (i=[0, 90, 180, 270]) {
            zrot(i)
            right(LS_MOUNT_DIAM_1 / 2)
            cylinder(0.02 + SR_THICKNESS, d= SR_MOUNT_HOLE_DIAM, center=true);
        }
    }

    module static_base_mount_cs() {
        for (i = [0, 90, 180, 270]) {
            up(SR_THICKNESS / 2)
            down(SR_CS_DEPTH)
            zrot(i)
            right(LS_MOUNT_DIAM_1 / 2)
            cylinder(0.1 + SR_CS_DEPTH, d=SR_CS_DIAM, center=false);
        }
    }

    difference() {
        color("linen")
        union() {
            // primary body
            cylindrical_body();

            // arms
            arms();
        }

        // center cavity
        color("steelblue")
        center_cavity();

        // holes for attaching slipring to the mount
        color("steelblue")
        slipring_mount_holes();

        // holes for attaching slipring to static base
        color("steelblue")
        static_base_mount_holes();

        // countersink for static base mount holes
        color("steelblue")
        static_base_mount_cs();

        // slot for magnet
        color("steelblue")
        fwd(SR_ARM_WIDTH/2)
        left(2 + SR_MAGNET_HEIGHT / 2)
        right(LS_DIAM_2/2)
        yrot(90)
        cylinder(SR_MAGNET_HEIGHT, d=SR_MAGNET_DIAM, center=true);
    }

}
