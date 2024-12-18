include <BOSL2/std.scad>
include <BOSL2/nema_steppers.scad>

include <lazy_susan.scad>
include <gears.scad>


SB_DIAM = 100;
SB_WIRE_PORT_DIAM = 25;
SB_MOUNT_HOLE_DEPTH = 101;
SB_MOUNT_HOLE_DIAM = 5.0; // M5 mount diameter is usually 5.5,
                          // however I would like the bolt to "self thread", thus d=5.0
SB_MOTOR_SIZE = 17;
SB_MOTOR_HEIGHT = 40;
SB_MOTOR_SLOT = 4;
SB_MOTOR_INFO = nema_motor_info(SB_MOTOR_SIZE);
SB_MOTOR_WIDTH = SB_MOTOR_INFO[0];
SB_MOTOR_MOUNT_THICK = 5;
SB_HEIGHT = SB_MOTOR_HEIGHT + SB_MOTOR_MOUNT_THICK;
module static_base() {
    gear_radius = AZ_DRIVE_GEAR_PITCH_RADIUS + AZ_GEAR_PITCH_RADIUS;

    module cylindrical_body() {
        cylinder(SB_HEIGHT, d=SB_DIAM, center=true);
    }

    module motor_mount_plate() {
        up(SB_HEIGHT / 2)
        down(SB_MOTOR_MOUNT_THICK / 2)
        right(0.95 * gear_radius)
        cube([1.2 * SB_MOTOR_WIDTH, 1.0 * SB_MOTOR_WIDTH, SB_MOTOR_MOUNT_THICK], center=true);
    }

    module center_cavity() {
        cylinder(SB_HEIGHT + 0.2, d=LS_DIAM_1, center=true);
    }

    module wire_port() {
        down(SB_HEIGHT / 2)
        zrot(45)
        xrot(90)
        cylinder(1.1 * SB_DIAM/2, d=SB_WIRE_PORT_DIAM, center=false);
    }

    module holes() {
        for (i = [0, 90, 180, 270]) {
            zrot(i)
            right(LS_MOUNT_DIAM_1 / 2)
            up(0.02 + (SB_MOUNT_HOLE_DEPTH + SB_HEIGHT)/2)
            down(SB_MOUNT_HOLE_DEPTH)
            cylinder(SB_MOUNT_HOLE_DEPTH, d=SB_MOUNT_HOLE_DIAM, center=true);
        }
    }

    module motor_mask() {
        up((SB_MOTOR_HEIGHT) / 2)
        right(gear_radius)
        zrot(90)
        nema_mount_mask(SB_MOTOR_SIZE, l=SB_MOTOR_SLOT, depth=0.2 + SB_MOTOR_MOUNT_THICK);
    }

    // sum the cylindrical_body and motor_mount_plate plate
    // then subtract center_cavity, wire_port, holes, and motor_mask
    difference() {
        color("linen")
        union() {
            cylindrical_body();
            motor_mount_plate();
        }
        color("steelblue")
        union() {
            center_cavity();
            wire_port();
            holes();
            motor_mask();
        }
    }
}
