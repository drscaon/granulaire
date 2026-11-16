"""What every grain draws, declared once: the tables of docs/variation.md are written from this
module and from the presets (presets.PRESETS), and tests/test_distributions.py checks that the
generator follows them.

A grain's shape comes from one of five bodies, its preset's ``kind``: an exact sphere (``sphere``,
glass beads), a faceted rock (``rock``), a smooth superellipsoid (``superellipsoid``, kernels and
beans), a cylinder (``cylinder``, pellets) or a bent tube (``tube``, packing peanuts). Each body
uses only some of the drawn values, and a value its body does not use is not recorded.

Each row is (column, aspect, rule, bodies), the rule applied to the preset's own numbers:

* ("normal", mean, sd): normal draw;
* ("diameter",): 2 ** -phi millimetres, from the drawn phi;
* ("beta_min", field, minimum, default): a beta draw with the preset's two numbers, raised to
  the preset's minimum (default when the preset gives none);
* ("integers", field): a whole number between the preset's two, both included (0 when it has none);
* ("loguniform", field): uniform in log between the preset's two;
* ("uniform", field): uniform between the preset's two (0 when it has none);
* ("taper",): the preset's taper; a number t is uniform between -t and t, a pair keeps its sign;
* ("weights", field): one of the preset's minerals, with its weight;
* ("tint",): the mineral's colour, times a uniform 0.88 to 1.12, plus a normal noise of sd 0.02 per
  channel, kept within 0 to 1.
"""

from __future__ import annotations

from .presets import PRESETS

ALL = ("sphere", "rock", "superellipsoid", "cylinder", "tube")
SHAPED = ("rock", "superellipsoid", "cylinder", "tube")
ROUND = ("rock", "superellipsoid")  # the bodies that have three axes

DECLARED = [
    ("phi", "size", ("normal", "phi_mean", "phi_std"), ALL),
    ("diameter_m", "size", ("diameter",), ALL),
    ("elongation", "shape", ("beta_min", "elongation_beta", "elongation_min", 0.4), ROUND),
    ("flatness", "shape", ("beta_min", "flatness_beta", "flatness_min", 0.4), SHAPED),
    ("aspect_ratio", "shape", ("uniform", "aspect"), ("cylinder", "tube")),
    ("lumpiness", "shape", ("uniform", "lumpiness"), SHAPED),
    ("taper", "shape", ("taper",), ("rock", "superellipsoid", "cylinder")),
    ("chips", "shape", ("integers", "chips"), ("rock", "superellipsoid", "cylinder")),
    ("pits", "shape", ("integers", "pits"), SHAPED),
    ("facets", "roundness", ("integers", "facets"), ("rock",)),
    ("roundness_p", "roundness", ("loguniform", "roundness_p"), ("rock",)),
    ("mineral", "mineralogy", ("weights", "minerals"), ALL),
    ("color_rgb", "mineralogy", ("tint",), ALL),
]


def body(preset: dict) -> str:
    """The body a preset's grains are made from (a preset, or a grain's drawn parameters)."""
    return "sphere" if preset.get("sphere") else preset.get("kind") or "rock"


def columns(preset: dict) -> list[str]:
    """The drawn values a grain of this preset records."""
    return [name for name, _aspect, _rule, bodies in DECLARED if body(preset) in bodies]


def rule_text(rule) -> str:
    kind, *args = rule
    if kind == "normal":
        return f"normal, mean `{args[0]}`, sd `{args[1]}`"
    if kind == "diameter":
        return "2^−phi mm, from the drawn phi"
    if kind == "beta_min":
        return f"beta(`{args[0]}`), raised to `{args[1]}` ({args[2]:g} by default)"
    if kind == "integers":
        return f"whole number within `{args[0]}`, both included (0 if none)"
    if kind == "loguniform":
        return f"log-uniform within `{args[0]}`"
    if kind == "uniform":
        return f"uniform within `{args[0]}` (0 if none)"
    if kind == "taper":
        return "`taper`: t gives uniform −t to t, a pair keeps its sign (0 if none)"
    if kind == "weights":
        return f"one of the `{args[0]}`, with its weight"
    if kind == "tint":
        return "the mineral's colour × uniform 0.88 to 1.12, + normal(0, 0.02) per channel, within 0 to 1"
    raise ValueError(f"unknown rule {kind!r}")


def _pair(p, name):
    v = p.get(name)
    if v is None:
        return ""
    return f"{v[0]:g} to {v[1]:g}" if isinstance(v, tuple) else f"±{v:g}"


def table() -> str:
    """The Markdown of docs/variation.md between its markers: the rules, then the presets' numbers."""
    out = ["### Rules", "", "| Column | Aspect | Drawn as | Bodies that record it |", "|---|---|---|---|"]
    for name, aspect, rule, bodies in DECLARED:
        out.append(f"| `variation:{name}` | {aspect} | {rule_text(rule)} | {', '.join(bodies)} |")
    out += [
        "",
        "### The presets' numbers",
        "",
        "| Preset | Body | phi mean, sd | `elongation_beta` | `flatness_beta` | `aspect` | `lumpiness` "
        "| `taper` | `chips` | `pits` | `facets` | `roundness_p` | minerals |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for key, p in PRESETS.items():
        b = body(p)
        used = set(columns(p))

        def cell(col, text, used=used):
            return text if col in used else ""

        minerals = ", ".join(f"{m[0]} {m[1]:g}" for m in p["minerals"])
        out.append(
            f"| `{key}` | {b} | {p['phi_mean']:g}, {p['phi_std']:g} "
            f"| {cell('elongation', '{:g}, {:g}'.format(*p['elongation_beta']))} "
            f"| {cell('flatness', '{:g}, {:g}'.format(*p['flatness_beta']))} "
            f"| {cell('aspect_ratio', _pair(p, 'aspect'))} | {cell('lumpiness', _pair(p, 'lumpiness'))} "
            f"| {cell('taper', _pair(p, 'taper'))} | {cell('chips', _pair(p, 'chips'))} "
            f"| {cell('pits', _pair(p, 'pits'))} | {cell('facets', _pair(p, 'facets'))} "
            f"| {cell('roundness_p', _pair(p, 'roundness_p'))} | {minerals} |"
        )
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    print(table())
