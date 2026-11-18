# Sources of the physical values

Every value of Granulaire that describes the real world (a grain's size and
sorting, density, friction, restitution and water absorption, the stiffness
of the soft grains, the moisture model) names its source below: a
classification table of sedimentology, a standard's requirements, a handbook
or a paper, or, where none was found, an estimate with what it rests on.
Where a source gives a range, the value lies within it
(`tests/test_sources.py`).

A preset is a kind of material, not a measurement of a specific deposit: its
source is the class it belongs to (medium sand for beach sand, the EN 13450
grading for railway ballast) or the density of its mineral. A size class
bounds a material's mean size; its grains spread around it by their sorting,
as a real sediment's do. The shape parameters describe Granulaire's shape
model and are estimates, checked by the measured sphericity and roundness of
the grains (see [Physics](physics.md)). Friction, restitution and the
moisture model are mostly estimates: nothing is calibrated.

The tables are written from `granulaire/sources.py`
(`python -m granulaire.sources`).

Part of the [Granulaire](../README.md) documentation.

<!-- sources: begin -->
| Value | | Unit | Range the source gives | Source |
|---|---|---|---|---|
| `PRESETS.beach_sand.phi_mean` | 1.5 | phi | 1 to 2 | [wentworth](#wentworth) |
| `PRESETS.beach_sand.phi_std` | 0.45 | phi | 0.35 to 0.5 | [folk](#folk) |
| `PRESETS.beach_sand.density` | 2650 | kg/m³ | 2650 to 2650 | [quartz](#quartz) |
| `PRESETS.beach_sand.friction` | 0.55 |  |  | [friction](#friction) |
| `PRESETS.beach_sand.restitution` | 0.1 |  |  | [restitution](#restitution) |
| `PRESETS.beach_sand.absorption` | 0.005 |  |  | [absorption](#absorption) |
| `PRESETS.beach_sand.elongation_beta.0` | 8 |  |  | [shape](#shape) |
| `PRESETS.beach_sand.elongation_beta.1` | 3 |  |  | [shape](#shape) |
| `PRESETS.beach_sand.flatness_beta.0` | 7 |  |  | [shape](#shape) |
| `PRESETS.beach_sand.flatness_beta.1` | 3 |  |  | [shape](#shape) |
| `PRESETS.beach_sand.facets.0` | 14 |  |  | [shape](#shape) |
| `PRESETS.beach_sand.facets.1` | 30 |  |  | [shape](#shape) |
| `PRESETS.beach_sand.roundness_p.0` | 3 |  |  | [shape](#shape) |
| `PRESETS.beach_sand.roundness_p.1` | 9 |  |  | [shape](#shape) |
| `PRESETS.beach_sand.roughness` | 0.012 |  |  | [shape](#shape) |
| `PRESETS.beach_sand.lumpiness.0` | 0.03 |  |  | [shape](#shape) |
| `PRESETS.beach_sand.lumpiness.1` | 0.1 |  |  | [shape](#shape) |
| `PRESETS.beach_sand.taper` | 0.15 |  |  | [shape](#shape) |
| `PRESETS.beach_sand.chips.0` | 0 |  |  | [shape](#shape) |
| `PRESETS.beach_sand.chips.1` | 2 |  |  | [shape](#shape) |
| `PRESETS.beach_sand.chip_depth.0` | 0.75 |  |  | [shape](#shape) |
| `PRESETS.beach_sand.chip_depth.1` | 0.9 |  |  | [shape](#shape) |
| `PRESETS.dune_sand.phi_mean` | 2.2 | phi | 2 to 3 | [wentworth](#wentworth) |
| `PRESETS.dune_sand.phi_std` | 0.3 | phi | 0 to 0.35 | [folk](#folk) |
| `PRESETS.dune_sand.density` | 2650 | kg/m³ | 2650 to 2650 | [quartz](#quartz) |
| `PRESETS.dune_sand.friction` | 0.5 |  |  | [friction](#friction) |
| `PRESETS.dune_sand.restitution` | 0.1 |  |  | [restitution](#restitution) |
| `PRESETS.dune_sand.absorption` | 0.003 |  |  | [absorption](#absorption) |
| `PRESETS.dune_sand.elongation_beta.0` | 10 |  |  | [shape](#shape) |
| `PRESETS.dune_sand.elongation_beta.1` | 2.5 |  |  | [shape](#shape) |
| `PRESETS.dune_sand.flatness_beta.0` | 9 |  |  | [shape](#shape) |
| `PRESETS.dune_sand.flatness_beta.1` | 2.5 |  |  | [shape](#shape) |
| `PRESETS.dune_sand.facets.0` | 20 |  |  | [shape](#shape) |
| `PRESETS.dune_sand.facets.1` | 40 |  |  | [shape](#shape) |
| `PRESETS.dune_sand.roundness_p.0` | 1.8 |  |  | [shape](#shape) |
| `PRESETS.dune_sand.roundness_p.1` | 3.5 |  |  | [shape](#shape) |
| `PRESETS.dune_sand.roughness` | 0.008 |  |  | [shape](#shape) |
| `PRESETS.dune_sand.lumpiness.0` | 0.02 |  |  | [shape](#shape) |
| `PRESETS.dune_sand.lumpiness.1` | 0.06 |  |  | [shape](#shape) |
| `PRESETS.dune_sand.taper` | 0.1 |  |  | [shape](#shape) |
| `PRESETS.volcanic_sand.phi_mean` | 1 | phi | -1 to 4 | [wentworth](#wentworth) |
| `PRESETS.volcanic_sand.phi_std` | 0.6 | phi | 0.5 to 0.71 | [folk](#folk) |
| `PRESETS.volcanic_sand.density` | 2900 | kg/m³ | 2700 to 3000 | [rocks](#rocks) |
| `PRESETS.volcanic_sand.friction` | 0.6 |  |  | [friction](#friction) |
| `PRESETS.volcanic_sand.restitution` | 0.1 |  |  | [restitution](#restitution) |
| `PRESETS.volcanic_sand.absorption` | 0.03 |  |  | [absorption](#absorption) |
| `PRESETS.volcanic_sand.elongation_beta.0` | 6 |  |  | [shape](#shape) |
| `PRESETS.volcanic_sand.elongation_beta.1` | 3 |  |  | [shape](#shape) |
| `PRESETS.volcanic_sand.flatness_beta.0` | 6 |  |  | [shape](#shape) |
| `PRESETS.volcanic_sand.flatness_beta.1` | 3 |  |  | [shape](#shape) |
| `PRESETS.volcanic_sand.facets.0` | 10 |  |  | [shape](#shape) |
| `PRESETS.volcanic_sand.facets.1` | 22 |  |  | [shape](#shape) |
| `PRESETS.volcanic_sand.roundness_p.0` | 6 |  |  | [shape](#shape) |
| `PRESETS.volcanic_sand.roundness_p.1` | 14 |  |  | [shape](#shape) |
| `PRESETS.volcanic_sand.roughness` | 0.015 |  |  | [shape](#shape) |
| `PRESETS.volcanic_sand.lumpiness.0` | 0.05 |  |  | [shape](#shape) |
| `PRESETS.volcanic_sand.lumpiness.1` | 0.15 |  |  | [shape](#shape) |
| `PRESETS.volcanic_sand.chips.0` | 1 |  |  | [shape](#shape) |
| `PRESETS.volcanic_sand.chips.1` | 4 |  |  | [shape](#shape) |
| `PRESETS.volcanic_sand.chip_depth.0` | 0.6 |  |  | [shape](#shape) |
| `PRESETS.volcanic_sand.chip_depth.1` | 0.85 |  |  | [shape](#shape) |
| `PRESETS.volcanic_sand.pits.0` | 2 |  |  | [shape](#shape) |
| `PRESETS.volcanic_sand.pits.1` | 6 |  |  | [shape](#shape) |
| `PRESETS.volcanic_sand.pit_depth.0` | 0.08 |  |  | [shape](#shape) |
| `PRESETS.volcanic_sand.pit_depth.1` | 0.2 |  |  | [shape](#shape) |
| `PRESETS.volcanic_sand.pit_size.0` | 0.25 |  |  | [shape](#shape) |
| `PRESETS.volcanic_sand.pit_size.1` | 0.45 |  |  | [shape](#shape) |
| `PRESETS.rounded_gravel.phi_mean` | -2.5 | phi | -3 to -2 | [wentworth](#wentworth) |
| `PRESETS.rounded_gravel.phi_std` | 0.5 | phi |  | [size](#size) |
| `PRESETS.rounded_gravel.density` | 2650 | kg/m³ | 2650 to 2650 | [quartz](#quartz) |
| `PRESETS.rounded_gravel.friction` | 0.55 |  |  | [friction](#friction) |
| `PRESETS.rounded_gravel.restitution` | 0.15 |  |  | [restitution](#restitution) |
| `PRESETS.rounded_gravel.absorption` | 0.008 |  |  | [absorption](#absorption) |
| `PRESETS.rounded_gravel.elongation_beta.0` | 7 |  |  | [shape](#shape) |
| `PRESETS.rounded_gravel.elongation_beta.1` | 3 |  |  | [shape](#shape) |
| `PRESETS.rounded_gravel.flatness_beta.0` | 6 |  |  | [shape](#shape) |
| `PRESETS.rounded_gravel.flatness_beta.1` | 3 |  |  | [shape](#shape) |
| `PRESETS.rounded_gravel.facets.0` | 16 |  |  | [shape](#shape) |
| `PRESETS.rounded_gravel.facets.1` | 32 |  |  | [shape](#shape) |
| `PRESETS.rounded_gravel.roundness_p.0` | 3 |  |  | [shape](#shape) |
| `PRESETS.rounded_gravel.roundness_p.1` | 8 |  |  | [shape](#shape) |
| `PRESETS.rounded_gravel.roughness` | 0.006 |  |  | [shape](#shape) |
| `PRESETS.rounded_gravel.lumpiness.0` | 0.04 |  |  | [shape](#shape) |
| `PRESETS.rounded_gravel.lumpiness.1` | 0.12 |  |  | [shape](#shape) |
| `PRESETS.rounded_gravel.taper` | 0.2 |  |  | [shape](#shape) |
| `PRESETS.rounded_gravel.chips.0` | 0 |  |  | [shape](#shape) |
| `PRESETS.rounded_gravel.chips.1` | 2 |  |  | [shape](#shape) |
| `PRESETS.rounded_gravel.chip_depth.0` | 0.7 |  |  | [shape](#shape) |
| `PRESETS.rounded_gravel.chip_depth.1` | 0.9 |  |  | [shape](#shape) |
| `PRESETS.crushed_gravel.phi_mean` | -3 | phi | -4 to -2 | [wentworth](#wentworth) |
| `PRESETS.crushed_gravel.phi_std` | 0.35 | phi |  | [size](#size) |
| `PRESETS.crushed_gravel.density` | 2700 | kg/m³ | 2700 to 3000 | [rocks](#rocks) |
| `PRESETS.crushed_gravel.friction` | 0.65 |  |  | [friction](#friction) |
| `PRESETS.crushed_gravel.restitution` | 0.15 |  |  | [restitution](#restitution) |
| `PRESETS.crushed_gravel.absorption` | 0.01 |  |  | [absorption](#absorption) |
| `PRESETS.crushed_gravel.elongation_beta.0` | 6 |  |  | [shape](#shape) |
| `PRESETS.crushed_gravel.elongation_beta.1` | 3 |  |  | [shape](#shape) |
| `PRESETS.crushed_gravel.flatness_beta.0` | 5 |  |  | [shape](#shape) |
| `PRESETS.crushed_gravel.flatness_beta.1` | 3 |  |  | [shape](#shape) |
| `PRESETS.crushed_gravel.facets.0` | 6 |  |  | [shape](#shape) |
| `PRESETS.crushed_gravel.facets.1` | 14 |  |  | [shape](#shape) |
| `PRESETS.crushed_gravel.roundness_p.0` | 18 |  |  | [shape](#shape) |
| `PRESETS.crushed_gravel.roundness_p.1` | 45 |  |  | [shape](#shape) |
| `PRESETS.crushed_gravel.roughness` | 0 |  |  | [shape](#shape) |
| `PRESETS.crushed_gravel.lumpiness.0` | 0 |  |  | [shape](#shape) |
| `PRESETS.crushed_gravel.lumpiness.1` | 0.04 |  |  | [shape](#shape) |
| `PRESETS.crushed_gravel.chips.0` | 2 |  |  | [shape](#shape) |
| `PRESETS.crushed_gravel.chips.1` | 6 |  |  | [shape](#shape) |
| `PRESETS.crushed_gravel.chip_depth.0` | 0.55 |  |  | [shape](#shape) |
| `PRESETS.crushed_gravel.chip_depth.1` | 0.85 |  |  | [shape](#shape) |
| `PRESETS.marble_chips.phi_mean` | -3.5 | phi | -4 to -3 | [wentworth](#wentworth) |
| `PRESETS.marble_chips.phi_std` | 0.3 | phi |  | [size](#size) |
| `PRESETS.marble_chips.density` | 2700 | kg/m³ | 2560 to 2760 | [rocks](#rocks) |
| `PRESETS.marble_chips.friction` | 0.6 |  |  | [friction](#friction) |
| `PRESETS.marble_chips.restitution` | 0.15 |  |  | [restitution](#restitution) |
| `PRESETS.marble_chips.absorption` | 0.003 |  |  | [absorption](#absorption) |
| `PRESETS.marble_chips.elongation_beta.0` | 6 |  |  | [shape](#shape) |
| `PRESETS.marble_chips.elongation_beta.1` | 3 |  |  | [shape](#shape) |
| `PRESETS.marble_chips.flatness_beta.0` | 5 |  |  | [shape](#shape) |
| `PRESETS.marble_chips.flatness_beta.1` | 3 |  |  | [shape](#shape) |
| `PRESETS.marble_chips.facets.0` | 8 |  |  | [shape](#shape) |
| `PRESETS.marble_chips.facets.1` | 16 |  |  | [shape](#shape) |
| `PRESETS.marble_chips.roundness_p.0` | 10 |  |  | [shape](#shape) |
| `PRESETS.marble_chips.roundness_p.1` | 25 |  |  | [shape](#shape) |
| `PRESETS.marble_chips.roughness` | 0 |  |  | [shape](#shape) |
| `PRESETS.marble_chips.lumpiness.0` | 0 |  |  | [shape](#shape) |
| `PRESETS.marble_chips.lumpiness.1` | 0.03 |  |  | [shape](#shape) |
| `PRESETS.marble_chips.chips.0` | 2 |  |  | [shape](#shape) |
| `PRESETS.marble_chips.chips.1` | 5 |  |  | [shape](#shape) |
| `PRESETS.marble_chips.chip_depth.0` | 0.6 |  |  | [shape](#shape) |
| `PRESETS.marble_chips.chip_depth.1` | 0.85 |  |  | [shape](#shape) |
| `PRESETS.pozzolana.phi_mean` | -3.5 | phi |  | [size](#size) |
| `PRESETS.pozzolana.phi_std` | 0.4 | phi |  | [size](#size) |
| `PRESETS.pozzolana.density` | 1400 | kg/m³ |  | [density](#density) |
| `PRESETS.pozzolana.friction` | 0.75 |  |  | [friction](#friction) |
| `PRESETS.pozzolana.restitution` | 0.1 |  |  | [restitution](#restitution) |
| `PRESETS.pozzolana.absorption` | 0.2 |  |  | [absorption](#absorption) |
| `PRESETS.pozzolana.elongation_beta.0` | 6 |  |  | [shape](#shape) |
| `PRESETS.pozzolana.elongation_beta.1` | 3 |  |  | [shape](#shape) |
| `PRESETS.pozzolana.flatness_beta.0` | 6 |  |  | [shape](#shape) |
| `PRESETS.pozzolana.flatness_beta.1` | 3 |  |  | [shape](#shape) |
| `PRESETS.pozzolana.facets.0` | 10 |  |  | [shape](#shape) |
| `PRESETS.pozzolana.facets.1` | 22 |  |  | [shape](#shape) |
| `PRESETS.pozzolana.roundness_p.0` | 5 |  |  | [shape](#shape) |
| `PRESETS.pozzolana.roundness_p.1` | 12 |  |  | [shape](#shape) |
| `PRESETS.pozzolana.roughness` | 0.02 |  |  | [shape](#shape) |
| `PRESETS.pozzolana.lumpiness.0` | 0.08 |  |  | [shape](#shape) |
| `PRESETS.pozzolana.lumpiness.1` | 0.18 |  |  | [shape](#shape) |
| `PRESETS.pozzolana.chips.0` | 0 |  |  | [shape](#shape) |
| `PRESETS.pozzolana.chips.1` | 2 |  |  | [shape](#shape) |
| `PRESETS.pozzolana.chip_depth.0` | 0.65 |  |  | [shape](#shape) |
| `PRESETS.pozzolana.chip_depth.1` | 0.85 |  |  | [shape](#shape) |
| `PRESETS.pozzolana.pits.0` | 4 |  |  | [shape](#shape) |
| `PRESETS.pozzolana.pits.1` | 10 |  |  | [shape](#shape) |
| `PRESETS.pozzolana.pit_depth.0` | 0.08 |  |  | [shape](#shape) |
| `PRESETS.pozzolana.pit_depth.1` | 0.22 |  |  | [shape](#shape) |
| `PRESETS.pozzolana.pit_size.0` | 0.2 |  |  | [shape](#shape) |
| `PRESETS.pozzolana.pit_size.1` | 0.4 |  |  | [shape](#shape) |
| `PRESETS.river_pebbles.phi_mean` | -5.5 | phi | -6 to -5 | [wentworth](#wentworth) |
| `PRESETS.river_pebbles.phi_std` | 0.5 | phi |  | [size](#size) |
| `PRESETS.river_pebbles.density` | 2650 | kg/m³ | 2650 to 2650 | [quartz](#quartz) |
| `PRESETS.river_pebbles.friction` | 0.5 |  |  | [friction](#friction) |
| `PRESETS.river_pebbles.restitution` | 0.2 |  |  | [restitution](#restitution) |
| `PRESETS.river_pebbles.absorption` | 0.006 |  |  | [absorption](#absorption) |
| `PRESETS.river_pebbles.elongation_beta.0` | 7 |  |  | [shape](#shape) |
| `PRESETS.river_pebbles.elongation_beta.1` | 2.5 |  |  | [shape](#shape) |
| `PRESETS.river_pebbles.flatness_beta.0` | 6 |  |  | [shape](#shape) |
| `PRESETS.river_pebbles.flatness_beta.1` | 2.5 |  |  | [shape](#shape) |
| `PRESETS.river_pebbles.facets.0` | 24 |  |  | [shape](#shape) |
| `PRESETS.river_pebbles.facets.1` | 40 |  |  | [shape](#shape) |
| `PRESETS.river_pebbles.roundness_p.0` | 1.3 |  |  | [shape](#shape) |
| `PRESETS.river_pebbles.roundness_p.1` | 2 |  |  | [shape](#shape) |
| `PRESETS.river_pebbles.roughness` | 0.004 |  |  | [shape](#shape) |
| `PRESETS.river_pebbles.lumpiness.0` | 0.02 |  |  | [shape](#shape) |
| `PRESETS.river_pebbles.lumpiness.1` | 0.07 |  |  | [shape](#shape) |
| `PRESETS.river_pebbles.taper` | 0.15 |  |  | [shape](#shape) |
| `PRESETS.beach_pebbles.phi_mean` | -5.3 | phi | -6 to -5 | [wentworth](#wentworth) |
| `PRESETS.beach_pebbles.phi_std` | 0.4 | phi |  | [size](#size) |
| `PRESETS.beach_pebbles.density` | 2850 | kg/m³ | 2700 to 3000 | [rocks](#rocks) |
| `PRESETS.beach_pebbles.friction` | 0.4 |  |  | [friction](#friction) |
| `PRESETS.beach_pebbles.restitution` | 0.25 |  |  | [restitution](#restitution) |
| `PRESETS.beach_pebbles.absorption` | 0.002 |  |  | [absorption](#absorption) |
| `PRESETS.beach_pebbles.elongation_beta.0` | 5 |  |  | [shape](#shape) |
| `PRESETS.beach_pebbles.elongation_beta.1` | 2.5 |  |  | [shape](#shape) |
| `PRESETS.beach_pebbles.flatness_beta.0` | 2.5 |  |  | [shape](#shape) |
| `PRESETS.beach_pebbles.flatness_beta.1` | 4 |  |  | [shape](#shape) |
| `PRESETS.beach_pebbles.flatness_min` | 0.22 |  |  | [shape](#shape) |
| `PRESETS.beach_pebbles.facets.0` | 24 |  |  | [shape](#shape) |
| `PRESETS.beach_pebbles.facets.1` | 40 |  |  | [shape](#shape) |
| `PRESETS.beach_pebbles.roundness_p.0` | 1.3 |  |  | [shape](#shape) |
| `PRESETS.beach_pebbles.roundness_p.1` | 2 |  |  | [shape](#shape) |
| `PRESETS.beach_pebbles.roughness` | 0.002 |  |  | [shape](#shape) |
| `PRESETS.beach_pebbles.lumpiness.0` | 0.02 |  |  | [shape](#shape) |
| `PRESETS.beach_pebbles.lumpiness.1` | 0.06 |  |  | [shape](#shape) |
| `PRESETS.beach_pebbles.taper` | 0.15 |  |  | [shape](#shape) |
| `PRESETS.railway_ballast.phi_mean` | -5.3 | phi | -5.977 to -4.977 | [en13450](#en13450) |
| `PRESETS.railway_ballast.phi_std` | 0.2 | phi |  | [size](#size) |
| `PRESETS.railway_ballast.density` | 2750 | kg/m³ | 2000 to 2800 | [en13450](#en13450) |
| `PRESETS.railway_ballast.friction` | 0.7 |  |  | [friction](#friction) |
| `PRESETS.railway_ballast.restitution` | 0.15 |  |  | [restitution](#restitution) |
| `PRESETS.railway_ballast.absorption` | 0.004 |  | to 0.035 | [en13450](#en13450) |
| `PRESETS.railway_ballast.elongation_beta.0` | 5 |  |  | [shape](#shape) |
| `PRESETS.railway_ballast.elongation_beta.1` | 3 |  |  | [shape](#shape) |
| `PRESETS.railway_ballast.flatness_beta.0` | 5 |  |  | [shape](#shape) |
| `PRESETS.railway_ballast.flatness_beta.1` | 3 |  |  | [shape](#shape) |
| `PRESETS.railway_ballast.facets.0` | 6 |  |  | [shape](#shape) |
| `PRESETS.railway_ballast.facets.1` | 12 |  |  | [shape](#shape) |
| `PRESETS.railway_ballast.roundness_p.0` | 25 |  |  | [shape](#shape) |
| `PRESETS.railway_ballast.roundness_p.1` | 60 |  |  | [shape](#shape) |
| `PRESETS.railway_ballast.roughness` | 0 |  |  | [shape](#shape) |
| `PRESETS.railway_ballast.lumpiness.0` | 0 |  |  | [shape](#shape) |
| `PRESETS.railway_ballast.lumpiness.1` | 0.03 |  |  | [shape](#shape) |
| `PRESETS.railway_ballast.chips.0` | 3 |  |  | [shape](#shape) |
| `PRESETS.railway_ballast.chips.1` | 7 |  |  | [shape](#shape) |
| `PRESETS.railway_ballast.chip_depth.0` | 0.55 |  |  | [shape](#shape) |
| `PRESETS.railway_ballast.chip_depth.1` | 0.8 |  |  | [shape](#shape) |
| `PRESETS.iron_ore.phi_mean` | -4 | phi |  | [size](#size) |
| `PRESETS.iron_ore.phi_std` | 0.5 | phi |  | [size](#size) |
| `PRESETS.iron_ore.density` | 4500 | kg/m³ |  | [density](#density) |
| `PRESETS.iron_ore.friction` | 0.7 |  |  | [friction](#friction) |
| `PRESETS.iron_ore.restitution` | 0.12 |  |  | [restitution](#restitution) |
| `PRESETS.iron_ore.absorption` | 0.01 |  |  | [absorption](#absorption) |
| `PRESETS.iron_ore.elongation_beta.0` | 5 |  |  | [shape](#shape) |
| `PRESETS.iron_ore.elongation_beta.1` | 3 |  |  | [shape](#shape) |
| `PRESETS.iron_ore.flatness_beta.0` | 5 |  |  | [shape](#shape) |
| `PRESETS.iron_ore.flatness_beta.1` | 3 |  |  | [shape](#shape) |
| `PRESETS.iron_ore.facets.0` | 6 |  |  | [shape](#shape) |
| `PRESETS.iron_ore.facets.1` | 12 |  |  | [shape](#shape) |
| `PRESETS.iron_ore.roundness_p.0` | 20 |  |  | [shape](#shape) |
| `PRESETS.iron_ore.roundness_p.1` | 50 |  |  | [shape](#shape) |
| `PRESETS.iron_ore.roughness` | 0 |  |  | [shape](#shape) |
| `PRESETS.iron_ore.lumpiness.0` | 0.02 |  |  | [shape](#shape) |
| `PRESETS.iron_ore.lumpiness.1` | 0.08 |  |  | [shape](#shape) |
| `PRESETS.iron_ore.chips.0` | 2 |  |  | [shape](#shape) |
| `PRESETS.iron_ore.chips.1` | 6 |  |  | [shape](#shape) |
| `PRESETS.iron_ore.chip_depth.0` | 0.5 |  |  | [shape](#shape) |
| `PRESETS.iron_ore.chip_depth.1` | 0.85 |  |  | [shape](#shape) |
| `PRESETS.iron_ore.pits.0` | 0 |  |  | [shape](#shape) |
| `PRESETS.iron_ore.pits.1` | 3 |  |  | [shape](#shape) |
| `PRESETS.iron_ore.pit_depth.0` | 0.05 |  |  | [shape](#shape) |
| `PRESETS.iron_ore.pit_depth.1` | 0.12 |  |  | [shape](#shape) |
| `PRESETS.iron_ore.pit_size.0` | 0.15 |  |  | [shape](#shape) |
| `PRESETS.iron_ore.pit_size.1` | 0.3 |  |  | [shape](#shape) |
| `PRESETS.coal.phi_mean` | -4.5 | phi |  | [size](#size) |
| `PRESETS.coal.phi_std` | 0.5 | phi |  | [size](#size) |
| `PRESETS.coal.density` | 1350 | kg/m³ |  | [density](#density) |
| `PRESETS.coal.friction` | 0.55 |  |  | [friction](#friction) |
| `PRESETS.coal.restitution` | 0.1 |  |  | [restitution](#restitution) |
| `PRESETS.coal.absorption` | 0.05 |  |  | [absorption](#absorption) |
| `PRESETS.coal.elongation_beta.0` | 5 |  |  | [shape](#shape) |
| `PRESETS.coal.elongation_beta.1` | 3 |  |  | [shape](#shape) |
| `PRESETS.coal.flatness_beta.0` | 4 |  |  | [shape](#shape) |
| `PRESETS.coal.flatness_beta.1` | 3 |  |  | [shape](#shape) |
| `PRESETS.coal.facets.0` | 6 |  |  | [shape](#shape) |
| `PRESETS.coal.facets.1` | 12 |  |  | [shape](#shape) |
| `PRESETS.coal.roundness_p.0` | 20 |  |  | [shape](#shape) |
| `PRESETS.coal.roundness_p.1` | 50 |  |  | [shape](#shape) |
| `PRESETS.coal.roughness` | 0 |  |  | [shape](#shape) |
| `PRESETS.coal.lumpiness.0` | 0 |  |  | [shape](#shape) |
| `PRESETS.coal.lumpiness.1` | 0.03 |  |  | [shape](#shape) |
| `PRESETS.coal.chips.0` | 2 |  |  | [shape](#shape) |
| `PRESETS.coal.chips.1` | 5 |  |  | [shape](#shape) |
| `PRESETS.coal.chip_depth.0` | 0.5 |  |  | [shape](#shape) |
| `PRESETS.coal.chip_depth.1` | 0.8 |  |  | [shape](#shape) |
| `PRESETS.rubber_mulch.phi_mean` | -4.3 | phi |  | [size](#size) |
| `PRESETS.rubber_mulch.phi_std` | 0.35 | phi |  | [size](#size) |
| `PRESETS.rubber_mulch.density` | 1150 | kg/m³ | 1100 to 1200 | [plastics](#plastics) |
| `PRESETS.rubber_mulch.friction` | 0.85 |  |  | [friction](#friction) |
| `PRESETS.rubber_mulch.restitution` | 0.55 |  |  | [restitution](#restitution) |
| `PRESETS.rubber_mulch.absorption` | 0 |  |  | [absorption](#absorption) |
| `PRESETS.rubber_mulch.elongation_beta.0` | 4 |  |  | [shape](#shape) |
| `PRESETS.rubber_mulch.elongation_beta.1` | 3 |  |  | [shape](#shape) |
| `PRESETS.rubber_mulch.flatness_beta.0` | 4 |  |  | [shape](#shape) |
| `PRESETS.rubber_mulch.flatness_beta.1` | 3 |  |  | [shape](#shape) |
| `PRESETS.rubber_mulch.flatness_min` | 0.35 |  |  | [shape](#shape) |
| `PRESETS.rubber_mulch.facets.0` | 7 |  |  | [shape](#shape) |
| `PRESETS.rubber_mulch.facets.1` | 13 |  |  | [shape](#shape) |
| `PRESETS.rubber_mulch.roundness_p.0` | 5 |  |  | [shape](#shape) |
| `PRESETS.rubber_mulch.roundness_p.1` | 12 |  |  | [shape](#shape) |
| `PRESETS.rubber_mulch.roughness` | 0.02 |  |  | [shape](#shape) |
| `PRESETS.rubber_mulch.lumpiness.0` | 0.08 |  |  | [shape](#shape) |
| `PRESETS.rubber_mulch.lumpiness.1` | 0.2 |  |  | [shape](#shape) |
| `PRESETS.rubber_mulch.taper` | 0.2 |  |  | [shape](#shape) |
| `PRESETS.rubber_mulch.chips.0` | 2 |  |  | [shape](#shape) |
| `PRESETS.rubber_mulch.chips.1` | 4 |  |  | [shape](#shape) |
| `PRESETS.rubber_mulch.chip_depth.0` | 0.55 |  |  | [shape](#shape) |
| `PRESETS.rubber_mulch.chip_depth.1` | 0.85 |  |  | [shape](#shape) |
| `PRESETS.wheat.phi_mean` | -2 | phi |  | [size](#size) |
| `PRESETS.wheat.phi_std` | 0.15 | phi |  | [size](#size) |
| `PRESETS.wheat.density` | 1250 | kg/m³ | 1177 to 1333 | [grains](#grains) |
| `PRESETS.wheat.friction` | 0.44 |  | 0.41 to 0.62 | [grains](#grains) |
| `PRESETS.wheat.restitution` | 0.4 |  |  | [restitution](#restitution) |
| `PRESETS.wheat.absorption` | 0.3 |  |  | [absorption](#absorption) |
| `PRESETS.wheat.elongation_beta.0` | 10 |  |  | [shape](#shape) |
| `PRESETS.wheat.elongation_beta.1` | 10 |  |  | [shape](#shape) |
| `PRESETS.wheat.flatness_beta.0` | 18 |  |  | [shape](#shape) |
| `PRESETS.wheat.flatness_beta.1` | 2 |  |  | [shape](#shape) |
| `PRESETS.wheat.facets.0` | 4 |  |  | [shape](#shape) |
| `PRESETS.wheat.facets.1` | 4 |  |  | [shape](#shape) |
| `PRESETS.wheat.roundness_p.0` | 1 |  |  | [shape](#shape) |
| `PRESETS.wheat.roundness_p.1` | 1 |  |  | [shape](#shape) |
| `PRESETS.wheat.roughness` | 0 |  |  | [shape](#shape) |
| `PRESETS.wheat.lumpiness.0` | 0 |  |  | [shape](#shape) |
| `PRESETS.wheat.lumpiness.1` | 0.03 |  |  | [shape](#shape) |
| `PRESETS.wheat.taper.0` | 0.1 |  |  | [shape](#shape) |
| `PRESETS.wheat.taper.1` | 0.2 |  |  | [shape](#shape) |
| `PRESETS.wheat.exponent` | 2 |  |  | [shape](#shape) |
| `PRESETS.wheat.crease.0` | 0.12 |  |  | [shape](#shape) |
| `PRESETS.wheat.crease.1` | 0.12 |  |  | [shape](#shape) |
| `PRESETS.maize.phi_mean` | -2.87 | phi |  | [size](#size) |
| `PRESETS.maize.phi_std` | 0.15 | phi |  | [size](#size) |
| `PRESETS.maize.density` | 1280 | kg/m³ | 1110 to 1290 | [grains](#grains) |
| `PRESETS.maize.friction` | 0.45 |  |  | [friction](#friction) |
| `PRESETS.maize.restitution` | 0.35 |  |  | [restitution](#restitution) |
| `PRESETS.maize.absorption` | 0.3 |  |  | [absorption](#absorption) |
| `PRESETS.maize.elongation_beta.0` | 14 |  |  | [shape](#shape) |
| `PRESETS.maize.elongation_beta.1` | 5 |  |  | [shape](#shape) |
| `PRESETS.maize.flatness_beta.0` | 11 |  |  | [shape](#shape) |
| `PRESETS.maize.flatness_beta.1` | 9 |  |  | [shape](#shape) |
| `PRESETS.maize.flatness_min` | 0.35 |  |  | [shape](#shape) |
| `PRESETS.maize.facets.0` | 4 |  |  | [shape](#shape) |
| `PRESETS.maize.facets.1` | 4 |  |  | [shape](#shape) |
| `PRESETS.maize.roundness_p.0` | 1 |  |  | [shape](#shape) |
| `PRESETS.maize.roundness_p.1` | 1 |  |  | [shape](#shape) |
| `PRESETS.maize.roughness` | 0 |  |  | [shape](#shape) |
| `PRESETS.maize.lumpiness.0` | 0 |  |  | [shape](#shape) |
| `PRESETS.maize.lumpiness.1` | 0.04 |  |  | [shape](#shape) |
| `PRESETS.maize.taper.0` | -0.5 |  |  | [shape](#shape) |
| `PRESETS.maize.taper.1` | -0.4 |  |  | [shape](#shape) |
| `PRESETS.maize.exponent` | 2.8 |  |  | [shape](#shape) |
| `PRESETS.maize.dent.0` | 0.05 |  |  | [shape](#shape) |
| `PRESETS.maize.dent.1` | 0.12 |  |  | [shape](#shape) |
| `PRESETS.maize.dent.2` | 0.35 |  |  | [shape](#shape) |
| `PRESETS.rice.phi_mean` | -1.49 | phi |  | [size](#size) |
| `PRESETS.rice.phi_std` | 0.1 | phi |  | [size](#size) |
| `PRESETS.rice.density` | 1450 | kg/m³ |  | [density](#density) |
| `PRESETS.rice.friction` | 0.4 |  |  | [friction](#friction) |
| `PRESETS.rice.restitution` | 0.3 |  |  | [restitution](#restitution) |
| `PRESETS.rice.absorption` | 0.25 |  |  | [absorption](#absorption) |
| `PRESETS.rice.elongation_beta.0` | 12 |  |  | [shape](#shape) |
| `PRESETS.rice.elongation_beta.1` | 28 |  |  | [shape](#shape) |
| `PRESETS.rice.flatness_beta.0` | 16 |  |  | [shape](#shape) |
| `PRESETS.rice.flatness_beta.1` | 4 |  |  | [shape](#shape) |
| `PRESETS.rice.elongation_min` | 0.2 |  |  | [shape](#shape) |
| `PRESETS.rice.facets.0` | 4 |  |  | [shape](#shape) |
| `PRESETS.rice.facets.1` | 4 |  |  | [shape](#shape) |
| `PRESETS.rice.roundness_p.0` | 1 |  |  | [shape](#shape) |
| `PRESETS.rice.roundness_p.1` | 1 |  |  | [shape](#shape) |
| `PRESETS.rice.roughness` | 0 |  |  | [shape](#shape) |
| `PRESETS.rice.taper.0` | 0.05 |  |  | [shape](#shape) |
| `PRESETS.rice.taper.1` | 0.15 |  |  | [shape](#shape) |
| `PRESETS.rice.exponent` | 2.2 |  |  | [shape](#shape) |
| `PRESETS.rice.dent.0` | 0.02 |  |  | [shape](#shape) |
| `PRESETS.rice.dent.1` | 0.06 |  |  | [shape](#shape) |
| `PRESETS.rice.dent.2` | 0.25 |  |  | [shape](#shape) |
| `PRESETS.beans.phi_mean` | -3.16 | phi |  | [size](#size) |
| `PRESETS.beans.phi_std` | 0.15 | phi |  | [size](#size) |
| `PRESETS.beans.density` | 1300 | kg/m³ |  | [density](#density) |
| `PRESETS.beans.friction` | 0.35 |  |  | [friction](#friction) |
| `PRESETS.beans.restitution` | 0.4 |  |  | [restitution](#restitution) |
| `PRESETS.beans.absorption` | 0.9 |  |  | [absorption](#absorption) |
| `PRESETS.beans.elongation_beta.0` | 11 |  |  | [shape](#shape) |
| `PRESETS.beans.elongation_beta.1` | 9 |  |  | [shape](#shape) |
| `PRESETS.beans.flatness_beta.0` | 15 |  |  | [shape](#shape) |
| `PRESETS.beans.flatness_beta.1` | 5 |  |  | [shape](#shape) |
| `PRESETS.beans.facets.0` | 4 |  |  | [shape](#shape) |
| `PRESETS.beans.facets.1` | 4 |  |  | [shape](#shape) |
| `PRESETS.beans.roundness_p.0` | 1 |  |  | [shape](#shape) |
| `PRESETS.beans.roundness_p.1` | 1 |  |  | [shape](#shape) |
| `PRESETS.beans.roughness` | 0 |  |  | [shape](#shape) |
| `PRESETS.beans.lumpiness.0` | 0 |  |  | [shape](#shape) |
| `PRESETS.beans.lumpiness.1` | 0.02 |  |  | [shape](#shape) |
| `PRESETS.beans.exponent` | 2.2 |  |  | [shape](#shape) |
| `PRESETS.beans.bend.0` | 0.6 |  |  | [shape](#shape) |
| `PRESETS.beans.bend.1` | 0.85 |  |  | [shape](#shape) |
| `PRESETS.beans.dent.0` | 0.03 |  |  | [shape](#shape) |
| `PRESETS.beans.dent.1` | 0.06 |  |  | [shape](#shape) |
| `PRESETS.beans.dent.2` | 0.18 |  |  | [shape](#shape) |
| `PRESETS.soybean.phi_mean` | -2.7 | phi |  | [size](#size) |
| `PRESETS.soybean.phi_std` | 0.15 | phi |  | [size](#size) |
| `PRESETS.soybean.density` | 1200 | kg/m³ |  | [density](#density) |
| `PRESETS.soybean.friction` | 0.35 |  |  | [friction](#friction) |
| `PRESETS.soybean.restitution` | 0.45 |  |  | [restitution](#restitution) |
| `PRESETS.soybean.absorption` | 0.4 |  |  | [absorption](#absorption) |
| `PRESETS.soybean.elongation_beta.0` | 18 |  |  | [shape](#shape) |
| `PRESETS.soybean.elongation_beta.1` | 3 |  |  | [shape](#shape) |
| `PRESETS.soybean.flatness_beta.0` | 18 |  |  | [shape](#shape) |
| `PRESETS.soybean.flatness_beta.1` | 3 |  |  | [shape](#shape) |
| `PRESETS.soybean.facets.0` | 4 |  |  | [shape](#shape) |
| `PRESETS.soybean.facets.1` | 4 |  |  | [shape](#shape) |
| `PRESETS.soybean.roundness_p.0` | 1 |  |  | [shape](#shape) |
| `PRESETS.soybean.roundness_p.1` | 1 |  |  | [shape](#shape) |
| `PRESETS.soybean.roughness` | 0 |  |  | [shape](#shape) |
| `PRESETS.soybean.lumpiness.0` | 0 |  |  | [shape](#shape) |
| `PRESETS.soybean.lumpiness.1` | 0.02 |  |  | [shape](#shape) |
| `PRESETS.soybean.exponent` | 2 |  |  | [shape](#shape) |
| `PRESETS.soybean.dent.0` | 0.02 |  |  | [shape](#shape) |
| `PRESETS.soybean.dent.1` | 0.05 |  |  | [shape](#shape) |
| `PRESETS.soybean.dent.2` | 0.15 |  |  | [shape](#shape) |
| `PRESETS.cherry_tomatoes.phi_mean` | -4.6 | phi |  | [size](#size) |
| `PRESETS.cherry_tomatoes.phi_std` | 0.18 | phi |  | [size](#size) |
| `PRESETS.cherry_tomatoes.density` | 1000 | kg/m³ |  | [density](#density) |
| `PRESETS.cherry_tomatoes.friction` | 0.45 |  |  | [friction](#friction) |
| `PRESETS.cherry_tomatoes.restitution` | 0.2 |  |  | [restitution](#restitution) |
| `PRESETS.cherry_tomatoes.absorption` | 0 |  |  | [absorption](#absorption) |
| `PRESETS.cherry_tomatoes.elongation_beta.0` | 30 |  |  | [shape](#shape) |
| `PRESETS.cherry_tomatoes.elongation_beta.1` | 2 |  |  | [shape](#shape) |
| `PRESETS.cherry_tomatoes.flatness_beta.0` | 12 |  |  | [shape](#shape) |
| `PRESETS.cherry_tomatoes.flatness_beta.1` | 2 |  |  | [shape](#shape) |
| `PRESETS.cherry_tomatoes.facets.0` | 4 |  |  | [shape](#shape) |
| `PRESETS.cherry_tomatoes.facets.1` | 4 |  |  | [shape](#shape) |
| `PRESETS.cherry_tomatoes.roundness_p.0` | 1 |  |  | [shape](#shape) |
| `PRESETS.cherry_tomatoes.roundness_p.1` | 1 |  |  | [shape](#shape) |
| `PRESETS.cherry_tomatoes.roughness` | 0 |  |  | [shape](#shape) |
| `PRESETS.cherry_tomatoes.lumpiness.0` | 0 |  |  | [shape](#shape) |
| `PRESETS.cherry_tomatoes.lumpiness.1` | 0.025 |  |  | [shape](#shape) |
| `PRESETS.cherry_tomatoes.exponent` | 2 |  |  | [shape](#shape) |
| `PRESETS.cherry_tomatoes.dent.0` | 0.05 |  |  | [shape](#shape) |
| `PRESETS.cherry_tomatoes.dent.1` | 0.09 |  |  | [shape](#shape) |
| `PRESETS.cherry_tomatoes.dent.2` | 0.16 |  |  | [shape](#shape) |
| `PRESETS.cherry_tomatoes.deformable.youngs_modulus` | 500000 |  |  | [soft](#soft) |
| `PRESETS.cherry_tomatoes.deformable.poissons_ratio` | 0.45 |  |  | [soft](#soft) |
| `PRESETS.cherry_tomatoes.deformable.elasticity_damping` | 0.01 |  |  | [soft](#soft) |
| `PRESETS.plastic_pellets.phi_mean` | -1.77 | phi |  | [size](#size) |
| `PRESETS.plastic_pellets.phi_std` | 0.08 | phi |  | [size](#size) |
| `PRESETS.plastic_pellets.density` | 950 | kg/m³ | 900 to 960 | [plastics](#plastics) |
| `PRESETS.plastic_pellets.friction` | 0.3 |  |  | [friction](#friction) |
| `PRESETS.plastic_pellets.restitution` | 0.5 |  |  | [restitution](#restitution) |
| `PRESETS.plastic_pellets.absorption` | 0 |  |  | [absorption](#absorption) |
| `PRESETS.plastic_pellets.elongation_beta.0` | 1 |  |  | [shape](#shape) |
| `PRESETS.plastic_pellets.elongation_beta.1` | 1 |  |  | [shape](#shape) |
| `PRESETS.plastic_pellets.flatness_beta.0` | 30 |  |  | [shape](#shape) |
| `PRESETS.plastic_pellets.flatness_beta.1` | 2 |  |  | [shape](#shape) |
| `PRESETS.plastic_pellets.facets.0` | 4 |  |  | [shape](#shape) |
| `PRESETS.plastic_pellets.facets.1` | 4 |  |  | [shape](#shape) |
| `PRESETS.plastic_pellets.roundness_p.0` | 1 |  |  | [shape](#shape) |
| `PRESETS.plastic_pellets.roundness_p.1` | 1 |  |  | [shape](#shape) |
| `PRESETS.plastic_pellets.roughness` | 0 |  |  | [shape](#shape) |
| `PRESETS.plastic_pellets.exponent` | 8 |  |  | [shape](#shape) |
| `PRESETS.plastic_pellets.aspect.0` | 0.75 |  |  | [shape](#shape) |
| `PRESETS.plastic_pellets.aspect.1` | 1.1 |  |  | [shape](#shape) |
| `PRESETS.wood_pellets.phi_mean` | -3.3 | phi |  | [size](#size) |
| `PRESETS.wood_pellets.phi_std` | 0.25 | phi |  | [size](#size) |
| `PRESETS.wood_pellets.density` | 1150 | kg/m³ |  | [density](#density) |
| `PRESETS.wood_pellets.friction` | 0.5 |  |  | [friction](#friction) |
| `PRESETS.wood_pellets.restitution` | 0.2 |  |  | [restitution](#restitution) |
| `PRESETS.wood_pellets.absorption` | 0.5 |  |  | [absorption](#absorption) |
| `PRESETS.wood_pellets.elongation_beta.0` | 1 |  |  | [shape](#shape) |
| `PRESETS.wood_pellets.elongation_beta.1` | 1 |  |  | [shape](#shape) |
| `PRESETS.wood_pellets.flatness_beta.0` | 30 |  |  | [shape](#shape) |
| `PRESETS.wood_pellets.flatness_beta.1` | 2 |  |  | [shape](#shape) |
| `PRESETS.wood_pellets.facets.0` | 4 |  |  | [shape](#shape) |
| `PRESETS.wood_pellets.facets.1` | 4 |  |  | [shape](#shape) |
| `PRESETS.wood_pellets.roundness_p.0` | 1 |  |  | [shape](#shape) |
| `PRESETS.wood_pellets.roundness_p.1` | 1 |  |  | [shape](#shape) |
| `PRESETS.wood_pellets.roughness` | 0.015 |  |  | [shape](#shape) |
| `PRESETS.wood_pellets.lumpiness.0` | 0 |  |  | [shape](#shape) |
| `PRESETS.wood_pellets.lumpiness.1` | 0.02 |  |  | [shape](#shape) |
| `PRESETS.wood_pellets.chips.0` | 1 |  |  | [shape](#shape) |
| `PRESETS.wood_pellets.chips.1` | 2 |  |  | [shape](#shape) |
| `PRESETS.wood_pellets.chip_depth.0` | 0.75 |  |  | [shape](#shape) |
| `PRESETS.wood_pellets.chip_depth.1` | 0.95 |  |  | [shape](#shape) |
| `PRESETS.wood_pellets.exponent` | 12 |  |  | [shape](#shape) |
| `PRESETS.wood_pellets.aspect.0` | 0.2 |  |  | [shape](#shape) |
| `PRESETS.wood_pellets.aspect.1` | 0.5 |  |  | [shape](#shape) |
| `PRESETS.packing_peanuts.phi_mean` | -4.3 | phi |  | [size](#size) |
| `PRESETS.packing_peanuts.phi_std` | 0.12 | phi |  | [size](#size) |
| `PRESETS.packing_peanuts.density` | 12 | kg/m³ |  | [density](#density) |
| `PRESETS.packing_peanuts.friction` | 0.5 |  |  | [friction](#friction) |
| `PRESETS.packing_peanuts.restitution` | 0.3 |  |  | [restitution](#restitution) |
| `PRESETS.packing_peanuts.absorption` | 0 |  |  | [absorption](#absorption) |
| `PRESETS.packing_peanuts.elongation_beta.0` | 1 |  |  | [shape](#shape) |
| `PRESETS.packing_peanuts.elongation_beta.1` | 1 |  |  | [shape](#shape) |
| `PRESETS.packing_peanuts.flatness_beta.0` | 14 |  |  | [shape](#shape) |
| `PRESETS.packing_peanuts.flatness_beta.1` | 4 |  |  | [shape](#shape) |
| `PRESETS.packing_peanuts.facets.0` | 4 |  |  | [shape](#shape) |
| `PRESETS.packing_peanuts.facets.1` | 4 |  |  | [shape](#shape) |
| `PRESETS.packing_peanuts.roundness_p.0` | 1 |  |  | [shape](#shape) |
| `PRESETS.packing_peanuts.roundness_p.1` | 1 |  |  | [shape](#shape) |
| `PRESETS.packing_peanuts.roughness` | 0.01 |  |  | [shape](#shape) |
| `PRESETS.packing_peanuts.lumpiness.0` | 0 |  |  | [shape](#shape) |
| `PRESETS.packing_peanuts.lumpiness.1` | 0.03 |  |  | [shape](#shape) |
| `PRESETS.packing_peanuts.aspect.0` | 0.32 |  |  | [shape](#shape) |
| `PRESETS.packing_peanuts.aspect.1` | 0.42 |  |  | [shape](#shape) |
| `PRESETS.packing_peanuts.curve_amplitude.0` | 0.3 |  |  | [shape](#shape) |
| `PRESETS.packing_peanuts.curve_amplitude.1` | 0.45 |  |  | [shape](#shape) |
| `PRESETS.packing_peanuts.deformable.youngs_modulus` | 1e+06 |  |  | [soft](#soft) |
| `PRESETS.packing_peanuts.deformable.poissons_ratio` | 0.1 |  |  | [soft](#soft) |
| `PRESETS.packing_peanuts.deformable.elasticity_damping` | 0.02 |  |  | [soft](#soft) |
| `PRESETS.lunar_regolith.phi_mean` | 3.8 | phi | 2.943 to 4.644 | [jsc1a](#jsc1a) |
| `PRESETS.lunar_regolith.phi_std` | 1.2 | phi | 1 to 2 | [folk](#folk) |
| `PRESETS.lunar_regolith.density` | 2920 | kg/m³ | 2900 to 2920 | [jsc1a](#jsc1a) |
| `PRESETS.lunar_regolith.friction` | 0.75 |  |  | [friction](#friction) |
| `PRESETS.lunar_regolith.restitution` | 0.05 |  |  | [restitution](#restitution) |
| `PRESETS.lunar_regolith.absorption` | 0 |  |  | [absorption](#absorption) |
| `PRESETS.lunar_regolith.elongation_beta.0` | 5 |  |  | [shape](#shape) |
| `PRESETS.lunar_regolith.elongation_beta.1` | 3 |  |  | [shape](#shape) |
| `PRESETS.lunar_regolith.flatness_beta.0` | 5 |  |  | [shape](#shape) |
| `PRESETS.lunar_regolith.flatness_beta.1` | 3 |  |  | [shape](#shape) |
| `PRESETS.lunar_regolith.facets.0` | 6 |  |  | [shape](#shape) |
| `PRESETS.lunar_regolith.facets.1` | 16 |  |  | [shape](#shape) |
| `PRESETS.lunar_regolith.roundness_p.0` | 10 |  |  | [shape](#shape) |
| `PRESETS.lunar_regolith.roundness_p.1` | 40 |  |  | [shape](#shape) |
| `PRESETS.lunar_regolith.roughness` | 0.01 |  |  | [shape](#shape) |
| `PRESETS.lunar_regolith.lumpiness.0` | 0.06 |  |  | [shape](#shape) |
| `PRESETS.lunar_regolith.lumpiness.1` | 0.18 |  |  | [shape](#shape) |
| `PRESETS.lunar_regolith.chips.0` | 2 |  |  | [shape](#shape) |
| `PRESETS.lunar_regolith.chips.1` | 6 |  |  | [shape](#shape) |
| `PRESETS.lunar_regolith.chip_depth.0` | 0.5 |  |  | [shape](#shape) |
| `PRESETS.lunar_regolith.chip_depth.1` | 0.85 |  |  | [shape](#shape) |
| `PRESETS.lunar_regolith.pits.0` | 1 |  |  | [shape](#shape) |
| `PRESETS.lunar_regolith.pits.1` | 5 |  |  | [shape](#shape) |
| `PRESETS.lunar_regolith.pit_depth.0` | 0.1 |  |  | [shape](#shape) |
| `PRESETS.lunar_regolith.pit_depth.1` | 0.25 |  |  | [shape](#shape) |
| `PRESETS.lunar_regolith.pit_size.0` | 0.2 |  |  | [shape](#shape) |
| `PRESETS.lunar_regolith.pit_size.1` | 0.4 |  |  | [shape](#shape) |
| `PRESETS.martian_regolith.phi_mean` | 3 | phi |  | [size](#size) |
| `PRESETS.martian_regolith.phi_std` | 1.3 | phi | 1 to 2 | [folk](#folk) |
| `PRESETS.martian_regolith.density` | 2900 | kg/m³ |  | [density](#density) |
| `PRESETS.martian_regolith.friction` | 0.7 |  |  | [friction](#friction) |
| `PRESETS.martian_regolith.restitution` | 0.05 |  |  | [restitution](#restitution) |
| `PRESETS.martian_regolith.absorption` | 0 |  |  | [absorption](#absorption) |
| `PRESETS.martian_regolith.elongation_beta.0` | 5 |  |  | [shape](#shape) |
| `PRESETS.martian_regolith.elongation_beta.1` | 3 |  |  | [shape](#shape) |
| `PRESETS.martian_regolith.flatness_beta.0` | 5 |  |  | [shape](#shape) |
| `PRESETS.martian_regolith.flatness_beta.1` | 3 |  |  | [shape](#shape) |
| `PRESETS.martian_regolith.facets.0` | 6 |  |  | [shape](#shape) |
| `PRESETS.martian_regolith.facets.1` | 18 |  |  | [shape](#shape) |
| `PRESETS.martian_regolith.roundness_p.0` | 8 |  |  | [shape](#shape) |
| `PRESETS.martian_regolith.roundness_p.1` | 30 |  |  | [shape](#shape) |
| `PRESETS.martian_regolith.roughness` | 0.01 |  |  | [shape](#shape) |
| `PRESETS.martian_regolith.lumpiness.0` | 0.05 |  |  | [shape](#shape) |
| `PRESETS.martian_regolith.lumpiness.1` | 0.14 |  |  | [shape](#shape) |
| `PRESETS.martian_regolith.chips.0` | 1 |  |  | [shape](#shape) |
| `PRESETS.martian_regolith.chips.1` | 4 |  |  | [shape](#shape) |
| `PRESETS.martian_regolith.chip_depth.0` | 0.55 |  |  | [shape](#shape) |
| `PRESETS.martian_regolith.chip_depth.1` | 0.85 |  |  | [shape](#shape) |
| `PRESETS.martian_regolith.pits.0` | 0 |  |  | [shape](#shape) |
| `PRESETS.martian_regolith.pits.1` | 3 |  |  | [shape](#shape) |
| `PRESETS.martian_regolith.pit_depth.0` | 0.08 |  |  | [shape](#shape) |
| `PRESETS.martian_regolith.pit_depth.1` | 0.2 |  |  | [shape](#shape) |
| `PRESETS.martian_regolith.pit_size.0` | 0.2 |  |  | [shape](#shape) |
| `PRESETS.martian_regolith.pit_size.1` | 0.4 |  |  | [shape](#shape) |
| `PRESETS.glass_beads.phi_mean` | 0 | phi |  | [size](#size) |
| `PRESETS.glass_beads.phi_std` | 0.1 | phi |  | [size](#size) |
| `PRESETS.glass_beads.density` | 2500 | kg/m³ | 2400 to 2700 | [plastics](#plastics) |
| `PRESETS.glass_beads.friction` | 0.4 |  | 0.4 to 0.4 | [interface_friction](#interface_friction) |
| `PRESETS.glass_beads.restitution` | 0.85 |  |  | [restitution](#restitution) |
| `PRESETS.glass_beads.absorption` | 0 |  |  | [absorption](#absorption) |
| `PRESETS.glass_beads.elongation_beta.0` | 1 |  |  | [shape](#shape) |
| `PRESETS.glass_beads.elongation_beta.1` | 1 |  |  | [shape](#shape) |
| `PRESETS.glass_beads.flatness_beta.0` | 1 |  |  | [shape](#shape) |
| `PRESETS.glass_beads.flatness_beta.1` | 1 |  |  | [shape](#shape) |
| `PRESETS.glass_beads.facets.0` | 4 |  |  | [shape](#shape) |
| `PRESETS.glass_beads.facets.1` | 4 |  |  | [shape](#shape) |
| `PRESETS.glass_beads.roundness_p.0` | 1 |  |  | [shape](#shape) |
| `PRESETS.glass_beads.roundness_p.1` | 1 |  |  | [shape](#shape) |
| `PRESETS.glass_beads.roughness` | 0 |  |  | [shape](#shape) |
| `moisture.POROSITY` | 0.38 |  | 0.36 to 0.4 | [moisture](#moisture) |
| `moisture.COHESION_REF_D` | 0.35 | mm |  | [moisture](#moisture) |
| `moisture.STATE_PARAMS.dry.film` | 0 |  |  | [moisture](#moisture) |
| `moisture.STATE_PARAMS.dry.sat` | 0 |  |  | [moisture](#moisture) |
| `moisture.STATE_PARAMS.dry.fill` | 0 |  |  | [moisture](#moisture) |
| `moisture.STATE_PARAMS.dry.mu` | 1 |  |  | [moisture](#moisture) |
| `moisture.STATE_PARAMS.dry.e` | 1 |  |  | [moisture](#moisture) |
| `moisture.STATE_PARAMS.dry.cohesion` | 0 |  |  | [moisture](#moisture) |
| `moisture.STATE_PARAMS.damp.film` | 5e-06 |  |  | [moisture](#moisture) |
| `moisture.STATE_PARAMS.damp.sat` | 0.3 |  |  | [moisture](#moisture) |
| `moisture.STATE_PARAMS.damp.fill` | 0.2 |  |  | [moisture](#moisture) |
| `moisture.STATE_PARAMS.damp.mu` | 1.1 |  |  | [moisture](#moisture) |
| `moisture.STATE_PARAMS.damp.e` | 0.6 |  |  | [moisture](#moisture) |
| `moisture.STATE_PARAMS.damp.cohesion` | 2000 |  |  | [moisture](#moisture) |
| `moisture.STATE_PARAMS.wet.film` | 2e-05 |  |  | [moisture](#moisture) |
| `moisture.STATE_PARAMS.wet.sat` | 0.8 |  |  | [moisture](#moisture) |
| `moisture.STATE_PARAMS.wet.fill` | 0.7 |  |  | [moisture](#moisture) |
| `moisture.STATE_PARAMS.wet.mu` | 1 |  |  | [moisture](#moisture) |
| `moisture.STATE_PARAMS.wet.e` | 0.4 |  |  | [moisture](#moisture) |
| `moisture.STATE_PARAMS.wet.cohesion` | 1000 |  |  | [moisture](#moisture) |
| `moisture.STATE_PARAMS.saturated.film` | 3.5e-05 |  |  | [moisture](#moisture) |
| `moisture.STATE_PARAMS.saturated.sat` | 1 |  |  | [moisture](#moisture) |
| `moisture.STATE_PARAMS.saturated.fill` | 1 |  |  | [moisture](#moisture) |
| `moisture.STATE_PARAMS.saturated.mu` | 0.8 |  |  | [moisture](#moisture) |
| `moisture.STATE_PARAMS.saturated.e` | 0.3 |  |  | [moisture](#moisture) |
| `moisture.STATE_PARAMS.saturated.cohesion` | 0 |  |  | [moisture](#moisture) |

### Sources

- <a id="wentworth"></a>**wentworth** (standard table): Udden-Wentworth grain-size classes on the Krumbein phi scale: fine sand 0.125 to 0.25 mm, medium sand 0.25 to 0.5 mm, sand 0.0625 to 2 mm, fine gravel 4 to 8 mm, medium gravel 8 to 16 mm, very coarse gravel 32 to 64 mm. <https://en.wikipedia.org/wiki/Grain_size>, <https://open.maricopa.edu/physicalgeology/chapter/6-1-clastic-sedimentary-rocks/>
- <a id="folk"></a>**folk** (standard table): Folk's sorting classes (inclusive graphic standard deviation, phi): very well sorted under 0.35, well sorted 0.35 to 0.50, moderately well sorted 0.50 to 0.71, moderately sorted 0.71 to 1.00, poorly sorted 1.00 to 2.00. <https://core.ecu.edu/rigsbyc/rigsby/sedimentology/CalculationOfGrainSizeStatistics.pdf>
- <a id="en13450"></a>**en13450** (standard table): Railway ballast to EN 13450: grading 31.5 to 63 mm (Rail Baltica specification, category F); particle density 2000 to 2800 kg/m³ and water absorption 0.5 to 3.5 % where railways set them. <https://www.railbaltica.org/wp-content/uploads/2024/01/RBDG-MAN-014C-0101_TS_Ballast.pdf>, <https://www.researchsquare.com/article/rs-10871621>
- <a id="quartz"></a>**quartz** (handbook): Density of quartz: 2650 kg/m³ (IRCAM material table; Engineers Edge, 2.65). <https://support.ircam.fr/docs/Modalys/3.6/Objects/ObjectProperties/object_properties_material.html>, <https://engineersedge.com/material_science/density_of_various_solids_tables_15685.htm>
- <a id="rocks"></a>**rocks** (handbook): Dry density of rocks: igneous 2700 to 3000 kg/m³, metamorphic 2700 (Useful numbers for geotechnical engineers); marble 2560 to 2760 (IRCAM). <https://geotechnics.webador.de/_downloads/3a14c91bf4e879f943d36823488fd77d>, <https://support.ircam.fr/docs/Modalys/3.6/Objects/ObjectProperties/object_properties_material.html>
- <a id="plastics"></a>**plastics** (handbook): Densities: soft commercial rubber 1.1, hard rubber 1.2 g/cm³ (Engineering ToolBox); polypropylene 0.90 to 0.96, glass 2.40 to 2.70 kg/dm³ (Archweb). <https://engineeringtoolbox.com/density-solids-d_1265.html>, <https://www.archweb.com/en/specific-weight-table/>
- <a id="grains"></a>**grains** (handbook): True density of kernels: wheat 1177 to 1222 kg/m³ (Kheiralipour et al. 2008), green wheat 1241 to 1333 (Al-Mahasneh and Rababah 2007); maize 1110 to 1290 (Bala et al.), 1195 to 1267 (Bhise et al. 2014); wheat on plywood, static friction 0.41 to 0.62. <https://thaiscience.info/Journals/Article/IJAT/10843016.pdf>, <https://agris.fao.org/search/en/records/65df573db766d82b1801449b>, <https://epubs.icar.org.in/index.php/IJAgS/article/download/87590/35690/224512>, <https://core.ac.uk/download/83549536.pdf>
- <a id="interface_friction"></a>**interface_friction** (handbook): Interface friction angles: glass on glass about 22° (tan = 0.40), rubber on concrete about 37° (Useful numbers for geotechnical engineers). <https://tu-freiberg.de/sites/default/files/2023-11/56%20Useful%20Numbers%20for%20Geotechnical%20Engineers%206.pdf>
- <a id="jsc1a"></a>**jsc1a** (handbook): JSC-1A lunar regolith simulant: specific gravity of solids 2.92 (JSC-1: 2.90); Apollo soils' median particle size about 40 to 130 µm (Carrier). <https://alshibli.utk.edu/?p=288>, <https://spaceresourcetech.com/blogs/articles/lunar-regolith-properties>
- <a id="size"></a>**size** (estimate): size and sorting of the materials no classification fixes (crushed products, seeds, pellets, fruit). Estimate: the usual sizes of each product (a wheat kernel about 4 mm across, a pellet 3 to 10 mm, a cherry tomato 2 to 3 cm); seeds and pellets are made or bred to size, so very well sorted.
- <a id="density"></a>**density** (estimate): particle density of the materials without a cited value. Estimate: the density of the solid, pores included where water does not fill them: coal 1.2 to 1.5 g/cm³, hematite-rich ore below hematite's 5.3, scoria and wood pellets with their pores, seeds over 1 (they sink), expanded polystyrene about 12 kg/m³, a basaltic Martian simulant near basalt.
- <a id="friction"></a>**friction** (estimate): contact friction of the grains without a cited value. Estimate: from each material's angle of repose (tan φ: 0.5 to 0.75 for sands and crushed rock, rounder and polished grains lower, seeds and pellets 0.3 to 0.45); not measured.
- <a id="restitution"></a>**restitution** (estimate): restitution of a grain on a hard floor. Estimate: rocks and sands barely bounce (0.05 to 0.25), seeds and plastics more, glass beads and rubber most; not measured.
- <a id="absorption"></a>**absorption** (estimate): water absorbed by a grain at saturation, as a fraction of its dry mass. Estimate: dense rock and quartz under 1 %, porous scoria and volcanic sand tens of percent, seeds 25 to 90 % (beans swell to about twice their mass); nothing for plastics and rubber.
- <a id="soft"></a>**soft** (estimate): Young's modulus, Poisson ratio and damping of the deformable grains (cherry tomato, packing peanut). Estimate: a tomato's flesh is a few 1e5 Pa and nearly incompressible; expanded polystyrene of 12 kg/m³ about 1 MPa with a small Poisson ratio; the damping is a starting point for PhysX, uncalibrated.
- <a id="shape"></a>**shape** (estimate): Granulaire's shape model: Zingg ratios (beta laws), facets, roundness exponent, roughness, lumps, taper, chips, pits, kernel creases and dents, pellet and tube proportions. Estimate: set by eye from photographs of each material, then checked by the measured sphericity and roundness of the generated grains (docs/physics.md); not fitted to a measured distribution.
- <a id="moisture"></a>**moisture** (estimate): the moisture model: water film, pore saturation, friction and restitution multipliers, capillary cohesion, heap porosity. Estimate: a random packing of grains has a porosity of about 0.36 to 0.40; the cohesion is the order of magnitude of a damp sand's (kPa) at 0.35 mm, scaled with grain size; the rest is chosen so the four states look and behave in order. To be calibrated, as moisture.py says.

### Numbers that are not physical values

- `PRESETS.*.minerals, surface_roughness, moisture.STATE_PARAMS albedo, rough, coat`: render appearance (colours and their shares, glossiness, the wet look), not physical properties.
- `PRESETS.*.subdivisions, deformable.tet_resolution`: mesh resolution.
- `PRESETS.*.curves, dent_dir, chip_axis`: which way a shape is built: choices of the shape model.
- `moisture.RHO_WATER`: the density of water (998 kg/m³ at 20 °C), rounded.
- `moisture.DEFAULT_WEIGHTS`: how often each moisture state is drawn: a choice.
- `ground.GROUND_*`: the shared ground of the Primvaria suite (ground.py), the same in every generator.
<!-- sources: end -->
