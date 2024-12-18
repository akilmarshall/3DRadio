include <BOSL2/std.scad>
LS_DIAM_1 = 70;
LS_DIAM_2 = 95;
LS_DIAM_3 = 120;
LS_THICK = 8;
LS_MOUNT_DIAM_1 = 82;
LS_MOUNT_DIAM_2 = 108;
LS_MOUNT_HOLE_DIAM = 5.5;
module lazy_susan() {
    difference() {
        union() {
            color("silver")
            cylinder(LS_THICK, d=LS_DIAM_2, center=true);
            color("lightgray")
            cylinder(LS_THICK-0.02, d=LS_DIAM_3, center=true);
        }

        color("steelblue")
        cylinder(LS_THICK+0.02, d=LS_DIAM_1, center=true);

        color("steelblue")
        for (i = [0, 90, 180, 270]) {
            zrot(i) {
                right(LS_MOUNT_DIAM_1/2)
                cylinder(0.2 + LS_THICK, d=LS_MOUNT_HOLE_DIAM, center=true);

                right(LS_MOUNT_DIAM_2/2)
                cylinder(0.2 + LS_THICK, d=LS_MOUNT_HOLE_DIAM, center=true);
            }
        }
    }
}
