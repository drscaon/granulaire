"""Prove that a pack is physically usable: drop the grains and let them settle.

The pile test builds a MuJoCo model from the OpenUSD file (shapes, masses,
friction and restitution are read from it), drops the grains on the ground and
checks that they come to rest: nothing flies away, nothing sinks into the
ground, no energy appears from nowhere. It is the test that runs on every
preset in Granulaire's continuous integration.

Needs MuJoCo:  pip install "granulaire[sim]"

    python examples/04_pile_test_in_mujoco.py
"""

import sys

from granulaire import generate_scene, write_outputs
from granulaire.sim import mujoco_test

out = sys.argv[1] if len(sys.argv) > 1 else "output/examples"
folder = write_outputs(generate_scene("glass_beads", shapes=10, copies=4, seed=1), out)

report = mujoco_test.run(folder)  # also written to <folder>/sim_test/sim_test.json
print(mujoco_test.summary(report))

# Each check is a yes or no; the report holds the numbers behind them.
for name, ok in report["checks"].items():
    print(f"  {'ok  ' if ok else 'FAIL'} {name}")
# Speeds are relative to the speed of a grain that falls from its own thickness.
print(
    f"pile height {report['pile_height_m'] * 1000:.1f} mm, fastest grain at rest: {report['max_speed_rel']:.4f}"
)

sys.exit(0 if report["passed"] else 1)
