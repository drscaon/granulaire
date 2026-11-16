# What each grain draws

Every Granulaire grain draws its own values, aspect by aspect (see
[openusd.md](openusd.md) for where they are written). Each value follows a
rule applied to its preset's own numbers: the rules first, then the numbers
of every preset.

A grain is made from one of five bodies, given by its preset: an exact
sphere (glass beads), a faceted rock, a smooth superellipsoid (kernels,
beans), a cylinder (pellets) or a bent tube (packing peanuts). A grain
records only the values its body uses: a glass bead records its size and
its colour, not an elongation it does not have.

Both tables are written from `granulaire/declared.py` and the presets, and
`tests/test_distributions.py` draws 2000 grains of every preset to check
that the generator follows them: every value lies in its declared range and
follows its rule (chi-square for choices and whole numbers,
Kolmogorov-Smirnov for the rest, at p > 0.001), and each grain records
exactly the values of its body. The sizes are also checked against the
preset's grading curve (`tests/test_grading.py`). Regenerate the tables with
`python -m granulaire.declared`.

Drawn but not recorded: where each chip, pit and bend falls, and the wave
pattern of the lumps. They come from each grain's own random stream, so the
same seed gives the same grain.

<!-- declared: begin -->

### Rules

| Column | Aspect | Drawn as | Bodies that record it |
|---|---|---|---|
| `variation:phi` | size | normal, mean `phi_mean`, sd `phi_std` | sphere, rock, superellipsoid, cylinder, tube |
| `variation:diameter_m` | size | 2^−phi mm, from the drawn phi | sphere, rock, superellipsoid, cylinder, tube |
| `variation:elongation` | shape | beta(`elongation_beta`), raised to `elongation_min` (0.4 by default) | rock, superellipsoid |
| `variation:flatness` | shape | beta(`flatness_beta`), raised to `flatness_min` (0.4 by default) | rock, superellipsoid, cylinder, tube |
| `variation:aspect_ratio` | shape | uniform within `aspect` (0 if none) | cylinder, tube |
| `variation:lumpiness` | shape | uniform within `lumpiness` (0 if none) | rock, superellipsoid, cylinder, tube |
| `variation:taper` | shape | `taper`: t gives uniform −t to t, a pair keeps its sign (0 if none) | rock, superellipsoid, cylinder |
| `variation:chips` | shape | whole number within `chips`, both included (0 if none) | rock, superellipsoid, cylinder |
| `variation:pits` | shape | whole number within `pits`, both included (0 if none) | rock, superellipsoid, cylinder, tube |
| `variation:facets` | roundness | whole number within `facets`, both included (0 if none) | rock |
| `variation:roundness_p` | roundness | log-uniform within `roundness_p` | rock |
| `variation:mineral` | mineralogy | one of the `minerals`, with its weight | sphere, rock, superellipsoid, cylinder, tube |
| `variation:color_rgb` | mineralogy | the mineral's colour × uniform 0.88 to 1.12, + normal(0, 0.02) per channel, within 0 to 1 | sphere, rock, superellipsoid, cylinder, tube |

### The presets' numbers

| Preset | Body | phi mean, sd | `elongation_beta` | `flatness_beta` | `aspect` | `lumpiness` | `taper` | `chips` | `pits` | `facets` | `roundness_p` | minerals |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `beach_sand` | rock | 1.5, 0.45 | 8, 3 | 7, 3 |  | 0.03 to 0.1 | ±0.15 | 0 to 2 |  | 14 to 30 | 3 to 9 | quartz 0.72, feldspar 0.13, dark lithics 0.09, shell 0.06 |
| `dune_sand` | rock | 2.2, 0.3 | 10, 2.5 | 9, 2.5 |  | 0.02 to 0.06 | ±0.1 |  |  | 20 to 40 | 1.8 to 3.5 | quartz 0.85, feldspar 0.1, dark lithics 0.05 |
| `volcanic_sand` | rock | 1, 0.6 | 6, 3 | 6, 3 |  | 0.05 to 0.15 |  | 1 to 4 | 2 to 6 | 10 to 22 | 6 to 14 | basaltic glass 0.7, olivine 0.15, plagioclase 0.1, oxidised scoria 0.05 |
| `rounded_gravel` | rock | -2.5, 0.5 | 7, 3 | 6, 3 |  | 0.04 to 0.12 | ±0.2 | 0 to 2 |  | 16 to 32 | 3 to 8 | quartz 0.45, granite 0.25, flint 0.15, basalt 0.15 |
| `crushed_gravel` | rock | -3, 0.35 | 6, 3 | 5, 3 |  | 0 to 0.04 |  | 2 to 6 |  | 6 to 14 | 18 to 45 | light limestone 0.4, grey granite 0.3, basalt 0.18, beige flint 0.12 |
| `marble_chips` | rock | -3.5, 0.3 | 6, 3 | 5, 3 |  | 0 to 0.03 |  | 2 to 5 |  | 8 to 16 | 10 to 25 | white marble 0.6, grey-veined marble 0.25, cream marble 0.15 |
| `pozzolana` | rock | -3.5, 0.4 | 6, 3 | 6, 3 |  | 0.08 to 0.18 |  | 0 to 2 | 4 to 10 | 10 to 22 | 5 to 12 | red scoria 0.55, black scoria 0.3, dark brown scoria 0.15 |
| `river_pebbles` | rock | -5.5, 0.5 | 7, 2.5 | 6, 2.5 |  | 0.02 to 0.07 | ±0.15 |  |  | 24 to 40 | 1.3 to 2 | tan quartzite 0.22, grey granite 0.2, brown sandstone 0.18, buff limestone 0.14, green greenstone 0.14, red jasper 0.12 |
| `beach_pebbles` | rock | -5.3, 0.4 | 5, 2.5 | 2.5, 4 |  | 0.02 to 0.06 | ±0.15 |  |  | 24 to 40 | 1.3 to 2 | black basalt 0.3, charcoal basalt 0.25, white marble 0.2, blue-grey basalt 0.15, grey marble 0.1 |
| `railway_ballast` | rock | -5.3, 0.2 | 5, 3 | 5, 3 |  | 0 to 0.03 |  | 3 to 7 |  | 6 to 12 | 25 to 60 | grey diorite 0.6, granite 0.3, rust-stained stone 0.1 |
| `iron_ore` | rock | -4, 0.5 | 5, 3 | 5, 3 |  | 0.02 to 0.08 |  | 2 to 6 | 0 to 3 | 6 to 12 | 20 to 50 | hematite 0.55, magnetite 0.25, quartz gangue 0.2 |
| `coal` | rock | -4.5, 0.5 | 5, 3 | 4, 3 |  | 0 to 0.03 |  | 2 to 5 |  | 6 to 12 | 20 to 50 | dull coal 0.6, bright coal 0.3, shale 0.1 |
| `rubber_mulch` | rock | -4.3, 0.35 | 4, 3 | 4, 3 |  | 0.08 to 0.2 | ±0.2 | 2 to 4 |  | 7 to 13 | 5 to 12 | black rubber 0.55, red-dyed rubber 0.15, brown-dyed rubber 0.15, green-dyed rubber 0.15 |
| `wheat` | superellipsoid | -2, 0.15 | 10, 10 | 18, 2 |  | 0 to 0.03 | 0.1 to 0.2 |  |  |  |  | golden kernel 0.75, pale kernel 0.2, reddish kernel 0.05 |
| `maize` | superellipsoid | -2.87, 0.15 | 14, 5 | 11, 9 |  | 0 to 0.04 | -0.5 to -0.4 |  |  |  |  | yellow kernel 0.75, orange kernel 0.15, white kernel 0.1 |
| `rice` | superellipsoid | -1.49, 0.1 | 12, 28 | 16, 4 |  |  | 0.05 to 0.15 |  |  |  |  | translucent white 0.85, chalky white 0.1, unpolished 0.05 |
| `beans` | superellipsoid | -3.16, 0.15 | 11, 9 | 15, 5 |  | 0 to 0.02 |  |  |  |  |  | red kidney 0.35, white navy 0.25, black bean 0.2, pinto 0.2 |
| `soybean` | superellipsoid | -2.7, 0.15 | 18, 3 | 18, 3 |  | 0 to 0.02 |  |  |  |  |  | yellow bean 0.8, greenish bean 0.12, brown bean 0.08 |
| `cherry_tomatoes` | superellipsoid | -4.6, 0.18 | 30, 2 | 12, 2 |  | 0 to 0.025 |  |  |  |  |  | red 0.7, deep red 0.2, orange-red 0.1 |
| `plastic_pellets` | cylinder | -1.77, 0.08 |  | 30, 2 | 0.75 to 1.1 |  |  |  |  |  |  | natural 0.5, white 0.2, black 0.15, blue 0.1, red 0.05 |
| `wood_pellets` | cylinder | -3.3, 0.25 |  | 30, 2 | 0.2 to 0.5 | 0 to 0.02 |  | 1 to 2 |  |  |  | light wood 0.6, dark wood 0.3, bark-rich 0.1 |
| `packing_peanuts` | tube | -4.3, 0.12 |  | 14, 4 | 0.32 to 0.42 | 0 to 0.03 |  |  |  |  |  | white EPS 0.6, green recycled EPS 0.25, pink antistatic EPS 0.15 |
| `lunar_regolith` | rock | 3.8, 1.2 | 5, 3 | 5, 3 |  | 0.06 to 0.18 |  | 2 to 6 | 1 to 5 | 6 to 16 | 10 to 40 | plagioclase 0.4, agglutinate glass 0.3, pyroxene 0.2, ilmenite 0.1 |
| `martian_regolith` | rock | 3, 1.3 | 5, 3 | 5, 3 |  | 0.05 to 0.14 |  | 1 to 4 | 0 to 3 | 6 to 18 | 8 to 30 | oxidised dust 0.4, basalt 0.3, orange alteration 0.2, light sulfates 0.1 |
| `glass_beads` | sphere | 0, 0.1 |  |  |  |  |  |  |  |  |  | clear glass 0.8, tinted glass 0.2 |

<!-- declared: end -->
