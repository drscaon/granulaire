"""Newton settings, as an OpenUSD layer over a file.

The main file holds plain OpenUSD and the standard `UsdPhysics` schemas. What Newton needs and
cannot guess from it is written here, in `<file>_newton.usda`: a layer whose only sublayer is the
main file and which adds, as `over`s on each prototype's collider (and so on every grain):

* `newton:contactGap`, the distance from which contacts are generated: a quarter of the
  prototype's smallest extent, at most GAP_MAX. Newton's own default, 0.1 m, is meant for robots:
  with grains it floods the contact buffer, and with sand it is a thousand grains wide.

Open the layer instead of the file to get both. Engines other than Newton ignore it. Packing
peanuts and cherry tomatoes stay rigid here: their deformable form is the OmniPhysics layer's.

    python -m granulaire.newton output/crushed_gravel     # check the layer of a pack

The check here is structural; Primvaria's CI opens the layers in Newton (scripts/newton_check.py).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from pxr import Sdf, Usd, UsdGeom, UsdPhysics

SUFFIX = "_newton"
GROUND = "/World/Ground"  # the shared ground carries no engine data (ground.py)
GAP = "newton:contactGap"
GAP_MAX = 0.0005  # m
GAP_SHARE = 0.25  # of the prototype's smallest extent
_F = Sdf.ValueTypeNames


def overlay_path(usd) -> Path:
    return Path(usd).with_name(f"{Path(usd).stem}{SUFFIX}.usda")


def _colliders(stage):
    """Every collider, prototypes (class prims) included, but the shared ground."""
    for prim in Usd.PrimRange.AllPrims(stage.GetPseudoRoot()):
        if prim.HasAPI(UsdPhysics.CollisionAPI) and prim.GetPath() != GROUND:
            yield prim


def contact_gap(prim) -> float:
    """A quarter of the collider's smallest extent, in metres, at most GAP_MAX."""
    points = np.asarray(UsdGeom.Mesh(prim).GetPointsAttr().Get(), dtype=float)
    m = UsdGeom.GetStageMetersPerUnit(prim.GetStage())
    return float(min(GAP_MAX, GAP_SHARE * np.ptp(points, axis=0).min() * m))


def write_overlay(usd) -> Path:
    """Write `<file>_newton.usda` beside an OpenUSD file and return its path."""
    usd = Path(usd)
    out = overlay_path(usd)
    out.unlink(missing_ok=True)
    layer = Sdf.Layer.CreateNew(str(out))
    layer.subLayerPaths.append(f"./{usd.name}")
    stage = Usd.Stage.Open(layer)
    base = Usd.Stage.Open(str(usd))
    UsdGeom.SetStageMetersPerUnit(stage, UsdGeom.GetStageMetersPerUnit(base))
    UsdGeom.SetStageUpAxis(stage, UsdGeom.GetStageUpAxis(base))
    UsdPhysics.SetStageKilogramsPerUnit(stage, UsdPhysics.GetStageKilogramsPerUnit(base))
    stage.SetDefaultPrim(stage.GetPrimAtPath(base.GetDefaultPrim().GetPath()))
    for prim in list(_colliders(stage)):
        if any(spec.path.ContainsPrimVariantSelection() for spec in prim.GetPrimStack()):
            continue  # a collider brought by a variant: none in Granulaire's files
        prim.CreateAttribute(GAP, _F.Float).Set(contact_gap(prim))
    layer.Save()
    return out


def check(path) -> list[str]:
    """Structural problems of a Newton layer (empty: none)."""
    path = Path(path)
    layer = Sdf.Layer.FindOrOpen(str(path))
    stem = path.stem.removesuffix(SUFFIX)
    main = next(
        (path.with_name(stem + ext) for ext in (".usdc", ".usda") if path.with_name(stem + ext).exists()),
        None,
    )
    if main is None:
        return [f"no file {stem}.usdc or {stem}.usda beside it"]
    if list(layer.subLayerPaths) != [f"./{main.name}"]:
        return [f"its only sublayer must be ./{main.name}"]
    problems = []
    base = Usd.Stage.Open(str(main))
    everything = Usd.PrimRange.AllPrims(base.GetPseudoRoot())
    if any(a.GetName().startswith("newton:") for p in everything for a in p.GetAttributes()):
        problems.append(f"{main.name} holds Newton data itself")
    stage = Usd.Stage.Open(str(path))
    base_paths = {p.GetPath() for p in Usd.PrimRange.AllPrims(base.GetPseudoRoot())}
    extra = [
        p.GetPath() for p in Usd.PrimRange.AllPrims(stage.GetPseudoRoot()) if p.GetPath() not in base_paths
    ]
    if extra:
        problems.append(f"defines prims the file does not have: {extra[0]}")
    for prim in _colliders(stage):
        gap = prim.GetAttribute(GAP).Get() if prim.HasAttribute(GAP) else None
        if gap is None:
            problems.append(f"{prim.GetPath()}: a collider without {GAP}")
        elif not 0 < gap <= GAP_MAX * (1 + 1e-6):  # a float attribute
            problems.append(f"{prim.GetPath()}: {GAP} {gap} m out of (0, {GAP_MAX}]")
    return problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Check the Newton layers (*_newton.usda) of packs or files.")
    ap.add_argument("paths", nargs="+", type=Path)
    args = ap.parse_args(argv)
    files = []
    for p in args.paths:
        files += sorted(p.rglob(f"*{SUFFIX}.usda")) if p.is_dir() else [p]
    if not files:
        print("no Newton layer found")
        return 1
    bad = 0
    for f in files:
        problems = check(f)
        bad += bool(problems)
        print(f"{'FAIL' if problems else 'ok  '} {f}")
        for line in problems[:10]:
            print(f"     {line}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
