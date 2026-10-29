"""Pile test in MuJoCo: the grains of a generated scene fall on the ground and must settle.

The model is built from the OpenUSD file only (see ``scene.py``): one free
body per grain, its collision mesh (MuJoCo collides with its convex hull, as
the file's ``convexHull`` approximation asks), its mass (inertia computed
from the convex hull, as engines do from the collider), its friction, and the
ground. The scene runs in scaled units (``scene.scale_units``) so that sand
and regolith grains stay above MuJoCo's numerical floors; the motion is the
same as at real scale.

Checks, all relative to the grain size so they mean the same for sand and
pebbles:

* ``mass``: the model's total mass is the sum of the masses in the file;
* ``finite``: no invalid position or velocity;
* ``ground``: no grain below the ground by more than a quarter of its
  thickness;
* ``overlap``: at rest, no contact deeper than a quarter of the median grain
  thickness; during the fall and the impacts, none deeper than half of it
  (a grain passing through another or through the ground would);
* ``energy``: the total energy (potential + kinetic) never rises above its
  initial value by more than 1 % of the energy released: the engine adds no
  energy (no explosion);
* ``rest``: at the end, the fastest grain moves slower than 5 % of the speed
  of a fall from its own thickness, and the kinetic energy left is below
  0.1 % of the potential energy released by the fall.

MuJoCo contacts are soft and have no restitution coefficient: the file's
restitution is not used here (it is in Blender and PhysX).

UsdPhysics has no rolling resistance, and without it a rounded pebble or a
cylindrical pellet on a flat floor rolls forever. Real granular materials
always have some (granular DEM models use a rolling friction coefficient of
about 0.01-0.1), so the test adds MuJoCo rolling friction of 2 % of the
grain thickness: a test setting, not a property of the asset.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

from .scene import G, Scene, read_scene, scale_units

TARGET_SIZE = 0.02  # m: grains are run at least this big (see scene.py)
TARGET_MASS = 1e-3  # kg
GROUND_TOL = 0.25  # of the grain thickness
OVERLAP_TOL = 0.25  # of the median grain thickness, at rest
IMPACT_TOL = 0.5  # of the median grain thickness, during the fall
ENERGY_TOL = 0.01  # of the energy released
REST_SPEED = 0.05  # of sqrt(2 g thickness)
REST_ENERGY = 1e-3  # of the potential energy released
ROLLING = 0.02  # rolling resistance, as a fraction of the grain thickness (see the docstring)
SETTLE = 200  # settling time after the fall, in units of sqrt(size / g)


def _f(v) -> str:
    return " ".join(f"{x:.9g}" for x in np.ravel(v))


def build_mjcf(scene: Scene, timestep: float) -> str:
    k, km = scene.k_len, scene.k_mass
    roll = ROLLING * scene.thickness * k
    assets, bodies, seen = [], [], set()
    for g in scene.grains:
        mesh = f"proto_{g.prototype}"
        if mesh not in seen:
            seen.add(mesh)
            assets.append(f'<mesh name="{mesh}" vertex="{_f(g.points * k)}" inertia="convex"/>')
        bodies.append(
            f'<body name="{g.name}" pos="{_f(g.position * k)}" quat="{_f(g.quat)}"><freejoint/>'
            f'<geom type="mesh" mesh="{mesh}" mass="{g.mass * km:.9g}" '
            f'friction="{g.friction:.6g} {roll:.6g} {roll:.6g}"/></body>'
        )
    half = scene.ground_half * k
    return (
        '<mujoco model="granulaire pile test">'
        f'<option timestep="{timestep:.6g}" gravity="0 0 {-G * k:.9g}" integrator="implicitfast" '
        'cone="elliptic" impratio="10"><flag energy="enable"/></option>'
        f'<default><geom solref="{2 * timestep:.6g} 1" condim="6"/></default>'
        f"<asset>{''.join(assets)}</asset><worldbody>"
        f'<geom name="ground" type="plane" size="{half:.9g} {half:.9g} {half:.9g}" '
        f'friction="{scene.ground_friction:.6g} 0.005 0.0001"/>'
        f"{''.join(bodies)}</worldbody></mujoco>"
    )


def run(target, out_dir=None, grains: int | None = None, settle: float = SETTLE) -> dict:
    import mujoco

    scene = scale_units(read_scene(target, grains), TARGET_SIZE, TARGET_MASS)
    if not scene.grains:
        raise ValueError(f"{scene.path}: no rigid grain (deformable presets: generate with --no-deformable)")
    k, km = scene.k_len, scene.k_mass
    g = G * k
    thick = scene.thickness * k
    top = max(float(gr.position[2]) for gr in scene.grains) * k
    v_impact = np.sqrt(2 * g * top)
    # a grain falls at most a tenth of its thickness per step
    dt = float(min(0.1 * thick / v_impact, 2e-3))
    duration = np.sqrt(2 * top / g) + settle * np.sqrt(scene.size * k / g)
    xml = build_mjcf(scene, dt)
    model = mujoco.MjModel.from_xml_string(xml)
    data = mujoco.MjData(model)
    mujoco.mj_forward(model, data)
    z0 = data.xipos[1:, 2].copy()
    masses = model.body_mass[1:]
    e0 = float(data.energy.sum())
    steps = int(np.ceil(duration / dt))
    deepest, e_max = 0.0, e0
    t0 = time.time()
    for i in range(steps):
        mujoco.mj_step(model, data)
        if i % 10 == 0:
            e_max = max(e_max, float(data.energy.sum()))
            if data.ncon:
                deepest = max(deepest, float(-data.contact.dist[: data.ncon].min()))
    wall = time.time() - t0
    mujoco.mj_forward(model, data)
    at_rest = float(-data.contact.dist[: data.ncon].min()) if data.ncon else 0.0

    pos = data.xpos[1:]
    vel = data.cvel[1:, 3:]  # linear velocity of each body (world frame)
    speed = np.linalg.norm(vel, axis=1)
    kinetic = 0.5 * float(np.sum(masses * speed**2))
    released = float(np.sum(masses * g * (z0 - data.xipos[1:, 2])))
    # lowest point of each grain's hull, in the engine's units
    lowest = []
    for j, gr in enumerate(scene.grains):
        R = data.xmat[j + 1].reshape(3, 3)
        lowest.append(float((gr.points * k @ R.T + pos[j])[:, 2].min()))
    lowest = np.array(lowest)
    thick_each = np.array([gr.thickness for gr in scene.grains]) * k
    half = scene.ground_half * k
    finite = bool(np.isfinite(data.qpos).all() and np.isfinite(data.qvel).all())
    rest_speed = REST_SPEED * np.sqrt(2 * g * thick)
    total_usd = sum(gr.mass for gr in scene.grains) * km
    checks = {
        "mass": bool(abs(masses.sum() - total_usd) <= 1e-6 * total_usd),
        "finite": finite,
        "ground": bool(finite and (lowest >= -GROUND_TOL * thick_each).all()),
        "overlap": bool(at_rest <= OVERLAP_TOL * thick and deepest <= IMPACT_TOL * thick),
        "energy": bool(e_max - e0 <= ENERGY_TOL * max(released, 1e-30)),
        "rest": bool(finite and speed.max() <= rest_speed and kinetic <= REST_ENERGY * max(released, 1e-30)),
    }
    report = {
        "engine": f"MuJoCo {mujoco.__version__}",
        "usd": str(scene.path),
        "preset": scene.preset,
        "grains": len(scene.grains),
        "deformable_skipped": scene.deformable,
        "size_m": scene.size,
        "thickness_m": scene.thickness,
        "length_factor": k,
        "mass_factor": km,
        "timestep_s": dt,
        "simulated_s": steps * dt,
        "wall_s": round(wall, 2),
        "max_speed_rel": float(speed.max() / np.sqrt(2 * g * thick)),
        "kinetic_over_released": kinetic / max(released, 1e-30),
        "deepest_contact_rel": deepest / thick,
        "contact_at_rest_rel": at_rest / thick,
        "energy_gain_over_released": (e_max - e0) / max(released, 1e-30),
        "off_ground": int((np.abs(pos[:, :2]) > half).any(axis=1).sum()),
        "lowest_point_rel": float((lowest / thick_each).min()),
        "pile_height_m": float((pos[:, 2].max()) / k),
        "checks": checks,
        "passed": all(checks.values()),
    }
    out = Path(out_dir) if out_dir else scene.path.parent / "sim_test"
    out.mkdir(parents=True, exist_ok=True)
    (out / "mujoco_pile.xml").write_text(xml + "\n", encoding="utf-8")
    (out / "sim_test.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    report["report"] = str(out / "sim_test.json")
    return report


def summary(report: dict) -> str:
    c = report["checks"]
    status = "PASS" if report["passed"] else "FAIL"
    failed = [k for k, v in c.items() if not v]
    return (
        f"{status}  {report['preset']:<17} {report['grains']:4d} grains  "
        f"x{report['length_factor']:.3g} length  dt {report['timestep_s'] * 1e3:.3g} ms  "
        f"speed {report['max_speed_rel']:.3f}  contact {report['deepest_contact_rel']:.3f}  "
        f"{report['wall_s']:.1f} s" + (f"  failed: {', '.join(failed)}" if failed else "")
    )
