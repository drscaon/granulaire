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
  dry mass (internal porosity; see granulaire/moisture.py);
- moisture: False where a wet state makes no sense: no liquid water
  (regoliths) or water runs off (polystyrene peanuts); moisture_note says why;
- kind: base body, "rock" (default, random polyhedron), "superellipsoid"
  (kernels and seeds, with `exponent`) or "cylinder" (pellets, with
  `exponent` and `aspect` = radius / half-length range); crease, dent and
  chip_axis="x" shape kernels and pellet ends (see granulaire/shape.py);
- kind "tube" (packing peanuts): a rounded tube along an S, C or straight
  curve (`curves` weights, `curve_amplitude`), radius `aspect`;
- deformable: Young's modulus, Poisson's ratio, elasticity damping (1/s,
  how much energy a deformation loses, hence how much the grain bounces) and
  simulation-mesh resolution for grains exported as deformable bodies (see usd_export.py);
- surface_roughness: visual roughness of the dry surface (default 0.85,
  matte); lower for glossy skins (fruit);
- sphere: True for exact spheres (glass beads, the reference);
- category: display family (see CATEGORIES).

Values are realistic orders of magnitude, not measurements of a specific
deposit.
"""

# display order of the categories
CATEGORIES = [
    "Sand",
    "Gravel",
    "Pebbles",
    "Industrial",
    "Agricultural",
    "Pellets",
    "Packaging",
    "Space",
    "Reference",
]

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
        # tumbled by steady, gentler currents: rounder, more equant than beach
        # pebbles, uniformly smooth, no fresh fracture faces
        "elongation_beta": (7.0, 2.5),  # mean I/L ~0.74
        "flatness_beta": (6.0, 2.5),  # mean S/I ~0.71
        "facets": (24, 40),
        "roundness_p": (1.3, 2.0),
        "roughness": 0.004,
        "lumpiness": (0.02, 0.07),
        "taper": 0.15,
        "density": 2650.0,  # quartz, granite
        "friction": 0.50,
        "restitution": 0.20,
        "absorption": 0.006,
        "subdivisions": 4,
        # rustic, earthy mix of varied minerals
        "minerals": [
            ("tan quartzite", 0.22, (0.76, 0.70, 0.60)),
            ("grey granite", 0.20, (0.56, 0.54, 0.52)),
            ("brown sandstone", 0.18, (0.55, 0.42, 0.30)),
            ("buff limestone", 0.14, (0.72, 0.64, 0.52)),
            ("green greenstone", 0.14, (0.42, 0.47, 0.38)),
            ("red jasper", 0.12, (0.60, 0.35, 0.28)),
        ],
    },
    "beach_pebbles": {
        "category": "Pebbles",
        "label": "Beach pebbles",
        "phi_mean": -5.3,  # ~40 mm
        "phi_std": 0.40,
        # shaped by the back-and-forth of the waves: flatter, disc-shaped or
        # oval, polished (e.g. Mexican beach pebbles)
        "elongation_beta": (5.0, 2.5),  # mean I/L ~0.67: discs and ovals
        "flatness_beta": (2.5, 4.0),  # mean S/I ~0.38: clearly flattened
        "flatness_min": 0.22,
        "facets": (24, 40),
        "roundness_p": (1.3, 2.0),  # very rounded
        "roughness": 0.002,  # sleek, polished
        "lumpiness": (0.02, 0.06),
        "taper": 0.15,
        "density": 2850.0,  # dense basalt (~2900-3000) and marble (~2700)
        "friction": 0.40,  # polished surfaces
        "restitution": 0.25,
        "absorption": 0.002,  # dense, low-porosity stones
        "subdivisions": 4,
        "minerals": [
            ("black basalt", 0.30, (0.10, 0.10, 0.11)),
            ("charcoal basalt", 0.25, (0.22, 0.23, 0.24)),
            ("white marble", 0.20, (0.86, 0.85, 0.82)),
            ("blue-grey basalt", 0.15, (0.30, 0.36, 0.44)),
            ("grey marble", 0.10, (0.62, 0.62, 0.63)),
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
    "rubber_mulch": {
        "category": "Industrial",
        "label": "Rubber mulch (recycled tyres)",
        # shredded tyre chunks for playgrounds and landscaping: torn, irregular,
        # somewhat flat nuggets; grippy and bouncy
        "phi_mean": -4.3,  # ~20 mm (sold as 10-20 mm or 3/8"-3/4" nuggets)
        "phi_std": 0.35,
        "elongation_beta": (4.0, 3.0),  # I/L ~0.57
        "flatness_beta": (4.0, 3.0),  # S/I ~0.57
        "flatness_min": 0.35,
        "facets": (7, 13),
        "roundness_p": (5.0, 12.0),  # torn and cut edges, barely softened
        "roughness": 0.02,  # torn rubber, fibrous surface
        "lumpiness": (0.08, 0.20),
        "taper": 0.2,
        "chips": (2, 4),  # flat cut faces from the shredder
        "chip_depth": (0.55, 0.85),
        "density": 1150.0,  # vulcanised rubber
        "friction": 0.85,  # rubber on rubber
        "restitution": 0.55,
        "absorption": 0.0,  # rubber does not absorb water: surface film only
        "surface_roughness": 0.9,  # matte
        "subdivisions": 4,
        # natural black with some dyed nuggets ("mixed colour" playground grade)
        "minerals": [
            ("black rubber", 0.55, (0.07, 0.07, 0.07)),
            ("red-dyed rubber", 0.15, (0.48, 0.16, 0.12)),
            ("brown-dyed rubber", 0.15, (0.36, 0.23, 0.14)),
            ("green-dyed rubber", 0.15, (0.20, 0.36, 0.20)),
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
    "cherry_tomatoes": {
        "category": "Agricultural",
        "label": "Cherry tomatoes",
        "kind": "superellipsoid",
        "exponent": 2.0,  # smooth, round fruit
        "phi_mean": -4.6,  # ~24 mm
        "phi_std": 0.18,  # graded fruit
        "elongation_beta": (30.0, 2.0),  # I/L ~0.94: round in plan
        "flatness_beta": (12.0, 2.0),  # S/I ~0.86: slightly flattened at the poles
        "dent": (0.05, 0.09, 0.16),  # stem scar
        "dent_dir": (0.0, 0.0, 1.0),
        "lumpiness": (0.0, 0.025),
        "facets": (4, 4),
        "roundness_p": (1.0, 1.0),
        "roughness": 0.0,
        "density": 1000.0,
        "friction": 0.45,
        "restitution": 0.20,
        "absorption": 0.0,
        "moisture": False,  # waxy skin: water beads and runs off
        "moisture_note": "waxy skin",
        "surface_roughness": 0.25,  # glossy skin
        # soft fruit that keeps its volume when squeezed; order of magnitude of
        # the apparent modulus of a whole cherry tomato in compression
        # elasticity_damping (1/s, PhysX): uncalibrated starting point
        "deformable": {
            "youngs_modulus": 5.0e5,
            "poissons_ratio": 0.45,
            "elasticity_damping": 0.01,
            "tet_resolution": 9,  # ~1,000-1,500 tetrahedra per tomato, like a peanut
        },
        "subdivisions": 4,
        "minerals": [
            ("red", 0.70, (0.74, 0.10, 0.07)),
            ("deep red", 0.20, (0.52, 0.06, 0.05)),
            ("orange-red", 0.10, (0.84, 0.30, 0.08)),
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
    # ------------------------------------------------------------- Packaging
    "packing_peanuts": {
        "category": "Packaging",
        "label": "Packing peanuts (EPS)",
        "kind": "tube",
        "curves": {"S": 0.75, "C": 0.25},
        "curve_amplitude": (0.30, 0.45),
        "aspect": (0.32, 0.42),  # tube radius / half-length
        "phi_mean": -4.3,  # ~20 mm nominal, ~35-40 mm long
        "phi_std": 0.12,
        "elongation_beta": (1.0, 1.0),  # unused for tubes
        "flatness_beta": (14.0, 4.0),  # cross-section ~0.78
        "lumpiness": (0.0, 0.03),
        "facets": (4, 4),
        "roundness_p": (1.0, 1.0),
        "roughness": 0.01,  # fused-bead texture
        "density": 12.0,  # expanded polystyrene, piece density
        "friction": 0.50,
        "restitution": 0.30,
        "absorption": 0.0,
        "moisture": False,  # closed-cell polystyrene: water runs off, the peanut stays dry
        "moisture_note": "water runs off",
        # elasticity_damping (1/s, PhysX): uncalibrated starting point, foam is lossy
        "deformable": {
            "youngs_modulus": 1.0e6,
            "poissons_ratio": 0.10,
            "elasticity_damping": 0.02,
            "tet_resolution": 18,
        },
        "subdivisions": 4,
        "minerals": [
            ("white EPS", 0.60, (0.95, 0.95, 0.93)),
            ("green recycled EPS", 0.25, (0.45, 0.70, 0.45)),
            ("pink antistatic EPS", 0.15, (0.92, 0.65, 0.72)),
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
