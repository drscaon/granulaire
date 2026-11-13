"""Change one thing and nothing else: the "checkboxes" of Granulaire.

Each property that varies from grain to grain (size, shape, roundness,
mineralogy, orientation) is an aspect with its own random stream. Turning one
aspect off leaves the draws of the others as they were. With the same seed you
therefore get the same scene with a single difference, which is what you want
when you study what a robot or a perception model is sensitive to.

Here: the same gravel twice, the second time with every grain at the median
size. Shapes and minerals stay the same, grain for grain.

    python examples/02_one_aspect_at_a_time.py
"""

from granulaire import Variations, generate_scene

SEED = 3

varied = generate_scene("crushed_gravel", shapes=6, copies=1, seed=SEED)
same_size = generate_scene("crushed_gravel", shapes=6, copies=1, seed=SEED, variations=Variations(size=False))

print(f"{'shape':6s} {'diameter (mm)':>22s} {'elongation':>18s}  mineral")
print(f"{'':6s} {'varied':>10s} {'size off':>11s} {'varied':>9s} {'size off':>8s}")
for i, (a, b) in enumerate(zip(varied.prototypes, same_size.prototypes, strict=True)):
    pa, pb = a["params"], b["params"]
    print(
        f"{i:<6d} {pa['diameter_m'] * 1000:10.2f} {pb['diameter_m'] * 1000:11.2f} "
        f"{pa['elongation']:9.3f} {pb['elongation']:8.3f}  {a['mineral']} / {b['mineral']}"
    )

# The size column changed; the others did not.
assert len({p["params"]["diameter_m"] for p in same_size.prototypes}) == 1
assert [p["params"]["elongation"] for p in varied.prototypes] == [
    p["params"]["elongation"] for p in same_size.prototypes
]
assert [p["mineral"] for p in varied.prototypes] == [p["mineral"] for p in same_size.prototypes]
print("\nsame seed, size switched off: one diameter for all, shapes and minerals unchanged")
