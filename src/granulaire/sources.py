"""Where every physical value of Granulaire comes from (PRV-33).

Each value that describes the real world (a grain's size and sorting, density, friction, restitution,
water absorption, stiffness, and the moisture model) names its source: a classification table of
sedimentology, a standard's requirements, a handbook or a paper, or, where none was found, an estimate
with what it rests on. Where the source gives a range, the value lies within it; tests/test_sources.py
checks it, and that no value is left without a source. A size class bounds a material's mean size: its
grains spread around it by their sorting, as a real sediment's do.

A preset is a kind of material, not a measurement of a specific deposit: its source is the class it
belongs to (medium sand for beach sand, the EN 13450 grading for railway ballast) or the density of its
mineral. The shape parameters (Zingg ratios, facets, roundness, lumps, chips, pits) describe Granulaire's
shape model and are estimates set by eye from photographs of each material.

    python -m granulaire.sources     # the tables of docs/sources.md
"""

from __future__ import annotations

import math
import numbers
from dataclasses import dataclass

from . import moisture
from .presets import PRESETS

KINDS = ("standard table", "datasheet", "handbook", "estimate")


@dataclass(frozen=True)
class Source:
    kind: str  # one of KINDS
    title: str
    urls: tuple = ()
    note: str = ""  # for an estimate: what it rests on


def phi(d_mm: float) -> float:
    """Krumbein phi of a diameter in mm."""
    return -math.log2(d_mm)


SOURCES = {
    "wentworth": Source(
        "standard table",
        "Udden-Wentworth grain-size classes on the Krumbein phi scale: fine sand 0.125 to 0.25 mm, medium "
        "sand 0.25 to 0.5 mm, sand 0.0625 to 2 mm, fine gravel 4 to 8 mm, medium gravel 8 to 16 mm, very "
        "coarse "
        "gravel 32 to 64 mm",
        (
            "https://en.wikipedia.org/wiki/Grain_size",
            "https://open.maricopa.edu/physicalgeology/chapter/6-1-clastic-sedimentary-rocks/",
        ),
    ),
    "folk": Source(
        "standard table",
        "Folk's sorting classes (inclusive graphic standard deviation, phi): very well sorted under 0.35, "
        "well "
        "sorted 0.35 to 0.50, moderately well sorted 0.50 to 0.71, moderately sorted 0.71 to 1.00, poorly "
        "sorted 1.00 to 2.00",
        ("https://core.ecu.edu/rigsbyc/rigsby/sedimentology/CalculationOfGrainSizeStatistics.pdf",),
    ),
    "en13450": Source(
        "standard table",
        "Railway ballast to EN 13450: grading 31.5 to 63 mm (Rail Baltica specification, category F); "
        "particle density 2000 to 2800 kg/m³ and water absorption 0.5 to 3.5 % where railways set them",
        (
            "https://www.railbaltica.org/wp-content/uploads/2024/01/RBDG-MAN-014C-0101_TS_Ballast.pdf",
            "https://www.researchsquare.com/article/rs-10871621",
        ),
    ),
    "quartz": Source(
        "handbook",
        "Density of quartz: 2650 kg/m³ (IRCAM material table; Engineers Edge, 2.65)",
        (
            "https://support.ircam.fr/docs/Modalys/3.6/Objects/ObjectProperties/object_properties_material.html",  # noqa: E501
            "https://engineersedge.com/material_science/density_of_various_solids_tables_15685.htm",
        ),
    ),
    "rocks": Source(
        "handbook",
        "Dry density of rocks: igneous 2700 to 3000 kg/m³, metamorphic 2700 (Useful numbers for geotechnical "
        "engineers); marble 2560 to 2760 (IRCAM)",
        (
            "https://geotechnics.webador.de/_downloads/3a14c91bf4e879f943d36823488fd77d",
            "https://support.ircam.fr/docs/Modalys/3.6/Objects/ObjectProperties/object_properties_material.html",  # noqa: E501
        ),
    ),
    "plastics": Source(
        "handbook",
        "Densities: soft commercial rubber 1.1, hard rubber 1.2 g/cm³ (Engineering ToolBox); polypropylene "
        "0.90 to 0.96, glass 2.40 to 2.70 kg/dm³ (Archweb)",
        (
            "https://engineeringtoolbox.com/density-solids-d_1265.html",
            "https://www.archweb.com/en/specific-weight-table/",
        ),
    ),
    "grains": Source(
        "handbook",
        "True density of kernels: wheat 1177 to 1222 kg/m³ (Kheiralipour et al. 2008), green wheat 1241 to "
        "1333 "
        "(Al-Mahasneh and Rababah 2007); maize 1110 to 1290 (Bala et al.), 1195 to 1267 (Bhise et al. 2014); "
        "wheat on plywood, static friction 0.41 to 0.62",
        (
            "https://thaiscience.info/Journals/Article/IJAT/10843016.pdf",
            "https://agris.fao.org/search/en/records/65df573db766d82b1801449b",
            "https://epubs.icar.org.in/index.php/IJAgS/article/download/87590/35690/224512",
            "https://core.ac.uk/download/83549536.pdf",
        ),
    ),
    "interface_friction": Source(
        "handbook",
        "Interface friction angles: glass on glass about 22° (tan = 0.40), rubber on concrete about 37° "
        "(Useful numbers for geotechnical engineers)",
        (
            "https://tu-freiberg.de/sites/default/files/2023-11/56%20Useful%20Numbers%20for%20Geotechnical%20Engineers%206.pdf",  # noqa: E501
        ),
    ),
    "jsc1a": Source(
        "handbook",
        "JSC-1A lunar regolith simulant: specific gravity of solids 2.92 (JSC-1: 2.90); Apollo soils' median "
        "particle size about 40 to 130 µm (Carrier)",
        (
            "https://alshibli.utk.edu/?p=288",
            "https://spaceresourcetech.com/blogs/articles/lunar-regolith-properties",
        ),
    ),
    # ------------------------------------------------------------------ estimates
    "size": Source(
        "estimate",
        "size and sorting of the materials no classification fixes (crushed products, seeds, pellets, fruit)",
        note="the usual sizes of each product (a wheat kernel about 4 mm across, a pellet 3 to 10 mm, a "
        "cherry "
        "tomato 2 to 3 cm); seeds and pellets are made or bred to size, so very well sorted",
    ),
    "density": Source(
        "estimate",
        "particle density of the materials without a cited value",
        note="the density of the solid, pores included where water does not fill them: coal 1.2 to 1.5 "
        "g/cm³, "
        "hematite-rich ore below hematite's 5.3, scoria and wood pellets with their pores, seeds over 1 "
        "(they sink), expanded polystyrene about 12 kg/m³, a basaltic Martian simulant near basalt",
    ),
    "friction": Source(
        "estimate",
        "contact friction of the grains without a cited value",
        note="from each material's angle of repose (tan φ: 0.5 to 0.75 for sands and crushed rock, rounder "
        "and "
        "polished grains lower, seeds and pellets 0.3 to 0.45); not measured",
    ),
    "restitution": Source(
        "estimate",
        "restitution of a grain on a hard floor",
        note="rocks and sands barely bounce (0.05 to 0.25), seeds and plastics more, glass beads and rubber "
        "most; not measured",
    ),
    "absorption": Source(
        "estimate",
        "water absorbed by a grain at saturation, as a fraction of its dry mass",
        note="dense rock and quartz under 1 %, porous scoria and volcanic sand tens of percent, seeds 25 to "
        "90 % "
        "(beans swell to about twice their mass); nothing for plastics and rubber",
    ),
    "soft": Source(
        "estimate",
        "Young's modulus, Poisson ratio and damping of the deformable grains (cherry tomato, packing peanut)",
        note="a tomato's flesh is a few 1e5 Pa and nearly incompressible; expanded polystyrene of 12 kg/m³ "
        "about "
        "1 MPa with a small Poisson ratio; the damping is a starting point for PhysX, uncalibrated",
    ),
    "shape": Source(
        "estimate",
        "Granulaire's shape model: Zingg ratios (beta laws), facets, roundness exponent, roughness, lumps, "
        "taper, chips, pits, kernel creases and dents, pellet and tube proportions",
        note="set by eye from photographs of each material, then checked by the measured sphericity and "
        "roundness of the generated grains (docs/physics.md); not fitted to a measured distribution",
    ),
    "moisture": Source(
        "estimate",
        "the moisture model: water film, pore saturation, friction and restitution multipliers, capillary "
        "cohesion, heap porosity",
        note="a random packing of grains has a porosity of about 0.36 to 0.40; the cohesion is the order of "
        "magnitude of a damp sand's (kPa) at 0.35 mm, scaled with grain size; the rest is chosen so the four "
        "states look and behave in order. To be calibrated, as moisture.py says",
    ),
}

DIAMETER = {  # preset: (source, range of phi_mean the source gives: class or measurements)
    "beach_sand": ("wentworth", phi(0.5), phi(0.25)),  # medium sand
    "dune_sand": ("wentworth", phi(0.25), phi(0.125)),  # fine sand
    "volcanic_sand": ("wentworth", phi(2.0), phi(0.0625)),  # sand
    "rounded_gravel": ("wentworth", phi(8.0), phi(4.0)),  # fine gravel
    "crushed_gravel": ("wentworth", phi(16.0), phi(4.0)),  # fine to medium gravel
    "marble_chips": ("wentworth", phi(16.0), phi(8.0)),  # medium gravel
    "river_pebbles": ("wentworth", phi(64.0), phi(32.0)),  # very coarse gravel
    "beach_pebbles": ("wentworth", phi(64.0), phi(32.0)),
    "railway_ballast": ("en13450", phi(63.0), phi(31.5)),
    "lunar_regolith": ("jsc1a", phi(0.130), phi(0.040)),
}
SORTING = {  # preset: (source, range of phi_std)
    "beach_sand": ("folk", 0.35, 0.50),  # well sorted
    "dune_sand": ("folk", 0.0, 0.35),  # very well sorted
    "volcanic_sand": ("folk", 0.50, 0.71),  # moderately well sorted
    "lunar_regolith": ("folk", 1.0, 2.0),  # poorly sorted
    "martian_regolith": ("folk", 1.0, 2.0),
}
DENSITY = {  # preset: (source, range in kg/m³)
    "beach_sand": ("quartz", 2650.0, 2650.0),
    "dune_sand": ("quartz", 2650.0, 2650.0),
    "rounded_gravel": ("quartz", 2650.0, 2650.0),
    "river_pebbles": ("quartz", 2650.0, 2650.0),
    "volcanic_sand": ("rocks", 2700.0, 3000.0),
    "crushed_gravel": ("rocks", 2700.0, 3000.0),
    "beach_pebbles": ("rocks", 2700.0, 3000.0),
    "marble_chips": ("rocks", 2560.0, 2760.0),
    "railway_ballast": ("en13450", 2000.0, 2800.0),
    "rubber_mulch": ("plastics", 1100.0, 1200.0),
    "plastic_pellets": ("plastics", 900.0, 960.0),
    "glass_beads": ("plastics", 2400.0, 2700.0),
    "wheat": ("grains", 1177.0, 1333.0),
    "maize": ("grains", 1110.0, 1290.0),
    "lunar_regolith": ("jsc1a", 2900.0, 2920.0),
}
FRICTION = {  # preset: (source, range)
    "wheat": ("grains", 0.41, 0.62),
    "glass_beads": ("interface_friction", 0.40, 0.40),
}
ABSORPTION = {"railway_ballast": ("en13450", None, 0.035)}  # a railway's upper limit

PHYSICAL = ("phi_mean", "phi_std", "density", "friction", "restitution", "absorption")
SHAPE = (
    "elongation_beta",
    "flatness_beta",
    "elongation_min",
    "flatness_min",
    "facets",
    "roundness_p",
    "roughness",
    "lumpiness",
    "taper",
    "chips",
    "chip_depth",
    "pits",
    "pit_depth",
    "pit_size",
    "exponent",
    "aspect",
    "bend",
    "crease",
    "dent",
    "curve_amplitude",
)
SOFT = ("youngs_modulus", "poissons_ratio", "elasticity_damping")


@dataclass(frozen=True)
class Value:
    path: str  # where it is in the code: PRESETS.beach_sand.density
    value: float
    unit: str
    source: str  # a key of SOURCES
    low: float | None = None  # the range the source gives, when it gives one
    high: float | None = None


def _numbers(path: str, x):
    """(path, number) of a number or of each number of a tuple."""
    if isinstance(x, tuple):
        for i, y in enumerate(x):
            yield f"{path}.{i}", y
    elif isinstance(x, numbers.Number) and not isinstance(x, bool):
        yield path, x


def _presets() -> list[Value]:
    out = []
    for key, p in PRESETS.items():
        name = f"PRESETS.{key}"
        if "phi_mean" in p:
            src, lo, hi = DIAMETER.get(key, ("size", None, None))
            out.append(Value(f"{name}.phi_mean", p["phi_mean"], "phi", src, lo, hi))
            src, lo, hi = SORTING.get(key, ("size", None, None))
            out.append(Value(f"{name}.phi_std", p["phi_std"], "phi", src, lo, hi))
        out.append(
            Value(f"{name}.density", p["density"], "kg/m³", *DENSITY.get(key, ("density", None, None)))
        )
        out.append(Value(f"{name}.friction", p["friction"], "", *FRICTION.get(key, ("friction", None, None))))
        out.append(Value(f"{name}.restitution", p["restitution"], "", "restitution"))
        src, lo, hi = ABSORPTION.get(key, ("absorption", None, None))
        out.append(Value(f"{name}.absorption", p.get("absorption", 0.0), "", src, lo, hi))
        for field in SHAPE:
            if field in p:
                out += [Value(path, x, "", "shape") for path, x in _numbers(f"{name}.{field}", p[field])]
        for field in SOFT:
            if field in p.get("deformable", {}):
                out.append(Value(f"{name}.deformable.{field}", p["deformable"][field], "", "soft"))
    return out


def _moisture() -> list[Value]:
    out = [
        Value("moisture.POROSITY", moisture.POROSITY, "", "moisture", 0.36, 0.40),
        Value("moisture.COHESION_REF_D", moisture.COHESION_REF_D * 1e3, "mm", "moisture"),
    ]
    for state, params in moisture.STATE_PARAMS.items():
        for field in ("film", "sat", "fill", "mu", "e", "cohesion"):
            out.append(Value(f"moisture.STATE_PARAMS.{state}.{field}", params[field], "", "moisture"))
    return out


def values() -> list[Value]:
    """Every physical value of the generator, with its source."""
    return _presets() + _moisture()


# Numbers in the code that are not about the real world, and so have no source: what they are.
NOT_PHYSICAL = {
    "PRESETS.*.minerals, surface_roughness, moisture.STATE_PARAMS albedo, rough, coat": "render appearance "
    "(colours and their shares, glossiness, the wet look), not physical properties",
    "PRESETS.*.subdivisions, deformable.tet_resolution": "mesh resolution",
    "PRESETS.*.curves, dent_dir, chip_axis": "which way a shape is built: choices of the shape model",
    "moisture.RHO_WATER": "the density of water (998 kg/m³ at 20 °C), rounded",
    "moisture.DEFAULT_WEIGHTS": "how often each moisture state is drawn: a choice",
    "ground.GROUND_*": "the shared ground of the Primvaria suite (ground.py), the same in every generator",
    "newton.GAP_MAX, GAP_SHARE": "the contact gap of the Newton layer (a quarter of a grain, at most "
    "0.5 mm): "
    "an engine setting, not a property of the grains",
}


def _fmt(x) -> str:
    return "" if x is None else f"{x:.4g}"


def table() -> str:
    """The Markdown tables of docs/sources.md."""
    out = ["| Value | | Unit | Range the source gives | Source |", "|---|---|---|---|---|"]
    for v in values():
        span = f"{_fmt(v.low)} to {_fmt(v.high)}" if v.low is not None or v.high is not None else ""
        span = "" if span == " to " else span.strip()
        out.append(f"| `{v.path}` | {v.value:g} | {v.unit} | {span} | [{v.source}](#{v.source}) |")
    out += ["", "### Sources", ""]
    for key, s in SOURCES.items():
        links = ", ".join(f"<{u}>" for u in s.urls)
        note = f" Estimate: {s.note}." if s.note else ""
        line = f'- <a id="{key}"></a>**{key}** ({s.kind}): {s.title}.{note}'
        out.append(line + (f" {links}" if links else ""))
    out += ["", "### Numbers that are not physical values", ""]
    out += [f"- `{name}`: {why}." for name, why in NOT_PHYSICAL.items()]
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    print(table())
