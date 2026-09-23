# Icon canvases and painted bounds

| Master | Safe area | Center | Home painted width |
| --- | --- | --- | --- |
| 24×24 | x/y = 2…22 (20×20) | 12,12 | 20 px regular folder |
| 32×32 | x/y = 2…30 (28×28) | 16,16 | 28 px regular folder |

All painted bounds, including strokes, must stay within the safe area. Preserve
proportions: artwork need not fill both dimensions. Center the painted bounds;
do not stretch a folder to fill the square. Scale strokes with the geometry.
These rules apply to new Places artwork; preserve external brand canvases and
existing application-requested status silhouettes.

The 24 px directory supports colorful regular artwork and monochrome symbolic
artwork. The symbolic Home master contains only a rounded house, within the
20×20 safe area, with an open doorway and no folder or gradients. The generic
symbolic folder uses the closed folder silhouette as a hollow rounded outline:
18.3 px path width plus a 1.7 px stroke, centered within the same safe area.

Use guides at 2, 12, 22 for 24 px artwork and 2, 16, 30 for 32 px artwork.
For a new stroked 24 px symbol, start with rounded 1.7 px strokes and gaps of at
least 1.5 px. Include stroke extents when measuring; no optical overshoot beyond
the safe area is permitted. Review optical weight and counters at display size.

Home's detailed folder uses a uniform scale of 28/24.46 around its painted
center (16,15.525) in the revised draft. Its bounds are (2,5.06214) through
(30,26.93786). The simplified 24 px folder uses 20/24.3 without the outer edge
stroke; its bounds are (2,4.20165) through (22,19.79835).

Run `task verify` and inspect both backgrounds at 16/22/24/32 px and 2×,
including selection, disabled opacity, doorway clarity and the 24-to-32 transition.
