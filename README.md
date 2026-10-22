# Granulat

Procedural granular materials for simulation: realistic grains instead of
perfect spheres, exported to **OpenUSD** with physical properties.
Everything runs on CPU.

## What it does

- Generates *N* distinct grain shapes (100 by default) from distributions
  borrowed from sedimentology: size on the phi scale (Wentworth), Zingg ratios
  (elongation I/L, flatness S/I), angularity and mineralogy.
- Places each shape *k* times (5 by default) in shuffled order with random
  orientations: 500 grains per scene.
- **Measures** every generated grain (nominal diameter, Zingg ratios, Wadell
  sphericity, convexity, angularity proxy) instead of trusting the inputs.
- Exports an OpenUSD scene: prototypes, grains by reference, UsdPreviewSurface
  materials, `UsdPhysics` rigid bodies (mass from volume and density,
  convex-hull collision, friction, restitution) and a collision ground.
- Optionally gives every grain a moisture state through an OpenUSD variant set.

## Installation

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[render]"        # add ",dev" for tests and linting
```

Requires Python 3.10+.

## Usage

```bash
granulat list
granulat generate --preset beach_sand --shapes 100 --copies 5 --seed 1
granulat generate --preset beach_pebbles --moisture --moisture-weights 0,20,50,30
granulat generate --preset rounded_gravel --no-size --no-orientation
granulat render output/beach_sand output/crushed_gravel
granulat render-moisture output/beach_pebbles output/crushed_gravel output/beach_sand
```

`python -m granulat ...` works too. From Python:

```python
from granulat import Variations, generate_scene, write_outputs

scene = generate_scene("beach_sand", shapes=100, copies=5, seed=1,
                       variations=Variations(moisture=True))
write_outputs(scene, "output")
```

### Presets

| Category | Presets |
|---|---|
| Sand | `beach_sand`, `dune_sand`, `volcanic_sand` |
| Gravel | `rounded_gravel`, `crushed_gravel`, `marble_chips`, `pozzolana` |
| Pebbles | `river_pebbles`, `beach_pebbles` |
| Industrial | `railway_ballast`, `iron_ore`, `coal` |
| Space | `lunar_regolith`, `martian_regolith` (no moisture) |
| Reference | `glass_beads`: exact spheres, the baseline to compare real grains against |

Values are realistic orders of magnitude, not measurements of a specific deposit.

### Variations (checkboxes)

| Option | On | Off |
|---|---|---|
| `--size` | diameter drawn from the grading curve | all at d50 |
| `--shape` | elongation / flatness drawn | mean values |
| `--roundness` | facets and edge rounding drawn | median values |
| `--mineralogy` | mineral and tint drawn | dominant mineral |
| `--orientation` | random orientation | all aligned |
| `--moisture` (off by default) | variant set + state drawn per grain | no moisture |

Turning one variation off does not change the other random draws: with the
same seed you compare the same scene with a single difference.

### Moisture (OpenUSD variant set)

Every prototype carries a `moisture` variant set (`dry`, `damp`, `wet`,
`saturated`) and every grain selects its own. A state changes:

- **mass**: absorbed water plus a surface film, capped by the pore water of a
  heap. Median water content of a beach-sand grain: 3.6 / 14 / 24 %; of a
  crushed-gravel grain: 0.5 / 1.6 / 2.4 %;
- **appearance**: darker colour, lower roughness, clearcoat (UsdPreviewSurface);
- **contact**: friction and restitution (one UsdPhysics material per state),
  plus capillary cohesion in the custom attribute `granulat:capillaryCohesion`,
  since UsdPhysics has no standard schema for it.

In usdview or Omniverse, change a grain's state by changing its variant
selection. Blender's USD importer takes the state selected at import time.
Contact and cohesion coefficients are indicative and still need calibrating.

## Outputs (per preset, under `output/<preset>/`)

| File | Content |
|---|---|
| `granulat_<preset>.usdc` | OpenUSD scene (Blender: File > Import > USD) |
| `prototype_metrics.csv` | measured descriptors, mass (per moisture state), parameters |
| `instances.csv` | grain → shape, position, moisture state |
| `summary.json` | global statistics (d50, mean sphericity, masses, water) |
| `prototypes.npz` | meshes, used by the renderer |
| `shape_sheet.png`, `mix_preview.png` | previews (`granulat render`) |

## Method in brief

1. Build a random convex polyhedron: the hull of points drawn on an ellipsoid
   with Zingg proportions. Few facets give an angular grain.
2. Round edges and corners by replacing the *max* in the polyhedron's gauge
   with a p-norm. Low p gives a rounded grain, high p sharp edges.
3. Add light surface roughness, then scale to the target nominal diameter.

## Known limits

- **Real units.** A sand grain is ~0.35 mm; physics engines are unstable at
  that scale, so scale up for rigid-body tests.
- **No grain-by-grain physics at large scale.** CPU physics targets a few
  hundred grains; instancing is for rendering surfaces.
- **Angularity is a proxy**, not Wadell roundness, and is only comparable
  between grains of the same mesh resolution.
- **Convex grains only**: no fractures or concave shells yet.

## Development

```bash
pip install -e ".[dev]"
pytest            # test suite
ruff check .      # lint
ruff format .     # format
```

### Commits and versions

- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/)
  (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `build:`, `chore:`).
- Versions follow [Semantic Versioning](https://semver.org/). The version
  lives in one place, `pyproject.toml`; `granulat.__version__` reads it from
  the installed package metadata.
- To release: update `version` in `pyproject.toml`, move the `Unreleased`
  entries of `CHANGELOG.md` under the new version with its date, commit as
  `chore(release): X.Y.Z`, then tag `vX.Y.Z` (annotated).
