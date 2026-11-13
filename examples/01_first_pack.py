"""Generate a first pack of grains and read its ground truth.

A pack is the folder Granulaire writes for one preset: an OpenUSD file with the
grains, and a table (instances.csv) with one row per grain. The table is read
back from the OpenUSD file, so the two cannot disagree.

Run it:

    python examples/01_first_pack.py            # writes under output/examples/
    python examples/01_first_pack.py some/dir   # or under a folder of your choice
"""

import sys

from granulaire import PRESETS, generate_scene, write_outputs
from granulaire.pack import read_manifest, read_table

out = sys.argv[1] if len(sys.argv) > 1 else "output/examples"

# The presets are the materials Granulaire knows: sands, gravels, seeds, pellets...
print(f"{len(PRESETS)} presets, for example: {', '.join(list(PRESETS)[:5])}")

# 8 distinct shapes, each placed 3 times: 24 grains. The seed fixes every random
# draw: the same call always gives the same grains.
scene = generate_scene("crushed_gravel", shapes=8, copies=3, seed=1)
folder = write_outputs(scene, out)
print(f"pack written to {folder}")

# manifest.json says what the pack is; its summary holds the global statistics.
manifest = read_manifest(folder)
summary = manifest["summary"]
grains, d50, mass = summary["grains"], summary["d50_mm"], summary["total_dry_mass_g"]
print(f"{grains} grains, median diameter {d50:.1f} mm, {mass:.1f} g in all")

# instances.csv is the ground truth of each grain: what was drawn for it
# (variation:*) and what was measured on its mesh once generated (measured:*).
rows = read_table(folder)
print(f"\n{'grain':8s} {'drawn diameter':>15s} {'measured mass':>14s} {'sphericity':>11s}  mineral")
for row in rows[:6]:
    diameter_mm = float(row["variation:diameter_m"]) * 1000
    mass_g = float(row["measured:mass_kg"]) * 1000
    sphericity = float(row["measured:sphericity"])
    print(
        f"{row['name']:8s} {diameter_mm:12.2f} mm {mass_g:11.3f} g {sphericity:11.2f}  {row['variation:mineral']}"
    )
