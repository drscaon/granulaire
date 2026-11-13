# Physics: method, values and checks

How shapes are made, the friction and restitution table, the pile tests in MuJoCo and Blender, and what changes with grain size.

Part of the [Granulaire](../README.md) documentation.

## Method in brief

Each grain is an implicit volume, meshed with marching cubes:

1. **Base body.** Rocks: a random convex polyhedron (the hull of points drawn
   on an ellipsoid with Zingg proportions; few facets give an angular grain),
   with edges rounded by replacing the *max* in its gauge with a p-norm (low p
   gives a rounded grain, high p sharp edges). Kernels and seeds: a
   superellipsoid. Pellets: a cylinder with rounded end edges.
2. **Fracture chips.** Random planes cut the body, leaving flat broken faces
   with sharp edges (crushed stone, broken pebbles, broken pellet ends).
3. **Taper and irregularity.** An egg or wedge taper along the long axis, then
   low-frequency lumps, pits (scoria vesicles, flint dents), a crease (wheat),
   a crown dent (maize), a kidney bend with its hilum (beans) and light
   roughness.
4. **Mesh and scale.** Marching cubes on the zero level set, recentring on the
   centre of mass, scaling to the target nominal diameter.
5. **Collider.** A separate `collision` mesh (purpose `guide`): the grain's
   convex hull reduced to at most 64 points, PhysX's default hull vertex limit,
   by adding the point farthest outside the hull so far, then scaled to the full
   hull's volume. Every engine collides with this same shape: PhysX would
   otherwise rebuild a 64-vertex hull on its own, while MuJoCo and Bullet keep
   every vertex. Over all presets the collider stays within 2.4 % of the grain's
   size of its full hull (median 1.5 %), with the same volume.

## Friction and restitution

Every grain gets a standard OpenUSD physics material (`UsdPhysicsMaterialAPI`:
static friction, dynamic friction, restitution), bound to its collision mesh
with the `physics` purpose. With moisture enabled there is one material per
state, and each grain's `moisture` variant selects it. The ground has its own
material, the one every Primvaria project gives its ground (below).

### Values

Dynamic friction is 90 % of static friction. In wet states, friction is
multiplied by 1.10 (damp: a little water makes grains grip), 1.00 (wet) and
0.80 (saturated: grains slide on the water); restitution by 0.60, 0.40
and 0.30. The values are realistic orders of magnitude, ranked sensibly
(angular crushed rock grips more than round, polished or waxy grains), not
measurements of a specific deposit.

| Preset | Static μ (dry) | Dynamic μ (dry) | Restitution (dry) | Static μ damp | Static μ wet | Static μ saturated |
|---|---|---|---|---|---|---|
| `beach_sand` | 0.55 | 0.50 | 0.10 | 0.61 | 0.55 | 0.44 |
| `dune_sand` | 0.50 | 0.45 | 0.10 | 0.55 | 0.50 | 0.40 |
| `volcanic_sand` | 0.60 | 0.54 | 0.10 | 0.66 | 0.60 | 0.48 |
| `rounded_gravel` | 0.55 | 0.50 | 0.15 | 0.61 | 0.55 | 0.44 |
| `crushed_gravel` | 0.65 | 0.59 | 0.15 | 0.72 | 0.65 | 0.52 |
| `marble_chips` | 0.60 | 0.54 | 0.15 | 0.66 | 0.60 | 0.48 |
| `pozzolana` | 0.75 | 0.68 | 0.10 | 0.83 | 0.75 | 0.60 |
| `river_pebbles` | 0.50 | 0.45 | 0.20 | 0.55 | 0.50 | 0.40 |
| `beach_pebbles` | 0.40 | 0.36 | 0.25 | 0.44 | 0.40 | 0.32 |
| `railway_ballast` | 0.70 | 0.63 | 0.15 | 0.77 | 0.70 | 0.56 |
| `iron_ore` | 0.70 | 0.63 | 0.12 | 0.77 | 0.70 | 0.56 |
| `coal` | 0.55 | 0.50 | 0.10 | 0.61 | 0.55 | 0.44 |
| `rubber_mulch` | 0.85 | 0.77 | 0.55 | 0.94 | 0.85 | 0.68 |
| `wheat` | 0.40 | 0.36 | 0.40 | 0.44 | 0.40 | 0.32 |
| `maize` | 0.45 | 0.41 | 0.35 | 0.50 | 0.45 | 0.36 |
| `rice` | 0.40 | 0.36 | 0.30 | 0.44 | 0.40 | 0.32 |
| `beans` | 0.35 | 0.32 | 0.40 | 0.39 | 0.35 | 0.28 |
| `soybean` | 0.35 | 0.32 | 0.45 | 0.39 | 0.35 | 0.28 |
| `cherry_tomatoes` | 0.45 | 0.41 | 0.20 | — | — | — |
| `plastic_pellets` | 0.30 | 0.27 | 0.50 | 0.33 | 0.30 | 0.24 |
| `wood_pellets` | 0.50 | 0.45 | 0.20 | 0.55 | 0.50 | 0.40 |
| `packing_peanuts` | 0.50 | 0.45 | 0.30 | — | — | — |
| `lunar_regolith` | 0.75 | 0.68 | 0.05 | — | — | — |
| `martian_regolith` | 0.70 | 0.63 | 0.05 | — | — | — |
| `glass_beads` | 0.35 | 0.32 | 0.85 | 0.39 | 0.35 | 0.28 |

— : no moisture states for this preset. Packing peanuts and cherry tomatoes
are deformable: NVIDIA OmniPhysics ignores static friction for deformables, so
their single value is written as both static and dynamic friction, and
restitution does not apply (their bounce comes from elasticity and damping, see
[Deformable grains](usage.md#deformable-grains-packing-peanuts-cherry-tomatoes)); the
restitution shown is used when they are exported as rigid bodies
(`--no-deformable`).

### Which engines use it

| Tool | Friction and restitution from the USD file |
|---|---|
| NVIDIA Isaac Sim / Omniverse (PhysX) | **Used**, including the material selected by each grain's moisture variant. PhysX averages the two materials in contact by default (`physxMaterial:frictionCombineMode` to change it). |
| Other engines importing `UsdPhysics` (e.g. Newton) | Should be read, as it is the standard schema; not tested here. |
| Blender | **Not used by the importer**: Blender's USD importer does not import physics data. `granulaire blender-test` reads it from the file and sets the rigid bodies up (see [Physics checks](#physics-checks)). |
| MuJoCo | Not native; `granulaire sim-test` builds the MuJoCo model from the file (see [Physics checks](#physics-checks)). MuJoCo combines friction differently (it takes the larger of the two) and has no restitution coefficient. |
| Gazebo, PyBullet | Not native; depends on the converter. |

## Physics checks

Every preset is dropped as a pile in **MuJoCo** and in **Blender**, from the
OpenUSD file only, and must settle:

```bash
pip install "granulaire[sim]"                 # MuJoCo
granulaire generate --preset crushed_gravel --shapes 20 --copies 2 --moisture
granulaire sim-test output/crushed_gravel     # MuJoCo
granulaire blender-test output/crushed_gravel # Blender (bpy module, Python 3.13, or blender on the PATH)
```

| Check | Meaning |
|---|---|
| `imported` (Blender) | every rigid grain of the file becomes a mesh object through Blender's USD importer |
| `mass` | the engine's total mass is the sum of the masses in the file (through each grain's moisture variant) |
| `finite` | no invalid coordinate |
| `ground` | no grain below the ground by more than a quarter of its thickness |
| `overlap` | at rest, no grain inside another (MuJoCo: no contact deeper than a quarter of the grain thickness, half during impacts; Blender: no grain's centre inside another's hull) |
| `energy` | potential + kinetic energy never rises by more than 1 % of the energy released: the engine adds none |
| `rest` | at the end, the fastest grain moves slower than 5 % of the speed of a fall from its own thickness, and less than 0.1 % of the energy released is left |

The model is built from the file only: each grain's collision mesh (its
convex hull of at most 64 points, as the file's `convexHull` approximation
asks), mass, friction and
restitution of its physics material, the ground. Reports are written to
`<folder>/sim_test/` (with the MuJoCo model, `mujoco_pile.xml`) and
`<folder>/blender_test/`. CI runs both tests on **all 25 presets**, deformable
presets as rigid bodies (`--no-deformable`).

**Scaled units.** Engines have absolute tolerances (collision margins, contact
offsets, minimum masses) set for objects of a few centimetres or more, which
is why the table [below](#physics-limits-by-grain-size) rates sand as not
usable as individual rigid bodies at real scale. The tests therefore multiply
**every length and the gravity by the same factor** (and every mass by
another): with gravity and frictional contact as the only forces, the motion
is the same in time as at real scale (same Froude number, same mass ratios,
same friction and restitution), and only the numbers the engine sees change.
Grains are run at least 2 cm big in MuJoCo and 10 cm in Blender (Bullet works
best above ~0.1 m; Blender's USD importer accepts at most ×1000). Do the same
to simulate fine grains in your own scenes.

**Test settings, not asset properties:**

- MuJoCo: rolling friction of 2 % of the grain thickness. UsdPhysics has no
  rolling resistance, and without any a rounded pebble rolls forever on a flat
  floor; granular simulations usually use 0.01–0.1. The file's restitution is
  not used (MuJoCo contacts are soft).
- Blender: Bullet multiplies the frictions (and restitutions) of the two
  bodies in contact, so each body gets the square root of its value (two
  grains of the same material get exactly the file's value). Each grain
  collides with the file's collider (64 points at most), not with its render
  mesh. The ground gets a thickness below its surface: a
  zero-thickness plane is unreliable in Bullet. Blender's default damping
  (linear 0.04, angular 0.1) is kept.

**Not tested: deformable grains.** Packing peanuts and cherry tomatoes as
deformable bodies need NVIDIA OmniPhysics (Isaac Sim, an RTX GPU); see
[Deformable grains](usage.md#deformable-grains-packing-peanuts-cherry-tomatoes).

## Physics limits by grain size

Grains are generated at their **real size**. That is right for rendering and
perception, but many of them are too small or too light for today's
rigid-body engines with default settings. Rules of thumb behind the table:

- **Bullet** (PyBullet, Blender) works best with objects larger than ~0.1 m,
  and Blender's default collision margin is 0.04 m.
- **PhysX** (Isaac Sim, Omniverse) uses a default `contactOffset` of 0.02 m
  per shape at metric scale, so two shapes are treated as touching from ~4 cm.
- **Tunnelling**: at 60 Hz, a grain falling at 1–2 m/s travels 1.7–3.3 cm per
  step and can pass through surfaces smaller than that without CCD or substeps.
- **Mass ratio**: iterative solvers become unstable when very light grains
  touch a much heavier body, such as a robot foot weighing a few kilograms.

| Physics risk | Presets (median nominal size · mean grain mass) | What to do |
|---|---|---|
| **Not usable as individual rigid bodies at real scale** (fine with scaled units, see [Physics checks](#physics-checks)) | `lunar_regolith` (0.07 mm · ~13 µg), `martian_regolith` (0.12 mm · ~0.1 mg), `dune_sand` (0.22 mm · ~18 µg), `beach_sand` (0.36 mm · ~0.1 mg), `volcanic_sand` (0.49 mm · ~0.4 mg), `glass_beads` (1 mm · ~1.4 mg) | Use for rendering and perception; for physics, use a continuum model (MPM), a deformable heightfield, or scaled-up grains |
| **Unstable without tuning** | `rice` (2.8 mm, 1.6 mm thick · ~18 mg), `plastic_pellets` (3.4 mm · ~20 mg), `wheat` (4.1 mm · ~53 mg), `rounded_gravel` (5.8 mm · ~0.4 g), `soybean` (6.6 mm · ~0.19 g), `beans` (9.1 mm, 5.8 mm thick · ~0.53 g), `maize` (7.4 mm, 4.7 mm thick · ~0.29 g), `crushed_gravel` (8.2 mm · ~1 g) | Reduce contact offsets / margins to ~1 mm, enable CCD, use substeps or a smaller time step |
| **Workable with tuning** | `packing_peanuts` (20 mm, ~9 mm thick · ~50 mg, extremely light), `wood_pellets` (9.8 mm, 6 mm thick · ~0.6 g), `pozzolana` (11 mm · ~1.5 g, very light), `marble_chips` (11.5 mm · ~2.5 g), `iron_ore` (16 mm · ~17 g), `rubber_mulch` (20 mm, 12 mm thick · ~6 g), `cherry_tomatoes` (25 mm · ~8 g, deformable) | Same settings as above; check stability against the heaviest body in contact |
| **Generally fine** | `coal` (23 mm · ~15 g), `beach_pebbles` (38 mm, 18 mm thick · ~140 g), `railway_ballast` (40 mm · ~100 g), `river_pebbles` (46 mm · ~230 g) | Keep CCD on for impacts; in Blender, lower the default 0.04 m margin |

For elongated or flat grains (rice, maize, beans, pellets), the **thickness** is what
matters for tunnelling, not the nominal size. Packing peanuts are large but
weigh almost nothing: the mass ratio with anything they touch is the main risk,
and as deformable bodies they are simulated only by NVIDIA OmniPhysics (see
above).

These are orders of magnitude, not hard limits: the actual threshold depends
on the engine, time step, solver iterations, contact settings and the bodies
in contact. Scaling grains up changes the physics (mass, inertia, contact
forces scale differently), so treat it as an approximation of the material.

**Perception is not affected.** Cameras and renderers have no minimum size:
every preset, including sand and regoliths, can be used at real scale for
synthetic images, ground-truth masks, grading-from-image benchmarks or
appearance studies (moisture darkening and gloss). Only dynamics need the
precautions above. A thin layer of a few hundred grains on a hard surface
(the "sand on the ramp" case) is also within reach of rigid-body engines for
the gravel and pebble presets.
