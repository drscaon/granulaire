"""Granular material presets.

Each preset describes parameter *distributions*, borrowed from sedimentology,
rather than a single shape:

- size: nominal diameter on the phi scale (phi = -log2(d in mm)), normal law
  (Wentworth scale: sand 0.063-2 mm, gravel 2-64 mm, cobbles 64-256 mm);
- shape: Zingg ratios I/L (elongation) and S/I (flatness), beta laws;
- facets: number of cutting planes of the base polyhedron (few = angular);
- roundness: exponent p of the "soft norm" that rounds edges and corners
  (low p = well rounded, high p = sharp edges);
- roughness: relative amplitude of the surface noise;
- irregularity (optional, per grain): lumpiness (amplitude range of
  low-frequency lumps), taper (max egg asymmetry), chips (range of fracture
  planes) with chip_depth, pits (range of dents/vesicles) with pit_depth and
  pit_size;
- minerals: colours and proportions (rendering), density (mass);
- absorption: water absorbed by the grain at saturation, as a fraction of its
  dry mass (internal porosity; see granulat/moisture.py);
- moisture: False for a material where water makes no sense (regoliths);
- kind: base body, "rock" (default, random polyhedron), "superellipsoid"
  (kernels and seeds, with `exponent`) or "cylinder" (pellets, with
  `exponent` and `aspect` = radius / half-length range); crease, dent and
  chip_axis="x" shape kernels and pellet ends (see granulat/shape.py);
- sphere: True for exact spheres (glass beads, the reference);
- category: display family (see CATEGORIES).

Values are realistic orders of magnitude, not measurements of a specific
deposit.
"""

# display order of the categories
CATEGORIES = ["Sand", "Gravel", "Pebbles", "Industrial", "Agricultural", "Pellets", "Space", "Reference"]

PRESETS = {
    # ------------------------------------------------------------------ Sand
    "beach_sand": {
        "category": "Sand",
        "label": "Beach sand",
        "phi_mean": 1.5,  # ~0.35 mm: medium sand
        "phi_std": 0.45,  # well sorted
        "elongation_beta": (8.0, 3.0),  # mean I/L ~0.73
        "flatness_beta": (7.0, 3.0),  # mean S/I ~0.70
        "facets": (14, 30),
        "roundness_p": (3.0, 9.0),
        "roughness": 0.012,
        "lumpiness": (0.03, 0.1),
        "taper": 0.15,
        "chips": (0, 2),
        "chip_depth": (0.75, 0.9),
        "density": 2650.0,  # quartz, kg/m3
        "friction": 0.55,
        "restitution": 0.10,
        "absorption": 0.005,
        "subdivisions": 4,
        "minerals": [
            # name, proportion, approximate linear RGB colour
            ("quartz", 0.72, (0.80, 0.70, 0.52)),
            ("feldspar", 0.13, (0.78, 0.60, 0.50)),
            ("dark lithics", 0.09, (0.30, 0.28, 0.26)),
            ("shell", 0.06, (0.92, 0.90, 0.84)),
        ],
    },
    "dune_sand": {
        "category": "Sand",
        "label": "Dune sand",
        "phi_mean": 2.2,  # ~0.22 mm: fine sand
        "phi_std": 0.30,  # very well sorted (wind sorting)
        "elongation_beta": (10.0, 2.5),
        "flatness_beta": (9.0, 2.5),
        "facets": (20, 40),
        "roundness_p": (1.8, 3.5),
        "roughness": 0.008,
        "lumpiness": (0.02, 0.06),
        "taper": 0.1,
        "density": 2650.0,
        "friction": 0.50,
        "restitution": 0.10,
        "absorption": 0.003,
        "subdivisions": 4,
        "minerals": [
            ("quartz", 0.85, (0.85, 0.68, 0.45)),
            ("feldspar", 0.10, (0.82, 0.55, 0.42)),
            ("dark lithics", 0.05, (0.35, 0.30, 0.25)),
        ],
    },
    "volcanic_sand": {
        "category": "Sand",
        "label": "Volcanic sand",
        "phi_mean": 1.0,  # ~0.5 mm
        "phi_std": 0.60,  # moderately sorted
        "elongation_beta": (6.0, 3.0),
        "flatness_beta": (6.0, 3.0),
        "facets": (10, 22),
        "roundness_p": (6.0, 14.0),  # subangular
        "roughness": 0.015,  # vesicular glass
        "lumpiness": (0.05, 0.15),
        "chips": (1, 4),
        "chip_depth": (0.6, 0.85),
        "pits": (2, 6),
        "pit_depth": (0.08, 0.2),
        "pit_size": (0.25, 0.45),
        "density": 2900.0,  # basaltic glass
        "friction": 0.60,
        "restitution": 0.10,
        "absorption": 0.03,  # porous grains
        "subdivisions": 4,
        "minerals": [
            ("basaltic glass", 0.70, (0.10, 0.10, 0.11)),
            ("olivine", 0.15, (0.30, 0.36, 0.18)),
            ("plagioclase", 0.10, (0.55, 0.55, 0.55)),
            ("oxidised scoria", 0.05, (0.35, 0.15, 0.10)),
        ],
    },
    # ---------------------------------------------------------------- Gravel
    "rounded_gravel": {
        "category": "Gravel",
        "label": "Rounded gravel",
        "phi_mean": -2.5,  # ~5.7 mm
        "phi_std": 0.50,
        "elongation_beta": (7.0, 3.0),
        "flatness_beta": (6.0, 3.0),
        "facets": (16, 32),
        "roundness_p": (3.0, 8.0),  # subrounded to rounded
        "roughness": 0.006,
        "lumpiness": (0.04, 0.12),
        "taper": 0.2,
        "chips": (0, 2),
        "chip_depth": (0.7, 0.9),
        "density": 2650.0,
        "friction": 0.55,
        "restitution": 0.15,
        "absorption": 0.008,
        "subdivisions": 4,
        "minerals": [
            ("quartz", 0.45, (0.75, 0.70, 0.62)),
            ("granite", 0.25, (0.58, 0.52, 0.50)),
            ("flint", 0.15, (0.55, 0.45, 0.35)),
            ("basalt", 0.15, (0.28, 0.28, 0.30)),
        ],
    },
    "crushed_gravel": {
        "category": "Gravel",
        "label": "Crushed gravel",
        "phi_mean": -3.0,  # ~8 mm
        "phi_std": 0.35,  # screened, hence narrow
        "elongation_beta": (6.0, 3.0),  # mean I/L ~0.67
        "flatness_beta": (5.0, 3.0),  # mean S/I ~0.63
        "facets": (6, 14),
        "roundness_p": (18.0, 45.0),
        "roughness": 0.0,  # micro-roughness belongs in a texture (normal map)
        "lumpiness": (0.0, 0.04),
        "chips": (2, 6),
        "chip_depth": (0.55, 0.85),
        "density": 2700.0,  # limestone / granite
        "friction": 0.65,
        "restitution": 0.15,
        "absorption": 0.01,
        "subdivisions": 4,
        "minerals": [
            ("light limestone", 0.40, (0.66, 0.64, 0.58)),
            ("grey granite", 0.30, (0.48, 0.48, 0.50)),
            ("basalt", 0.18, (0.27, 0.28, 0.30)),
            ("beige flint", 0.12, (0.62, 0.52, 0.40)),
        ],
    },
    "marble_chips": {
        "category": "Gravel",
        "label": "White marble chips",
        "phi_mean": -3.5,  # ~11 mm (decorative 8/16 grade)
        "phi_std": 0.30,
        "elongation_beta": (6.0, 3.0),
        "flatness_beta": (5.0, 3.0),
        "facets": (8, 16),
        "roundness_p": (10.0, 25.0),  # crushed, edges slightly worn
        "roughness": 0.0,
        "lumpiness": (0.0, 0.03),
        "chips": (2, 5),
        "chip_depth": (0.6, 0.85),
        "density": 2700.0,  # calcite
        "friction": 0.60,
        "restitution": 0.15,
        "absorption": 0.003,
        "subdivisions": 4,
        "minerals": [
            ("white marble", 0.60, (0.88, 0.87, 0.84)),
            ("grey-veined marble", 0.25, (0.76, 0.76, 0.75)),
            ("cream marble", 0.15, (0.86, 0.82, 0.73)),
        ],
    },
    "pozzolana": {
        "category": "Gravel",
        "label": "Pozzolana (scoria)",
        "phi_mean": -3.5,  # ~11 mm (garden 7/15 grade)
        "phi_std": 0.40,
        "elongation_beta": (6.0, 3.0),
        "flatness_beta": (6.0, 3.0),
        "facets": (10, 22),
        "roundness_p": (5.0, 12.0),  # subangular scoria
        "roughness": 0.02,  # vesicular surface
        "lumpiness": (0.08, 0.18),
        "chips": (0, 2),
        "chip_depth": (0.65, 0.85),
        "pits": (4, 10),
        "pit_depth": (0.08, 0.22),
        "pit_size": (0.2, 0.4),
        "density": 1400.0,  # apparent grain density, pores included
        "friction": 0.75,
        "restitution": 0.10,
        "absorption": 0.20,  # very porous: soaks up water
        "subdivisions": 4,
        "minerals": [
            ("red scoria", 0.55, (0.45, 0.18, 0.12)),
            ("black scoria", 0.30, (0.12, 0.11, 0.11)),
            ("dark brown scoria", 0.15, (0.30, 0.14, 0.10)),
        ],
    },
    # --------------------------------------------------------------- Pebbles
    "river_pebbles": {
        "category": "Pebbles",
        "label": "River pebbles",
        "phi_mean": -5.5,  # ~45 mm
        "phi_std": 0.50,
        "elongation_beta": (6.0, 3.0),
        "flatness_beta": (4.0, 3.0),  # pebbles are often flattened
        "facets": (18, 36),
        "roundness_p": (1.5, 3.0),
        "roughness": 0.006,
        "lumpiness": (0.04, 0.12),
        "taper": 0.25,
        "chips": (0, 1),
        "chip_depth": (0.75, 0.9),
        "density": 2650.0,
        "friction": 0.50,
        "restitution": 0.20,
        "absorption": 0.006,
        "subdivisions": 4,
        "minerals": [
            ("granite", 0.35, (0.55, 0.52, 0.50)),
            ("quartzite", 0.30, (0.78, 0.74, 0.68)),
            ("basalt", 0.20, (0.25, 0.26, 0.28)),
            ("sandstone", 0.15, (0.60, 0.45, 0.33)),
        ],
    },
    "beach_pebbles": {
        "category": "Pebbles",
        "label": "Beach pebbles",
        "phi_mean": -5.3,  # ~40 mm
        "phi_std": 0.40,
        "elongation_beta": (6.0, 2.5),
        "flatness_beta": (3.0, 3.0),  # discs: the surf flattens pebbles
        "flatness_min": 0.30,
        "facets": (20, 36),
        "roundness_p": (1.5, 2.5),  # very rounded, polished
        "roughness": 0.004,
        "lumpiness": (0.03, 0.12),
        "taper": 0.2,
        "pits": (0, 2),
        "pit_depth": (0.05, 0.12),
        "pit_size": (0.2, 0.35),
        "density": 2600.0,  # flint
        "friction": 0.45,
        "restitution": 0.20,
        "absorption": 0.005,
        "subdivisions": 4,
        "minerals": [
            ("grey flint", 0.40, (0.45, 0.45, 0.47)),
            ("white quartzite", 0.25, (0.82, 0.80, 0.76)),
            ("pink granite", 0.20, (0.66, 0.55, 0.50)),
            ("basalt", 0.15, (0.24, 0.24, 0.26)),
        ],
    },
    # ------------------------------------------------------------ Industrial
    "railway_ballast": {
        "category": "Industrial",
        "label": "Railway ballast",
        "phi_mean": -5.3,  # ~40 mm (31.5/50 grade)
        "phi_std": 0.20,  # very narrow
        "elongation_beta": (5.0, 3.0),
        "flatness_beta": (5.0, 3.0),
        "facets": (6, 12),
        "roundness_p": (25.0, 60.0),  # very angular
        "roughness": 0.0,
        "lumpiness": (0.0, 0.03),
        "chips": (3, 7),
        "chip_depth": (0.55, 0.8),
        "density": 2750.0,  # diorite / granite
        "friction": 0.70,
        "restitution": 0.15,
        "absorption": 0.004,
        "subdivisions": 4,
        "minerals": [
            ("grey diorite", 0.60, (0.42, 0.42, 0.43)),
            ("granite", 0.30, (0.55, 0.53, 0.52)),
            ("rust-stained stone", 0.10, (0.48, 0.38, 0.30)),
        ],
    },
    "iron_ore": {
        "category": "Industrial",
        "label": "Crushed iron ore",
        "phi_mean": -4.0,  # ~16 mm
        "phi_std": 0.50,
        "elongation_beta": (5.0, 3.0),
        "flatness_beta": (5.0, 3.0),
        "facets": (6, 12),
        "roundness_p": (20.0, 50.0),  # crushed, very angular
        "roughness": 0.0,
        "lumpiness": (0.02, 0.08),
        "chips": (2, 6),
        "chip_depth": (0.5, 0.85),
        "pits": (0, 3),
        "pit_depth": (0.05, 0.12),
        "pit_size": (0.15, 0.3),
        "density": 4500.0,  # hematite-rich ore
        "friction": 0.70,
        "restitution": 0.12,
        "absorption": 0.01,
        "subdivisions": 4,
        "minerals": [
            ("hematite", 0.55, (0.25, 0.12, 0.10)),
            ("magnetite", 0.25, (0.10, 0.10, 0.11)),
            ("quartz gangue", 0.20, (0.60, 0.58, 0.55)),
        ],
    },
    "coal": {
        "category": "Industrial",
        "label": "Crushed coal",
        "phi_mean": -4.5,  # ~22 mm
        "phi_std": 0.50,
        "elongation_beta": (5.0, 3.0),
        "flatness_beta": (4.0, 3.0),  # breaks into platelets
        "facets": (6, 12),
        "roundness_p": (20.0, 50.0),
        "roughness": 0.0,
        "lumpiness": (0.0, 0.03),
        "chips": (2, 5),
        "chip_depth": (0.5, 0.8),
        "density": 1350.0,
        "friction": 0.55,
        "restitution": 0.10,
        "absorption": 0.05,
        "subdivisions": 4,
        "minerals": [
            ("dull coal", 0.60, (0.07, 0.07, 0.07)),
            ("bright coal", 0.30, (0.11, 0.11, 0.12)),
            ("shale", 0.10, (0.30, 0.30, 0.30)),
        ],
    },
    # ---------------------------------------------------------- Agricultural
    "wheat": {
        "category": "Agricultural",
        "label": "Wheat kernels",
        "kind": "superellipsoid",
        "exponent": 2.0,
        "phi_mean": -2.0,  # ~4 mm nominal (about 6.5 x 3.3 x 3 mm)
        "phi_std": 0.15,
        "elongation_beta": (10.0, 10.0),  # I/L ~0.5
        "flatness_beta": (18.0, 2.0),  # S/I ~0.9
        "taper": (0.1, 0.2),  # germ end narrower than brush end
        "crease": (0.12, 0.12),  # ventral groove along the kernel
        "lumpiness": (0.0, 0.03),
        "facets": (4, 4),  # unused for kernels
        "roundness_p": (1.0, 1.0),
        "roughness": 0.0,
        "density": 1400.0,  # kernel true density
        "friction": 0.40,
        "restitution": 0.40,
        "absorption": 0.30,  # kernels swell when soaked
        "subdivisions": 4,
        "minerals": [
            ("golden kernel", 0.75, (0.78, 0.56, 0.30)),
            ("pale kernel", 0.20, (0.86, 0.70, 0.45)),
            ("reddish kernel", 0.05, (0.62, 0.36, 0.20)),
        ],
    },
    "maize": {
        "category": "Agricultural",
        "label": "Maize kernels",
        "kind": "superellipsoid",
        "exponent": 2.8,  # boxy, wedge-like
        "phi_mean": -2.87,  # ~7.3 mm nominal (about 11 x 8 x 4.5 mm)
        "phi_std": 0.15,
        "elongation_beta": (14.0, 5.0),  # I/L ~0.74
        "flatness_beta": (11.0, 9.0),  # S/I ~0.55
        "flatness_min": 0.35,
        "taper": (-0.5, -0.4),  # narrow tip (attachment), broad crown at -x
        "dent": (0.05, 0.12, 0.35),  # dent corn: hollow in the crown
        "lumpiness": (0.0, 0.04),
        "facets": (4, 4),
        "roundness_p": (1.0, 1.0),
        "roughness": 0.0,
        "density": 1280.0,
        "friction": 0.45,
        "restitution": 0.35,
        "absorption": 0.30,
        "subdivisions": 4,
        "minerals": [
            ("yellow kernel", 0.75, (0.90, 0.62, 0.15)),
            ("orange kernel", 0.15, (0.85, 0.45, 0.10)),
            ("white kernel", 0.10, (0.90, 0.86, 0.72)),
        ],
    },
    "rice": {
        "category": "Agricultural",
        "label": "Rice (long grain, milled)",
        "kind": "superellipsoid",
        "exponent": 2.2,
        "phi_mean": -1.49,  # ~2.8 mm nominal (about 6.8 x 2 x 1.6 mm)
        "phi_std": 0.10,
        "elongation_beta": (12.0, 28.0),  # I/L ~0.3: slender
        "elongation_min": 0.2,
        "flatness_beta": (16.0, 4.0),  # S/I ~0.8
        "taper": (0.05, 0.15),
        "dent": (0.02, 0.06, 0.25),  # embryo notch
        "facets": (4, 4),
        "roundness_p": (1.0, 1.0),
        "roughness": 0.0,
        "density": 1450.0,
        "friction": 0.40,
        "restitution": 0.30,
        "absorption": 0.25,
        "subdivisions": 4,
        "minerals": [
            ("translucent white", 0.85, (0.88, 0.86, 0.80)),
            ("chalky white", 0.10, (0.95, 0.94, 0.90)),
            ("unpolished", 0.05, (0.74, 0.62, 0.45)),
        ],
    },
    "beans": {
        "category": "Agricultural",
        "label": "Common beans",
        "kind": "superellipsoid",
        "exponent": 2.2,
        "phi_mean": -3.16,  # ~9 mm nominal (about 15 x 8 x 6 mm)
        "phi_std": 0.15,
        "elongation_beta": (11.0, 9.0),  # I/L ~0.55
        "flatness_beta": (15.0, 5.0),  # S/I ~0.75
        "bend": (0.60, 0.85),  # kidney shape (above 0.5 the inner side turns concave)
        "dent": (0.03, 0.06, 0.18),  # hilum, on the inner side
        "dent_dir": (0.0, 1.0, 0.0),
        "lumpiness": (0.0, 0.02),
        "facets": (4, 4),
        "roundness_p": (1.0, 1.0),
        "roughness": 0.0,
        "density": 1300.0,
        "friction": 0.35,
        "restitution": 0.40,
        "absorption": 0.90,  # dry beans about double in mass when soaked
        "subdivisions": 4,
        "minerals": [
            ("red kidney", 0.35, (0.45, 0.10, 0.10)),
            ("white navy", 0.25, (0.92, 0.90, 0.84)),
            ("black bean", 0.20, (0.08, 0.07, 0.08)),
            ("pinto", 0.20, (0.78, 0.62, 0.48)),
        ],
    },
    "soybean": {
        "category": "Agricultural",
        "label": "Soybeans",
        "kind": "superellipsoid",
        "exponent": 2.0,
        "phi_mean": -2.7,  # ~6.5 mm
        "phi_std": 0.15,
        "elongation_beta": (18.0, 3.0),  # I/L ~0.86
        "flatness_beta": (18.0, 3.0),  # S/I ~0.86
        "dent": (0.02, 0.05, 0.15),  # hilum
        "lumpiness": (0.0, 0.02),
        "facets": (4, 4),
        "roundness_p": (1.0, 1.0),
        "roughness": 0.0,
        "density": 1200.0,
        "friction": 0.35,
        "restitution": 0.45,
        "absorption": 0.40,  # soybeans roughly double in mass when soaked
        "subdivisions": 4,
        "minerals": [
            ("yellow bean", 0.80, (0.85, 0.72, 0.45)),
            ("greenish bean", 0.12, (0.70, 0.70, 0.40)),
            ("brown bean", 0.08, (0.55, 0.40, 0.25)),
        ],
    },
    # --------------------------------------------------------------- Pellets
    "plastic_pellets": {
        "category": "Pellets",
        "label": "Plastic pellets",
        "kind": "cylinder",
        "exponent": 8.0,  # strand-cut pellets: slightly rounded end edges
        "aspect": (0.75, 1.1),  # radius / half-length: diameter ~ length
        "phi_mean": -1.77,  # ~3.4 mm
        "phi_std": 0.08,  # very uniform
        "elongation_beta": (1.0, 1.0),  # unused for cylinders
        "flatness_beta": (30.0, 2.0),  # cross-section slightly oval
        "facets": (4, 4),
        "roundness_p": (1.0, 1.0),
        "roughness": 0.0,
        "density": 950.0,  # polyethylene / polypropylene
        "friction": 0.30,
        "restitution": 0.50,
        "absorption": 0.0,  # plastics do not absorb water (surface film only)
        "subdivisions": 4,
        "minerals": [
            ("natural", 0.50, (0.86, 0.86, 0.82)),
            ("white", 0.20, (0.95, 0.95, 0.95)),
            ("black", 0.15, (0.08, 0.08, 0.08)),
            ("blue", 0.10, (0.15, 0.35, 0.75)),
            ("red", 0.05, (0.75, 0.15, 0.12)),
        ],
    },
    "wood_pellets": {
        "category": "Pellets",
        "label": "Wood pellets",
        "kind": "cylinder",
        "exponent": 12.0,
        "aspect": (0.2, 0.5),  # 6 mm diameter, 10-30 mm long
        "phi_mean": -3.3,  # ~10 mm nominal
        "phi_std": 0.25,
        "elongation_beta": (1.0, 1.0),
        "flatness_beta": (30.0, 2.0),
        "chips": (1, 2),  # broken ends
        "chip_axis": "x",
        "chip_depth": (0.75, 0.95),
        "lumpiness": (0.0, 0.02),
        "facets": (4, 4),
        "roundness_p": (1.0, 1.0),
        "roughness": 0.015,  # pressed sawdust surface
        "density": 1150.0,  # particle density
        "friction": 0.50,
        "restitution": 0.20,
        "absorption": 0.50,  # swell and crumble when wet
        "subdivisions": 4,
        "minerals": [
            ("light wood", 0.60, (0.72, 0.58, 0.40)),
            ("dark wood", 0.30, (0.55, 0.42, 0.28)),
            ("bark-rich", 0.10, (0.42, 0.32, 0.22)),
        ],
    },
    # ----------------------------------------------------------------- Space
    "lunar_regolith": {
        "category": "Space",
        "label": "Lunar regolith (simulant)",
        "phi_mean": 3.8,  # ~0.07 mm: silt / very fine sand
        "phi_std": 1.20,  # very poorly sorted
        "elongation_beta": (5.0, 3.0),
        "flatness_beta": (5.0, 3.0),
        "facets": (6, 16),
        "roundness_p": (10.0, 40.0),  # very angular: no water or wind erosion
        "roughness": 0.010,
        "lumpiness": (0.06, 0.18),
        "chips": (2, 6),
        "chip_depth": (0.5, 0.85),
        "pits": (1, 5),
        "pit_depth": (0.1, 0.25),
        "pit_size": (0.2, 0.4),
        "density": 3100.0,  # particle density
        "friction": 0.75,
        "restitution": 0.05,
        "absorption": 0.0,
        "moisture": False,  # no water
        "subdivisions": 4,
        "minerals": [
            ("plagioclase", 0.40, (0.55, 0.55, 0.55)),
            ("agglutinate glass", 0.30, (0.18, 0.17, 0.16)),
            ("pyroxene", 0.20, (0.30, 0.28, 0.25)),
            ("ilmenite", 0.10, (0.08, 0.08, 0.08)),
        ],
    },
    "martian_regolith": {
        "category": "Space",
        "label": "Martian regolith (simulant)",
        "phi_mean": 3.0,  # ~0.125 mm
        "phi_std": 1.30,  # very poorly sorted
        "elongation_beta": (5.0, 3.0),
        "flatness_beta": (5.0, 3.0),
        "facets": (6, 18),
        "roundness_p": (8.0, 30.0),  # angular, slightly wind-worn
        "roughness": 0.010,
        "lumpiness": (0.05, 0.14),
        "chips": (1, 4),
        "chip_depth": (0.55, 0.85),
        "pits": (0, 3),
        "pit_depth": (0.08, 0.2),
        "pit_size": (0.2, 0.4),
        "density": 2900.0,  # basaltic
        "friction": 0.70,
        "restitution": 0.05,
        "absorption": 0.0,
        "moisture": False,  # no liquid water at the surface
        "subdivisions": 4,
        "minerals": [
            ("oxidised dust", 0.40, (0.55, 0.28, 0.16)),
            ("basalt", 0.30, (0.20, 0.18, 0.17)),
            ("orange alteration", 0.20, (0.65, 0.38, 0.22)),
            ("light sulfates", 0.10, (0.75, 0.65, 0.50)),
        ],
    },
    # ------------------------------------------------------------- Reference
    "glass_beads": {
        "category": "Reference",
        "label": "Glass beads (reference)",
        "phi_mean": 0.0,  # 1 mm
        "phi_std": 0.10,  # calibrated
        "elongation_beta": (1.0, 1.0),  # ignored: exact spheres
        "flatness_beta": (1.0, 1.0),
        "sphere": True,
        "facets": (4, 4),
        "roundness_p": (1.0, 1.0),
        "roughness": 0.0,
        "density": 2500.0,  # soda-lime glass
        "friction": 0.35,
        "restitution": 0.85,
        "absorption": 0.0,
        "subdivisions": 4,
        "minerals": [
            ("clear glass", 0.80, (0.82, 0.86, 0.84)),
            ("tinted glass", 0.20, (0.55, 0.70, 0.66)),
        ],
    },
}
