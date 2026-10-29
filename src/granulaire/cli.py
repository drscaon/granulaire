"""Command-line interface.

granulaire list
granulaire generate --preset beach_sand [--shapes 100] [--copies 5] [--no-shuffle] [--seed 1]
                  [--no-size] [--no-shape] [--no-roundness] [--no-mineralogy]
                  [--no-orientation] [--moisture] [--moisture-weights 40,30,20,10]
granulaire render output/beach_sand output/crushed_gravel
granulaire render-moisture output/beach_pebbles output/crushed_gravel output/beach_sand
granulaire sim-test output/crushed_gravel [--grains 40]        (MuJoCo, needs [sim])
granulaire blender-test output/crushed_gravel [--grains 40]    (Blender, needs bpy)
granulaire blender-script
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from . import __version__, moisture
from .generator import Variations, generate_scene, moisture_applies, summarize, write_outputs
from .presets import CATEGORIES, PRESETS

VARIATION_HELP = {
    "size": "diameter from the grading curve (off: d50 for all)",
    "shape": "elongation, flatness and irregularity drawn (off: mean values)",
    "roundness": "facets and edge rounding drawn (off: median values)",
    "mineralogy": "mineral and tint drawn (off: dominant mineral)",
    "orientation": "random orientation (off: all aligned)",
}


def _cmd_list(_args) -> int:
    for c in CATEGORIES:
        print(c)
        for k, p in PRESETS.items():
            if p["category"] == c:
                notes = [] if p.get("moisture", True) else ["no moisture"]
                if p.get("deformable"):
                    notes.append("deformable")
                note = f"  ({', '.join(notes)})" if notes else ""
                print(f"  {k:<18} {p['label']:<30} ~{2.0 ** (-p['phi_mean']):.3g} mm{note}")
    return 0


def _positive_int(text: str) -> int:
    value = int(text)
    if value < 1:
        raise argparse.ArgumentTypeError(f"must be at least 1, got {value}")
    return value


def _cmd_generate(args) -> int:
    var = Variations(**{k: getattr(args, k) for k in VARIATION_HELP}, moisture=args.moisture)
    if args.moisture and not moisture_applies(args.preset):
        print(f"moisture ignored: not applicable to '{PRESETS[args.preset]['label']}'")
    scene = generate_scene(
        args.preset,
        args.shapes,
        args.copies,
        args.seed,
        var,
        args.moisture_weights,
        args.deformable,
        args.shuffle,
    )
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


def _cmd_render_gallery(args) -> int:
    from . import render

    folders = [Path(f) for f in args.folders]
    out = Path(args.output) if args.output else folders[0].parent / "moisture_gallery.png"
    print(render.moisture_gallery(folders, out, grains=args.grains))
    return 0


def _cmd_sim_test(args) -> int:
    try:
        from .sim import mujoco_test
    except ImportError:
        print('MuJoCo is needed: pip install "granulaire[sim]"', file=sys.stderr)
        return 2
    code = 0
    for folder in args.folders:
        report = mujoco_test.run(folder, args.out, args.grains)
        print(mujoco_test.summary(report))
        code |= not report["passed"]
    return code


def _blender_script() -> Path:
    return Path(__file__).parent / "blender" / "pile_test.py"


def _cmd_blender_test(args) -> int:
    forwarded = []
    if args.grains:
        forwarded += ["--grains", str(args.grains)]
    if args.out:
        forwarded += ["--out", args.out]
    code = 0
    for folder in args.folders:
        try:
            import bpy  # noqa: F401
        except ImportError:
            blender = shutil.which("blender")
            if blender is None:
                print(
                    "Blender is needed: install the bpy module (Python 3.13) or put blender on the PATH, "
                    f'or run: blender -b -P "{_blender_script()}" -- {folder}',
                    file=sys.stderr,
                )
                return 2
            cmd = [blender, "-b", "-P", str(_blender_script()), "--", folder, *forwarded]
            code |= subprocess.call(cmd)
        else:
            from .blender import pile_test

            code |= pile_test.main([folder, *forwarded])
    return code


def _cmd_blender_script(_args) -> int:
    print(_blender_script())
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="granulaire",
        description="Realistic granular assets generator for Physical AI, exporting to OpenUSD.",
    )
    ap.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = ap.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="list presets by category").set_defaults(func=_cmd_list)

    g = sub.add_parser("generate", help="generate a grain library and an OpenUSD scene")
    g.add_argument("--preset", default="beach_sand", choices=sorted(PRESETS))
    g.add_argument(
        "--shapes", type=_positive_int, default=100, help="number of distinct shapes (default: 100)"
    )
    g.add_argument("--copies", type=_positive_int, default=5, help="copies of each shape (default: 5)")
    g.add_argument(
        "--shuffle",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="mix the copies in random order (--no-shuffle: copies of each shape side by side)",
    )
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
    g.add_argument(
        "--deformable",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="deformable presets (packing peanuts): TetMesh + NVIDIA OmniPhysics deformable schema, "
        "simulated only by Omniverse / Isaac Sim (off: rigid bodies for any engine)",
    )
    g.set_defaults(func=_cmd_generate)

    r = sub.add_parser("render", help="shape sheet, mixed preview and metrics chart (needs [render])")
    r.add_argument("folders", nargs="+", help="output folders written by 'generate'")
    r.set_defaults(func=_cmd_render)

    rm = sub.add_parser("render-moisture", help="one grain per preset in the four moisture states")
    rm.add_argument("folders", nargs="+", help="output folders generated with --moisture")
    rm.set_defaults(func=_cmd_render_moisture)

    rg = sub.add_parser("render-gallery", help="several grains per preset in every moisture state")
    rg.add_argument("folders", nargs="+", help="output folders written by 'generate'")
    rg.add_argument("--grains", type=int, default=5, help="grains shown per preset and state")
    rg.add_argument("--output", help="image path (default: <root>/moisture_gallery.png)")
    rg.set_defaults(func=_cmd_render_gallery)

    s = sub.add_parser("sim-test", help="pile test in MuJoCo, read back from the OpenUSD file (needs [sim])")
    s.add_argument("folders", nargs="+", help="output folders written by 'generate'")
    s.add_argument("--grains", type=_positive_int, default=None, help="test only the first N grains")
    s.add_argument("--out", default=None, help="report folder (default: <folder>/sim_test)")
    s.set_defaults(func=_cmd_sim_test)

    b = sub.add_parser("blender-test", help="pile test in Blender, through Blender's USD importer")
    b.add_argument("folders", nargs="+", help="output folders written by 'generate'")
    b.add_argument("--grains", type=_positive_int, default=None, help="test only the first N grains")
    b.add_argument("--out", default=None, help="report folder (default: <folder>/blender_test)")
    b.set_defaults(func=_cmd_blender_test)

    sub.add_parser(
        "blender-script", help="print the path of the Blender pile-test script, to run with Blender"
    ).set_defaults(func=_cmd_blender_script)
    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
