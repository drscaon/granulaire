# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

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
