# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Ground truth of the variation, in the file (Primvaria contract, variation
  model): `primvaria:variation:aspects`, the aspects that were switched on, and
  one `primvaria:variation:<name>` per drawn value (`diameter_m`, `elongation`, `flatness`, `facets`, `roundness_p`, `chips`, `pits`, `mineral`, `color_rgb`…).
  `python -m granulaire.conformance` requires the aspects on every asset.
- `CONTRIBUTING.md`, issue templates (bug report, material preset request),
  `SECURITY.md` and `CITATION.cff`.
- Primvaria OpenUSD contract, version 0
  ([docs/contract.md](https://github.com/drscaon/primvaria/blob/main/docs/contract.md)):
  every grain is a model of kind `component` with `assetInfo` (name,
  identifier, version) and the attributes `primvaria:contract`,
  `primvaria:generator`, `primvaria:version`, `primvaria:preset` and
  `primvaria:seed`; `/World` is an `assembly`, `/World/Grains` and
  `/World/Prototypes` are groups.
- `python -m granulaire.conformance`: checks files against the contract (stage
  units, model hierarchy, identity). Run in the tests and, in CI, on every
  preset.

## [0.3.0b1] - 2026-11-11 (beta)

### Breaking changes

- Python 3.11 or later (was 3.10): MuJoCo 4 requires it, and Python 3.10 reached
  its end of life in October 2026.
- `usd-core` 26.5 or later (was 24.0): the OpenUSD validators do not load from
  earlier wheels (25.5 lacks the validator libraries, 25.8 and 25.11 the
  UsdPreviewSurface definitions), and 24.x has no `UsdValidation` at all. A CI
  job runs the tests on exactly 26.5.
- MuJoCo 4 (`mujoco>=4.0`, was 3.2) for the `sim` and `dev` extras; MuJoCo 3 is no
  longer supported.
- The ground and physics scene are the same in every Primvaria project (`ground.py`, the
  same file in each): `/World/PhysicsScene`, gravity 9.81 m/s² along −Z; `/World/Ground`,
  a 2 cm box (`UsdGeom.Cube`) whose top is z = 0, covering the content with 0.5 m to
  spare, rendered, no PhysX attributes; `/World/GroundMaterial`, static friction 0.6,
  dynamic 0.5, restitution 0.1. A test checks every generated file against it.
  Granulaire's ground was a flat mesh sized to the pile, with its physics material at
  `/World/Looks/Phys_ground` (friction 0.6/0.54); that prim is gone.
- Rigid grains collide with a new `collision` child mesh (purpose `guide`, convex hull
  of at most 64 points, scaled back to the full hull's volume), not with the render
  mesh, which no longer has `CollisionAPI`. The physics material is bound on the
  collider; the render mesh keeps the visual one. Tools that read the render mesh
  as the collider must read `collision` instead. PhysX caps a hull at 64 vertices by
  default and rebuilt a coarser grain on its own: MuJoCo, Blender and PhysX now collide
  with the same shape, within 2.4 % of the grain's size of its full hull. The Blender
  pile test takes the file's collider instead of reducing the render mesh itself.

### Added

- `granulaire sim-test`: pile test in MuJoCo, built from the OpenUSD file only
  (collision hulls, masses through the moisture variants, friction, ground);
  checks mass, finite values, ground, overlap, energy and rest. The MuJoCo
  model is written next to the report. Extra `sim`.
- `granulaire blender-test` (and `blender-script`): the same pile test in
  Blender, through Blender's USD importer; runs with the `bpy` module (extra
  `blender`, Python 3.13) or with `blender` on the PATH.
- Both run in scaled units (lengths and gravity by the same factor, masses by
  another), which leaves the motion unchanged: sand and regolith grains, not
  usable at real scale, pass too. CI runs both on all 25 presets.
- `python -m granulaire.validate FILE_OR_FOLDER`: every OpenUSD `UsdValidation` validator
  (what `usdchecker` runs) on each file and each variant; the tests and a CI job
  (every preset) require no error and no warning.

### Changed

- README: the same header as the other Primvaria projects (PyPI and suite
  badges), an Engines table matching the suite's engine matrix, and links to
  primvaria.com.

## [0.2.0b3] - 2026-10-29 (beta)

First release on PyPI.

### Changed

- Released on PyPI (`pip install granulaire`) by the release workflow, through Trusted Publishing.
- README images and links use absolute URLs, so that they show on PyPI; the README links to Primvaria, the suite the project belongs to.

## [0.2.0b2] - 2026-10-23 (beta)

Second beta: two new materials (25 in all), distinct river and beach pebbles,
friction documentation, optional shuffling, and continuous integration.

### Added
- `rubber_mulch` preset (Industrial): shredded recycled-tyre nuggets, ~20 mm,
  torn and jagged, very grippy (friction 0.85) and bouncy (restitution 0.55),
  natural black with dyed nuggets; surface water only.
- `cherry_tomatoes` preset (Agricultural): ~25 mm glossy fruit with a stem
  scar, deformable (E ≈ 0.5 MPa, ν ≈ 0.45) for NVIDIA OmniPhysics, no moisture.
- Shuffling is optional: `--no-shuffle` on the command line, `shuffle=False` in
  `generate_scene`, places the copies of each shape side by side. Shapes,
  positions and orientations are unchanged. `summary.json` records `shuffled`.
- `surface_roughness` preset entry: glossy surfaces (fruit skin) in the USD
  materials and the previews.
- Deformable materials also apply `OmniPhysicsBaseMaterialAPI` (density,
  friction) and `PhysxDeformableMaterialAPI` with
  `physxDeformableMaterial:elasticityDamping`, which controls how much a
  deformable grain bounces (starting values, uncalibrated).
- README section "Friction and restitution": values per preset and moisture
  state, which engines use them, and limits (cohesion, rolling resistance).
- Blender screenshots of gravel and sand in the README ("In Blender").
- Continuous integration with GitHub Actions: lint, tests on Python 3.10–3.13
  (Linux) and on macOS and Windows, command-line smoke test, package build and
  check.
- Release workflow: a `v*` tag builds the packages and publishes them on the
  GitHub release, marked as a pre-release for alpha, beta and rc versions.
- Dependabot for GitHub Actions and Python dependencies.
- CI, Python and license badges in the README.
- GitHub Flow: changes reach `main` only through pull requests from
  short-lived branches; a versioned `pre-push` hook (`.githooks/`) refuses
  direct pushes to `main`.

### Changed
- River and beach pebbles now differ in shape and material:
  - `river_pebbles`: rounder and more equant (mean S/I ~0.71), uniformly
    smooth, no fracture chips; earthy mix of tan quartzite, grey granite, brown
    sandstone, buff limestone, green greenstone and red jasper;
  - `beach_pebbles`: flatter discs and ovals (mean S/I ~0.38), polished, no
    pits; black, charcoal and blue-grey basalt, white and grey marble, with a
    higher density (2850 kg/m³), lower absorption and friction.
  README tables (weight gain, physics limits) and moisture gallery updated.
- `--shapes` and `--copies` (and `shapes=`, `copies=` in Python) reject values
  below 1 with a clear message; their defaults (100 and 5) are shown in the help.
- README: deformable grains are stated as untested in Isaac Sim; the Python
  example writes both scenes it generates.
- GitHub Actions moved to versions running on Node.js 24 (`actions/checkout@v7`,
  `actions/setup-python@v7`, `actions/upload-artifact@v7`), removing the
  Node.js 20 deprecation warnings.

### Fixed
- Grains in the OpenUSD scene are spaced from their full reach (bounding
  sphere), so angular grains can no longer start in contact with a neighbour.
- `mix_preview.png` places grains without overlaps and follows `--no-shuffle`.

## [0.2.0b1] - 2026-10-22 (beta)

First beta, under the new name Granulaire.

### Added
- MIT license.
- "Granulaire" logo (light and dark versions, "ai" highlighted, a shaded
  hexagonal grain as the dot of the "i") and a Physical AI description in the
  README.
- Agricultural presets: `wheat`, `maize`, `rice`, `beans`, `soybean`; pellet presets:
  `plastic_pellets`, `wood_pellets`; new categories Agricultural and Pellets.
- Deformable packing peanuts: `packing_peanuts` (EPS), new Packaging
  category. Tube shape family (S, C or straight), tetrahedral
  simulation mesh (`UsdGeom.TetMesh`) and NVIDIA OmniPhysics deformable
  schemas (body, volume simulation, bind pose, material). Deformable
  simulation works only with NVIDIA OmniPhysics (Omniverse, Isaac Sim 5+);
  `--no-deformable` exports them as rigid bodies for other engines.
  No moisture states: EPS never gets wet.
- Shape families: superellipsoid (kernels, seeds) and cylinder (pellets),
  plus crease, crown dent, kidney bend and axial end cuts.
- Per-preset irregularity: fracture chips, low-frequency lumps, egg/wedge
  taper and pits, so material families look clearly different.
- `granulaire render-gallery`: several grains per preset shown in every
  moisture state; README illustrated with the gallery of all presets.
- README section on physics limits by grain size: which presets are unstable
  in current rigid-body engines, recommended settings, and why perception use
  is unaffected.

### Changed
- **Project renamed from `granulat` to `granulaire`**: Python package
  (`import granulaire`), command line (`granulaire`), PyPI name, output file
  names (`granulaire_<preset>.usdc`) and the USD attribute namespace
  (`granulaire:*`, was `granulat:*`). Files exported by 0.1.0 keep the old
  attribute names.
- Grains are meshed from implicit volumes with marching cubes (new
  dependency: scikit-image). Triangles stay well shaped on flat fracture
  faces; meshes are watertight.
- Shapes generated for a given seed differ from 0.1.0; each grain now uses its
  own random stream.
- L, I and S are measured along the principal axes (faster than the
  minimum-volume box); all metrics are computed at unit scale so micron-sized
  grains are measured reliably.

### Fixed
- Dark scratch marks on flat faces of crushed grains (folded sliver triangles).
- Measurement failure on the smallest regolith grains.

## [0.1.0] - 2026-10-22

### Added
- Procedural grain shapes: random convex polyhedron rounded by a p-norm gauge,
  scaled to a target nominal diameter; exact spheres for the reference preset.
- Shape metrics measured on every generated mesh: nominal diameter, Zingg
  ratios, Wadell sphericity, convexity, angularity proxy.
- 15 presets in 6 categories: Sand, Gravel, Pebbles, Industrial, Space, Reference.
- OpenUSD export: prototypes plus referencing grains, rigid body, mass,
  convex-hull collision, UsdPreviewSurface and UsdPhysics materials.
- Per-grain moisture as a `moisture` variant set (dry, damp, wet, saturated)
  changing mass, appearance, friction, restitution and a custom capillary
  cohesion attribute.
- Variation toggles: size, shape, roundness, mineralogy, orientation, moisture;
  turning one off leaves the other random draws unchanged.
- `granulat` command line: `list`, `generate`, `render`, `render-moisture`.
- CPU previews: shape sheet, mixed-scene preview, metrics chart, moisture states.
- Test suite (pytest) and lint configuration (ruff).
