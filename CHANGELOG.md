# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Changed
- GitHub Actions moved to versions running on Node.js 24 (`actions/checkout@v7`,
  `actions/setup-python@v7`, `actions/upload-artifact@v7`), removing the
  Node.js 20 deprecation warnings.

### Added
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
