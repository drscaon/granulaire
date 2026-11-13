# Limits

Everything Granulaire does not do or has not verified, stated plainly.

Part of the [Granulaire](../README.md) documentation.

## Limits

- **Friction is per pair of surfaces.** What a robot foot feels also depends on
  the foot's own material and the engine's combine mode.
- **No capillary cohesion in simulation.** Wet-grain cohesion is stored in
  `granulaire:capillaryCohesion`, but OpenUSD has no standard schema for it and
  no rigid-body engine reads it: in simulation, wet grains differ only by
  friction, restitution and mass.
- **No rolling resistance.** Neither `UsdPhysics` nor PhysX rigid bodies model
  it, which is why piles of spheres flow far too easily. Here the irregular
  shapes play that role: an angular grain cannot roll. Rounded grains (river
  pebbles, beads, soybeans, pellets) do roll: add the engine's own rolling
  resistance when it has one (the MuJoCo test does).
- **A pack is a sample of the grading curve.** Sizes are drawn from a normal
  law in phi units (`phi_mean`, `phi_std` of the preset), and the tests check
  2000 draws per preset against it. A pack of 100 shapes is a small sample:
  its `grading` entry in `manifest.json` gives the sample's mean and spread
  next to the target's, with the Kolmogorov–Smirnov statistic and p-value.
  For a closer match, generate more shapes.
- **Calibrate for quantitative work.** For training with domain
  randomisation, these values are a sensible centre to randomise around; for a
  quantitative study, calibrate them against the real material, for example
  with its angle of repose.
- **Angle of repose not verified.** The pile test proves that grains settle
  and stay put, not that a heap takes the real material's slope. Two CPU
  tests were tried in MuJoCo 4.0.1 and neither can be trusted. A heap poured
  from a lifted cylinder (200 crushed-gravel grains, 15 minutes) came to rest
  at about 21°, well below what crushed stone does. A tilting bed (54 to 96
  free grains on a layer of fixed ones) started to slide at 31° for crushed
  gravel and 33–35° for glass beads, the reverse of the real materials'
  order. A few hundred grains is too few for a slope to mean anything, and
  more does not fit in a CPU check. No angle of repose is published for any
  preset until a test reproduces known materials.

## Known limits

- **Real units.** See *Physics limits by grain size* above.
- **No grain-by-grain physics at large scale.** CPU physics targets a few
  hundred grains; instancing is for rendering surfaces.
- **Angularity is a proxy**, not Wadell roundness, and is only comparable
  between grains of the same mesh resolution.
- **Collision uses a convex hull of 64 points** for rigid grains, within 2.4 %
  of the grain's size of its full hull. Pits, creases and dents are visible
  but not part of the collision shape; hollow shells (whole
  seashells) are not generated. Deformable grains collide with their
  tetrahedral mesh.
- **Deformables work only with NVIDIA OmniPhysics, untested.** Until OpenUSD
  standardises deformable bodies, packing peanuts and cherry tomatoes are
  simulated as deformables only in Omniverse / Isaac Sim (GPU); elsewhere they
  are static meshes unless exported with `--no-deformable`. They have not been
  run in Isaac Sim yet.
- **Mesh resolution.** Marching cubes runs on a 48-cell grid along the longest
  axis; the sharpest edges can show slight stair-stepping.
