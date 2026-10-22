"""Command-line interface.

granulat list
granulat generate --preset beach_sand [--shapes 100] [--copies 5] [--seed 1]
                  [--no-size] [--no-shape] [--no-roundness] [--no-mineralogy]
                  [--no-orientation] [--moisture] [--moisture-weights 40,30,20,10]
granulat render output/beach_sand output/crushed_gravel
granulat render-moisture output/beach_pebbles output/crushed_gravel output/beach_sand
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import __version__, moisture
from .generator import Variations, generate_scene, moisture_applies, summarize, write_outputs
from .presets import CATEGORIES, PRESETS

VARIATION_HELP = {
    "size": "diameter from the grading curve (off: d50 for all)",
    "shape": "elongation and flatness drawn (off: mean values)",
    "roundness": "facets and edge rounding drawn (off: median values)",
    "mineralogy": "mineral and tint drawn (off: dominant mineral)",
    "orientation": "random orientation (off: all aligned)",
}


def _cmd_list(_args) -> int:
    for c in CATEGORIES:
        print(c)
        for k, p in PRESETS.items():
            if p["category"] == c:
                note = "" if p.get("moisture", True) else "  (no moisture)"
                print(f"  {k:<18} {p['label']:<30} ~{2.0 ** (-p['phi_mean']):.3g} mm{note}")
    return 0


def _cmd_generate(args) -> int:
    var = Variations(**{k: getattr(args, k) for k in VARIATION_HELP}, moisture=args.moisture)
    if args.moisture and not moisture_applies(args.preset):
        print(f"moisture ignored: not applicable to '{PRESETS[args.preset]['label']}'")
    scene = generate_scene(args.preset, args.shapes, args.copies, args.seed, var, args.moisture_weights)
    out = write_outputs(scene, args.out)
    summary = summarize(scene)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"written to {out}")
    return 0


def _cmd_render(args) -> int:
    from . import render

    folders = [Path(f) for f in args.folders]
    for folder in folders:
        print(render.shape_sheet(folder))
        print(render.mix_preview(folder))
    print(render.metrics_chart(folders[:6], folders[0].parent / "metrics.png"))
    return 0


def _cmd_render_moisture(args) -> int:
    from . import render

    folders = [Path(f) for f in args.folders]
    print(render.moisture_states(folders, folders[0].parent / "moisture_states.png"))
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="granulat", description="Procedural granular materials for simulation.")
    ap.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = ap.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="list presets by category").set_defaults(func=_cmd_list)

    g = sub.add_parser("generate", help="generate a grain library and an OpenUSD scene")
    g.add_argument("--preset", default="beach_sand", choices=sorted(PRESETS))
    g.add_argument("--shapes", type=int, default=100, help="number of distinct shapes")
    g.add_argument("--copies", type=int, default=5, help="copies of each shape")
    g.add_argument("--seed", type=int, default=1)
    g.add_argument("--out", default="output", help="output root folder")
    for name, text in VARIATION_HELP.items():
        g.add_argument(f"--{name}", action=argparse.BooleanOptionalAction, default=True, help=text)
    g.add_argument(
        "--moisture",
        action=argparse.BooleanOptionalAction,
        default=False,
        help='"moisture" variant set with a state drawn per grain',
    )
    g.add_argument(
        "--moisture-weights",
        default=moisture.DEFAULT_WEIGHTS,
        help="share of grains per state: dry,damp,wet,saturated",
    )
    g.set_defaults(func=_cmd_generate)

    r = sub.add_parser("render", help="shape sheet, mixed preview and metrics chart (needs [render])")
    r.add_argument("folders", nargs="+", help="output folders written by 'generate'")
    r.set_defaults(func=_cmd_render)

    rm = sub.add_parser("render-moisture", help="one grain per preset in the four moisture states")
    rm.add_argument("folders", nargs="+", help="output folders generated with --moisture")
    rm.set_defaults(func=_cmd_render_moisture)
    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
