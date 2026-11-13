"""Read what Granulaire wrote, with OpenUSD alone.

You do not need Granulaire to use a pack. Everything is in the OpenUSD file,
under the attribute namespace of the Primvaria contract:

    primvaria:generator, primvaria:preset, primvaria:seed   what made this asset
    primvaria:variation:<name>                              what was drawn for it
    primvaria:measured:<name>                               what was measured on it

This script generates a small pack, then opens it with pxr only, as a
simulator or a data pipeline would.

    python examples/03_read_the_usd_file.py
"""

import sys
from pathlib import Path

from pxr import Usd, UsdGeom, UsdPhysics

from granulaire import generate_scene, write_outputs

out = sys.argv[1] if len(sys.argv) > 1 else "output/examples"
folder = write_outputs(generate_scene("river_pebbles", shapes=5, copies=2, seed=7), out)
usd_file = next(Path(folder).glob("*.usd*"))

# ---- from here on, no Granulaire: only OpenUSD ----
stage = Usd.Stage.Open(str(usd_file))
units, up = UsdGeom.GetStageMetersPerUnit(stage), UsdGeom.GetStageUpAxis(stage)
print(f"{usd_file.name}: {units} m per unit, up axis {up}")

# An asset of the contract says which generator made it and which aspects varied.
grains = [p for p in stage.Traverse() if p.HasAttribute("primvaria:variation:aspects")]
aspects = grains[0].GetAttribute("primvaria:variation:aspects").Get()
made_by = grains[0].GetAttribute("primvaria:generator").Get()
print(f"{len(grains)} grains made by {made_by}, aspects that varied: {', '.join(aspects)}")

for prim in grains[:4]:
    drawn = prim.GetAttribute("primvaria:variation:diameter_m").Get()
    mass = prim.GetAttribute("primvaria:measured:mass_kg").Get()
    # The physics is standard UsdPhysics: any engine that reads OpenUSD finds it.
    body = "rigid body" if prim.HasAPI(UsdPhysics.RigidBodyAPI) else "no rigid body"
    print(f"  {prim.GetPath()}  drawn diameter {drawn * 1000:.1f} mm, mass {mass * 1000:.2f} g, {body}")
