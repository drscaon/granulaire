# OpenUSD layout and contract

The ground and physics scene, OpenUSD compliance, and what the Primvaria contract writes on every grain.

Part of the [Granulaire](../README.md) documentation.

## Ground and physics scene (the same in every Primvaria project)

Every file with physics carries the same two prims, so that assets from
different generators can share one scene and every engine gets the same floor:

| Prim | What it is |
|---|---|
| `/World/PhysicsScene` | gravity 9.81 m/s² along −Z |
| `/World/Ground` | a static box (`UsdGeom.Cube`, `CollisionAPI`), its top face at z = 0, 2 cm thick, covering the content with 0.5 m to spare on each side (1 m × 1 m at least), grey and rendered, no PhysX attributes (engines derive their contact offsets) |
| `/World/GroundMaterial` | its physics material: static friction 0.6, dynamic friction 0.5, restitution 0.1, a wooden or concrete floor |

The code is one file, `ground.py`, identical in Granulaire, Maillage, Filaire
and Quincaillerie; a test checks every generated file against it. The MuJoCo
checks and the Blender rigid-body checks take the ground's friction from the
file (Blender's cloth, in Maillage, has its own collision settings).

## OpenUSD compliance

```bash
python -m granulaire.validate output/beach_sand
```

This runs every validator of OpenUSD's `UsdValidation` registry on each file,
the checks `usdchecker` runs: composition, stage metadata (meters, Z up),
geometry, material bindings, shaders, UsdPhysics rigid bodies and colliders.
Each file is checked once per variant (every moisture state), since a variant
that is not selected is not composed. The tests and CI require no error and no
warning, on every preset.

## Primvaria contract

```bash
python -m granulaire.conformance output/beach_sand
```

Granulaire is part of [Primvaria](https://primvaria.com) and follows its
[mission](https://github.com/drscaon/primvaria/blob/main/MISSION.md) and its
[OpenUSD contract](https://github.com/drscaon/primvaria/blob/main/docs/contract.md),
version 0, which the four generators share. Every grain is an asset any tool
can find without knowing Granulaire: a model of kind `component` (under
`/World`, an `assembly`) with `assetInfo` (name, identifier, version) and the
attributes `primvaria:contract`, `primvaria:generator`, `primvaria:version`,
`primvaria:preset` and `primvaria:seed`, written on the prototype and
inherited by each grain that references it. The command above checks the
stage units, the model hierarchy and this identity; the tests and CI require
it on every preset.

What was drawn for each grain is in the file too, its ground truth:
`primvaria:variation:aspects` lists the aspects that were switched on
(`size`, `shape`, `roundness`, `mineralogy`, `orientation`, `moisture`) and `primvaria:variation:<name>` holds each drawn value
(`diameter_m`, `elongation`, `flatness`, `facets`, `roundness_p`, `chips`, `pits`, `mineral`, `color_rgb`…). They are written on the prototype; a grain adds its own drawn `moisture` state, and its orientation is its transform. An aspect that is switched off is still recorded, at its
nominal value, and the other aspects keep their draws.

What was measured on each grain once generated is there as well, as
`primvaria:measured:<name>` (`mass_kg`, `mass_<state>_kg`, `volume_m3`, `sphericity`, `convexity`, `angularity_deg`, the three axes…).
The pack's `instances.csv` is read back from the OpenUSD files, one row per
asset with the same names (`variation:<name>`, `measured:<name>`), and
`manifest.json` says what the pack is; both have the same shape in the four
generators, and the command above fails when the table and the files disagree.
