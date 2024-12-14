include <BOSL2/std.scad>
include <BOSL2/gears.scad>

include <lazy_susan.scad>


module keyed_hole(height, print_slack) {
    hole_diameter = 5 + print_slack;
    hole_radius = hole_diameter / 2;
    key_depth = 0.5;

    down(height / 2)
    difference() {
        cylinder(height, d=hole_diameter);

        color("purple")
        up(height/2)
        right(hole_diameter-key_depth)
        cube([hole_diameter, hole_diameter, height + 0.02], center=true);
    }
}

AZ_DRIVE_GEAR_DIAMETER = 24;
AZ_DRIVE_GEAR_TEETH = 29;
AZ_DRIVE_GEAR_THICKNESS = 8;
AZ_DRIVE_GEAR_PITCH_RADIUS = pitch_radius(mod=AZ_DRIVE_GEAR_DIAMETER/AZ_DRIVE_GEAR_TEETH, teeth=AZ_DRIVE_GEAR_TEETH);
module azimuth_drive_gear() {
    let (mod = AZ_DRIVE_GEAR_DIAMETER / AZ_DRIVE_GEAR_TEETH) {
        difference() {
            spur_gear(teeth=AZ_DRIVE_GEAR_TEETH, thickness=AZ_DRIVE_GEAR_THICKNESS, mod=mod);
            keyed_hole(height=10, print_slack=0.1);
        }
    }
}

AZ_GEAR_THICKNESS = 8;
AZ_GEAR_DIAMETER = 120;
AZ_GEAR_TEETH = 149;
AZ_GEAR_PITCH_RADIUS = pitch_radius(mod=AZ_GEAR_DIAMETER / AZ_GEAR_TEETH, teeth=AZ_GEAR_TEETH);
AZ_GEAR_MOUNT_HOLE_DIAM = 5.5;
module azimuth_gear() {
    let (mod = AZ_GEAR_DIAMETER / AZ_GEAR_TEETH) {
        difference() {
            // azimuth gear object
            color("linen")
            spur_gear(mod=mod, teeth=AZ_GEAR_TEETH, thickness=AZ_GEAR_THICKNESS);

            // mount holes
            color("steelblue")
            for (i = [0, 90, 180, 270]) {
                zrot(i)
                right(LS_MOUNT_DIAM_2 / 2)
                cylinder(0.2 + AZ_GEAR_THICKNESS, d=AZ_GEAR_MOUNT_HOLE_DIAM, center=true);
            }

            // center cavity
            color("steelblue")
            cylinder(0.2 + AZ_GEAR_THICKNESS, d=LS_DIAM_2, center=true);
        }
    }
}
