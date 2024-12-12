include <BOSL2/std.scad>
include <BOSL2/gears.scad>
include <BOSL2/nema_steppers.scad>

module base_holes(diameter, length, height) {
    half = length / 2;
    down(height / 2) {
        right(half)
        cylinder(height, d=diameter, center=true);
        back(half)
        cylinder(height, d=diameter, center=true);
        left(half)
        cylinder(height, d=diameter, center=true);
        fwd(half)
        cylinder(height, d=diameter, center=true);
    }
}

module keyed_hole(height=10, print_slack=0) {
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

DG_DIAMETER = 24;
DG_TEETH = 29;
DG_THICKNESS = 5;
DG_PITCH_RADIUS = pitch_radius(mod=DG_DIAMETER/DG_TEETH, teeth=DG_TEETH);
module drive_gear(diameter=DG_DIAMETER, teeth=DG_TEETH, thickness=DG_THICKNESS) {
    difference() {
        mod = diameter / teeth;
        spur_gear(teeth=teeth, thickness=thickness, mod=mod);
        keyed_hole(print_slack=0.1);
    }
}

SB_HEIGHT = 50;
SB_BASE_DIAM = 100;
SB_CS_RADIUS = 16;
SB_CS_DEPTH = 10;
SB_WIRE_PORT_D = 25;
SB_MOUNT_HOLE_DEPTH = 10;
AZ_MOTOR_SIZE = 17;
AZ_MOTOR_MASK_DEPTH = 7;
AZ_MOTOR_SHAFT_LEN = 25;
AZ_MOTOR_SLOT = 4;
AZ_MOTOR_INFO = nema_motor_info(AZ_MOTOR_SIZE);
AZ_MOTOR_WIDTH = AZ_MOTOR_INFO[0];
AZ_MOTOR_HEIGHT = 40;
AZ_MOTOR_MOUNT_WIDTH = 43;
AZ_MOTOR_MOUNT_DEPTH = 50;
AZ_MOTOR_MOUNT_THICK = 5;
module static_base(height=SB_HEIGHT, hole_diameter=LS_MOUNT_HOLE_D, mount_hole_diam=LS_MOUNT_DIAM_1, base_diameter=SB_BASE_DIAM, center_diameter=LS_DIAM_1, cs_radius=SB_CS_RADIUS, cs_depth=SB_CS_DEPTH) {
    half = mount_hole_diam / 2;

    difference() {
        cylinder(height, d=base_diameter, center=true);

        color("red")
        up(0.02 + height/2)
        base_holes(hole_diameter, mount_hole_diam, SB_MOUNT_HOLE_DEPTH);

        color("purple")
        up(SB_CS_DEPTH + 10)
        base_holes(cs_radius, mount_hole_diam, (1 * cs_depth));

        color("blue")
        cylinder(2 * height, d=center_diameter, center=true);

        down(SB_HEIGHT / 2)
        color("pink") {
            /* fwd(LS_DIAM_1/2) */
            /* down((SB_BASE_DIAM - LS_DIAM_1)/2) */
            /* fwd(LS_DIAM_1/2) */
            xrot(90)
            cylinder(2 * (SB_BASE_DIAM - LS_DIAM_1), d=SB_WIRE_PORT_D, center=false);
        }
    }
    down(5) // idk where this height is coming from...
    up(AZ_MOTOR_HEIGHT/2) {
    right(DG_PITCH_RADIUS + AG_PITCH_RADIUS) {
        difference() {
            left((LS_DIAM_3 - LS_DIAM_2) / 8)
            cube([AZ_MOTOR_MOUNT_DEPTH, AZ_MOTOR_MOUNT_WIDTH, AZ_MOTOR_MOUNT_THICK], center=true);
            zrot(90)
            nema_mount_mask(AZ_MOTOR_SIZE, l=AZ_MOTOR_SLOT, depth=AZ_MOTOR_MASK_DEPTH);
        }
        color("green") {
            up(AZ_MOTOR_MOUNT_THICK / 2)
            left((LS_DIAM_3 - LS_DIAM_2) / 8 +AZ_MOTOR_MOUNT_DEPTH / 2)
            fwd(AZ_MOTOR_MOUNT_THICK + AZ_MOTOR_MOUNT_WIDTH / 2)
            xrot(-90)
            linear_extrude(AZ_MOTOR_MOUNT_THICK)
            right_triangle([AZ_MOTOR_MOUNT_DEPTH, AZ_MOTOR_HEIGHT]);
        }
        color("green") {
            up(AZ_MOTOR_MOUNT_THICK / 2)
            left((LS_DIAM_3 - LS_DIAM_2) / 8 +AZ_MOTOR_MOUNT_DEPTH / 2)
            back(AZ_MOTOR_MOUNT_WIDTH / 2)
            xrot(-90)
            linear_extrude(AZ_MOTOR_MOUNT_THICK)
            right_triangle([AZ_MOTOR_MOUNT_DEPTH, AZ_MOTOR_HEIGHT]);
        }
    }
    }
    //down(5) // idk where this height is coming from...
    //up(AZ_MOTOR_HEIGHT/2)
    //right(DG_PITCH_RADIUS + AG_PITCH_RADIUS)
    //nema_stepper_motor(size=AZ_MOTOR_SIZE, shaft_len=AZ_MOTOR_SHAFT_LEN, h=AZ_MOTOR_HEIGHT);
}

AG_HEIGHT = 5;
AG_DIAMETER = 120;
AG_HOLE_DIAMETER = 5.5;
AG_CENTER_DIAMETER = 95;
AG_HOLE_MOUNT_RADIUS = 108/2;
AG_TEETH = 149;
AG_PITCH_RADIUS = pitch_radius(mod=AG_DIAMETER / AG_TEETH, teeth=AG_TEETH);

module azimuth_gear(height=AG_HEIGHT, diameter=AG_DIAMETER, hole_diameter=AG_HOLE_DIAMETER, center_diameter=AG_CENTER_DIAMETER, hole_mount_radius=AG_HOLE_MOUNT_RADIUS) {
    mod = diameter / AG_TEETH;
    difference() {
        spur_gear(mod=mod, teeth=AG_TEETH, thickness=height);
        color("red")
        right(hole_mount_radius)
        cylinder(height * 2, d=hole_diameter, center=true);

        color("red")
        fwd(hole_mount_radius)
        cylinder(height * 2, d=hole_diameter, center=true);

        color("red")
        left(hole_mount_radius)
        cylinder(height * 2, d=hole_diameter, center=true);

        color("red")
        back(hole_mount_radius)
        cylinder(height * 2, d=hole_diameter, center=true);

        color("blue")
        cylinder(height*2, d=center_diameter, center=true);
    }
}

LS_DIAM_1 = 70;
LS_DIAM_2 = 95;
LS_DIAM_3 = 120;
LS_THICK = 8;
LS_MOUNT_DIAM_1 = 82;
LS_MOUNT_DIAM_2 = 108;
LS_MOUNT_HOLE_D = 5.5;
module lazy_susan(diam_1=LS_DIAM_1, diam_2=LS_DIAM_2, diam_3=LS_DIAM_3, mount_diam_1=LS_MOUNT_DIAM_1, mount_diam_2=LS_MOUNT_DIAM_2, thickness=LS_THICK) {

    difference() {
        union() {
            color("silver")
            cylinder(thickness, d=diam_2, center=true);
            color("grey")
            cylinder(thickness-0.02, d=diam_3, center=true);
        }

        color("blue")
        cylinder(thickness+0.02, d=diam_1, center=true);

        color("red") {
            right(mount_diam_1/2)
            cylinder(2 * thickness, d=LS_MOUNT_HOLE_D, center=true);
            left(mount_diam_1/2)
            cylinder(2 * thickness, d=LS_MOUNT_HOLE_D, center=true);
            fwd(mount_diam_1/2)
            cylinder(2 * thickness, d=LS_MOUNT_HOLE_D, center=true);
            back(mount_diam_1/2)
            cylinder(2 * thickness, d=LS_MOUNT_HOLE_D, center=true);
        }
        color("green") {
            right(mount_diam_2/2)
            cylinder(2 * thickness, d=LS_MOUNT_HOLE_D, center=true);
            left(mount_diam_2/2)
            cylinder(2 * thickness, d=LS_MOUNT_HOLE_D, center=true);
            fwd(mount_diam_2/2)
            cylinder(2 * thickness, d=LS_MOUNT_HOLE_D, center=true);
            back(mount_diam_2/2)
            cylinder(2 * thickness, d=LS_MOUNT_HOLE_D, center=true);
        }
    }
}

SR_THICK = 5;
SR_DIAM_1 = 22.1;
SR_DIAM_2 = 35;
SR_DIAM_3 = 45;
SR_MOUNT_DIAM = 5.5;
SR_ARM_WIDTH = 12;
SR_ARM_RADIUS = (LS_MOUNT_DIAM_1 / 2) - SR_DIAM_1 / 2;
SR_CS_DIAM = 9;
SR_CS_DEPTH = 3;
module slipring_mount() {
    difference() {
        union() {
            color("teal")
            cylinder(SR_THICK-0.01, d=SR_DIAM_3, center=true);
            color("grey") {
                for (i = [0, 90, 180, 270]) {
                    zrot(i)
                    fwd(1 + SR_ARM_RADIUS)
                    cube([SR_ARM_WIDTH, SR_ARM_RADIUS, SR_THICK - 0.02], center=true);
                }
            }
        }
        cylinder(SR_THICK, d=SR_DIAM_1, center=true);
        color("orange") {
            for (i = [0, 120, 240]) {
                zrot(i)
                right(SR_DIAM_2 / 2)
                cylinder(SR_THICK * 2, d=SR_MOUNT_DIAM, center=true);
            }
        }
        color("green")
        up(SR_THICK/2)
        base_holes(LS_MOUNT_HOLE_D, LS_MOUNT_DIAM_1, SR_THICK+0.02);

        color("purple")
        up(0.02 + SR_THICK/2)
        base_holes(SR_CS_DIAM, LS_MOUNT_DIAM_1, SR_CS_DEPTH);
    }
}

module azimuth_render() {
    sb_center = SB_HEIGHT / 2;
    ls_center = LS_THICK / 2;
    ag_center = AG_HEIGHT / 2;
    dg_center = DG_THICKNESS / 2;
    sr_center = SR_THICK / 2;

    up(sb_center) {
        static_base();
    }
    /*
    up(1 + SB_HEIGHT + ls_center) {
        lazy_susan();
    }
    up(1 + SB_HEIGHT + LS_THICK + sr_center) {
        slipring_mount();
    }
    up(2 + SB_HEIGHT + LS_THICK + dg_center) {
        right(DG_PITCH_RADIUS + AG_PITCH_RADIUS)
        drive_gear();
    }
    up(2 + SB_HEIGHT + LS_THICK + ag_center) {
        azimuth_gear();
    }
    */
}
