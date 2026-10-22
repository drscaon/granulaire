"""Scene generation: grain library, mixing, moisture states, and file outputs.

The library API is separate from the command line so it can be used from
Python and tested directly:

    from granulat import Variations, generate_scene, write_outputs
    scene = generate_scene("beach_sand", shapes=100, copies=5, seed=1,
                           variations=Variations(moisture=True))
    write_outputs(scene, "output")
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np

from . import moisture
from .measure import measure
from .presets import PRESETS
from .shape import make_grain
from .usd_export import export_stage


@dataclass
class Variations:
    """Which properties vary from grain to grain (the "checkboxes").

    Turning one off does not change the random draws of the others: with the
    same seed you compare the same scene with a single difference.
    """

    size: bool = True  # diameter from the grading curve, else d50 for all
    shape: bool = True  # elongation and flatness drawn, else mean values
    roundness: bool = True  # facets and edge rounding drawn, else median values
    mineralogy: bool = True  # mineral and tint drawn, else dominant mineral
    orientation: bool = True  # random orientation, else all aligned
    moisture: bool = False  # "moisture" variant set + state drawn per grain


@dataclass
class Scene:
    preset_key: str
    preset: dict
    seed: int
    variations: Variations
    prototypes: list
    instances: list
    states: list | None
    order: np.ndarray
    spacing: float
    side: int
    moisture_weights: dict | None = field(default=None)
    deformable: dict | None = field(default=None)


def _beta_mean(ab):
    return ab[0] / (ab[0] + ab[1])


def sample_params(rng, preset, var: Variations):
    # always draw, then override when the variation is off:
    # the random sequence stays the same whatever boxes are ticked
    phi = rng.normal(preset["phi_mean"], preset["phi_std"])
    elong = rng.beta(*preset["elongation_beta"])
    flat = rng.beta(*preset["flatness_beta"])
    facets = int(rng.integers(preset["facets"][0], preset["facets"][1] + 1))
    lo_p, hi_p = preset["roundness_p"]
    p = float(np.exp(rng.uniform(np.log(lo_p), np.log(hi_p))))

    # irregularity: low-frequency lumps, egg taper, fracture chips, pits
    lump_lo, lump_hi = preset.get("lumpiness", (0.0, 0.0))
    lump = rng.uniform(lump_lo, lump_hi)
    # taper: a number gives a random sign up to that amount, a range keeps its sign
    taper_spec = preset.get("taper", 0.0)
    taper_lo, taper_hi = taper_spec if isinstance(taper_spec, tuple) else (-taper_spec, taper_spec)
    taper = rng.uniform(taper_lo, taper_hi)
    chips_lo, chips_hi = preset.get("chips", (0, 0))
    chips = int(rng.integers(chips_lo, chips_hi + 1))
    pits_lo, pits_hi = preset.get("pits", (0, 0))
    pits = int(rng.integers(pits_lo, pits_hi + 1))
    aspect_lo, aspect_hi = preset.get("aspect", (1.0, 1.0))
    aspect = rng.uniform(aspect_lo, aspect_hi)

    if not var.size:
        phi = preset["phi_mean"]
    if not var.shape:
        elong = _beta_mean(preset["elongation_beta"])
        flat = _beta_mean(preset["flatness_beta"])
        lump, taper = (lump_lo + lump_hi) / 2, (taper_lo + taper_hi) / 2
        chips, pits = round((chips_lo + chips_hi) / 2), round((pits_lo + pits_hi) / 2)
        aspect = (aspect_lo + aspect_hi) / 2
    if not var.roundness:
        facets = (preset["facets"][0] + preset["facets"][1]) // 2
        p = float(np.sqrt(lo_p * hi_p))
    return {
        "phi": phi,
        "diameter_m": 2.0 ** (-phi) / 1000.0,
        # lower bounds avoid unrealistic flakes (cf. aggregate flakiness index)
        "elongation": max(elong, preset.get("elongation_min", 0.4)),
        "flatness": max(flat, preset.get("flatness_min", 0.4)),
        "facets": facets,
        "roundness_p": p,
        "roughness": preset["roughness"],
        "kind": preset.get("kind", "rock"),
        "exponent": preset.get("exponent", 2.0),
        "aspect": aspect,
        "crease": preset.get("crease"),
        "dent": preset.get("dent"),
        "dent_dir": preset.get("dent_dir"),
        # drawn inside make_grain from the grain's own stream; mean when shape is off
        "bend": preset.get("bend") if var.shape or not preset.get("bend") else (sum(preset["bend"]) / 2,) * 2,
        "chip_axis": preset.get("chip_axis"),
        "lumpiness": lump,
        "taper": taper,
        "chips": chips,
        "chip_depth": preset.get("chip_depth", (0.6, 0.85)),
        "pits": pits,
        "pit_depth": preset.get("pit_depth", (0.08, 0.2)),
        "pit_size": preset.get("pit_size", (0.2, 0.4)),
        "subdivisions": preset["subdivisions"],
        "sphere": preset.get("sphere", False),
        # tube grains: curve drawn inside make_grain; mean amplitude when shape is off
        "curves": preset.get("curves"),
        "curve_amplitude": preset.get("curve_amplitude", (0.0, 0.0)),
        "vary": var.shape,
    }


def sample_color(rng, preset, var: Variations):
    names = [m[0] for m in preset["minerals"]]
    probs = np.array([m[1] for m in preset["minerals"]])
    k = rng.choice(len(names), p=probs / probs.sum())
    factor = rng.uniform(0.88, 1.12)
    noise = rng.normal(0, 0.02, 3)
    if not var.mineralogy:
        k, factor, noise = int(np.argmax(probs)), 1.0, np.zeros(3)
    base = np.array(preset["minerals"][k][2])
    return names[k], tuple(np.clip(base * factor + noise, 0.0, 1.0))


def random_quaternion(rng):
    """Uniform rotation (Shoemake's method), returned as (w, x, y, z)."""
    u1, u2, u3 = rng.random(3)
    a, b = np.sqrt(1 - u1), np.sqrt(u1)
    return (
        b * np.cos(2 * np.pi * u3),
        a * np.sin(2 * np.pi * u2),
        a * np.cos(2 * np.pi * u2),
        b * np.sin(2 * np.pi * u3),
    )


def moisture_applies(preset_key: str) -> bool:
    return PRESETS[preset_key].get("moisture", True)


def generate_scene(
    preset_key: str,
    shapes: int = 100,
    copies: int = 5,
    seed: int = 1,
    variations: Variations | None = None,
    moisture_weights: str = moisture.DEFAULT_WEIGHTS,
    deformable: bool = True,
) -> Scene:
    """Build the grain library and the mixed scene in memory.

    Presets with a "deformable" entry (packing peanuts) also get a tetrahedral
    simulation mesh per grain and are exported as deformable bodies, unless
    deformable=False (then they are exported as rigid bodies like the others).
    """
    if preset_key not in PRESETS:
        raise KeyError(f"unknown preset '{preset_key}'")
    preset = PRESETS[preset_key]
    var = variations or Variations()
    use_moisture = var.moisture and moisture_applies(preset_key)
    weights = moisture.parse_weights(moisture_weights) if use_moisture else None
    states = list(moisture.STATES) if use_moisture else None
    soft = preset.get("deformable") if deformable else None

    rng = np.random.default_rng(seed)
    prototypes = []
    for i in range(shapes):
        params = sample_params(rng, preset, var)
        # each grain's geometry uses its own stream: the number of chips or pits
        # of one grain never shifts the draws of the next ones
        tet_points = tets = None
        if soft:
            params.update(tets=True, tet_resolution=soft.get("tet_resolution", 18))
            verts, faces, tet_points, tets = make_grain(np.random.default_rng([seed, 2, i]), params)
        else:
            verts, faces = make_grain(np.random.default_rng([seed, 2, i]), params)
        metrics = measure(verts, faces)
        mineral, color = sample_color(rng, preset, var)
        dry = metrics["volume_m3"] * preset["density"]
        proto = {
            "verts": verts,
            "faces": faces,
            "params": params,
            "metrics": metrics,
            "mineral": mineral,
            "color": color,
            "mass": dry,
        }
        if soft:
            proto["tet_points"], proto["tets"] = tet_points, tets
        if use_moisture:
            proto["moisture"] = {}
            for s in states:
                w = moisture.water_mass(
                    s, dry, metrics["area_m2"], preset.get("absorption", 0.0), preset["density"]
                )
                proto["moisture"][s] = {
                    "water_mass": w,
                    "mass": dry + w,
                    "cohesion": moisture.cohesion(s, metrics["diameter_nominal_m"]),
                }
        prototypes.append(proto)

    # Mixing: each shape appears `copies` times, in random order,
    # with its own random orientation.
    order = rng.permutation(np.repeat(np.arange(shapes), copies))
    n = len(order)
    side = int(np.ceil(n ** (1 / 3)))
    spacing = 1.15 * max(p["metrics"]["L_m"] for p in prototypes)
    instances = []
    for j, proto in enumerate(order):
        ix, iy, iz = j % side, (j // side) % side, j // (side * side)
        jitter = rng.uniform(-0.05, 0.05, 3) * spacing
        pos = (
            np.array([(ix - (side - 1) / 2) * spacing, (iy - (side - 1) / 2) * spacing, (iz + 1) * spacing])
            + jitter
        )
        q = random_quaternion(rng)
        if not var.orientation:
            q = (1.0, 0.0, 0.0, 0.0)
        instances.append({"proto": int(proto), "position": tuple(pos), "orient": q, "state": None})

    if use_moisture:
        # separate generator: enabling moisture leaves the rest of the scene unchanged
        rng_w = np.random.default_rng([seed, 1])
        drawn = rng_w.choice(states, size=n, p=[weights[s] for s in states])
        for inst, s in zip(instances, drawn, strict=True):
            inst["state"] = str(s)

    effective = Variations(**{**asdict(var), "moisture": bool(use_moisture)})
    return Scene(
        preset_key,
        preset,
        seed,
        effective,
        prototypes,
        instances,
        states,
        order,
        spacing,
        side,
        weights,
        soft,
    )


def summarize(scene: Scene) -> dict:
    protos = scene.prototypes
    keys = list(protos[0]["metrics"].keys())
    m = {k: np.array([p["metrics"][k] for p in protos]) for k in keys}
    dry_total = sum(protos[i]["mass"] for i in scene.order)
    summary = {
        "preset": scene.preset_key,
        "label": scene.preset["label"],
        "category": scene.preset["category"],
        "shapes": len(protos),
        "grains": len(scene.instances),
        "copies_per_shape": len(scene.instances) // len(protos),
        "seed": scene.seed,
        "variations": asdict(scene.variations),
        "d50_mm": float(np.median(m["diameter_nominal_m"]) * 1000),
        "d_min_mm": float(m["diameter_nominal_m"].min() * 1000),
        "d_max_mm": float(m["diameter_nominal_m"].max() * 1000),
        "mean_sphericity": float(m["sphericity"].mean()),
        "mean_elongation": float(m["elongation_IL"].mean()),
        "mean_flatness": float(m["flatness_SI"].mean()),
        "mean_angularity_deg": float(m["angularity_deg"].mean()),
        "min_convexity": float(m["convexity"].min()),
        "total_dry_mass_g": float(dry_total * 1000),
        "deformable": bool(scene.deformable),
    }
    if scene.deformable:
        summary["tetrahedra_per_grain_median"] = int(np.median([len(p["tets"]) for p in protos]))
    if scene.states:
        wet_total = sum(protos[i["proto"]]["moisture"][i["state"]]["mass"] for i in scene.instances)
        summary["moisture"] = {
            "grains_per_state": {s: sum(1 for i in scene.instances if i["state"] == s) for s in scene.states},
            "total_wet_mass_g": float(wet_total * 1000),
            "water_g": float((wet_total - dry_total) * 1000),
            # water content of the median grain, per state (% of dry mass)
            "median_water_content_pct": {
                s: float(np.median([p["moisture"][s]["water_mass"] / p["mass"] * 100 for p in protos]))
                for s in scene.states
            },
        }
    return summary


def write_outputs(scene: Scene, out_root: str | Path = "output") -> Path:
    """Write the USD scene, CSV tables, mesh archive and summary. Returns the folder."""
    out = Path(out_root) / scene.preset_key
    out.mkdir(parents=True, exist_ok=True)
    protos, states = scene.prototypes, scene.states

    usd_path = out / f"granulat_{scene.preset_key}.usdc"
    export_stage(
        usd_path,
        scene.preset,
        protos,
        scene.instances,
        ground_size=4 * scene.side * scene.spacing,
        states=states,
        deformable=scene.deformable,
    )

    keys = list(protos[0]["metrics"].keys())
    with open(out / "prototype_metrics.csv", "w", newline="") as f:
        w = csv.writer(f)
        extra = [f"mass_{s}_kg" for s in states] if states else []
        w.writerow(["prototype", "mineral", "mass_kg", "facets", "roundness_p"] + keys + extra)
        for i, p in enumerate(protos):
            row = [
                i,
                p["mineral"],
                f"{p['mass']:.6e}",
                p["params"]["facets"],
                f"{p['params']['roundness_p']:.2f}",
            ] + [f"{p['metrics'][k]:.6g}" for k in keys]
            if states:
                row += [f"{p['moisture'][s]['mass']:.6e}" for s in states]
            w.writerow(row)
    with open(out / "instances.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["grain", "prototype", "x_m", "y_m", "z_m", "moisture"])
        for j, inst in enumerate(scene.instances):
            w.writerow([j, inst["proto"], *[f"{c:.6g}" for c in inst["position"]], inst["state"] or ""])

    np.savez_compressed(
        out / "prototypes.npz",
        **{f"v{i}": p["verts"] for i, p in enumerate(protos)},
        **{f"f{i}": p["faces"] for i, p in enumerate(protos)},
        colors=np.array([p["color"] for p in protos]),
    )

    summary = summarize(scene)
    summary["usd"] = usd_path.name
    (out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    return out
