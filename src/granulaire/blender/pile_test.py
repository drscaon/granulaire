"""Blender pile test for Granulaire scenes.

Runs inside Blender (it does not import granulaire, so Blender's own Python
needs nothing installed):

    blender -b -P pile_test.py -- output/crushed_gravel [--grains 40]

or, when the `bpy` module is installed (pip install bpy, Python 3.13):

    granulaire blender-test output/crushed_gravel

It:

1. imports the OpenUSD scene with Blender's USD importer (each grain becomes
   one mesh object, the ground too);
2. reads, with the OpenUSD Python bindings shipped with Blender, what the file
   says about each grain: mass (through its moisture variant), friction and
   restitution of its physics material, nominal size;
3. makes every grain an active rigid body with a convex hull collision shape
   (the file's ``convexHull`` approximation) and the ground a passive body,
   then lets the grains fall and settle;
4. checks the result (see below) and writes blender_test.json.

Scaled units: Bullet, Blender's physics engine, works best with objects of
0.1 m or more (its default collision margin is 0.04 m). Grains are imported
with every length multiplied by ``k`` and the gravity multiplied by ``k`` too,
and every mass by the same factor: gravity and frictional contact being the
only forces, the motion is the same in time as at real scale. Grains of 10 cm
or more run at their real scale.

Bullet multiplies the frictions (and restitutions) of the two bodies in
contact; each body gets the square root of its value, so that two grains of
the same material get exactly the file's value. Blender's default rigid body
damping (linear 0.04, angular 0.1) is kept, as a user would get it.

Checks, relative to the grain size so they mean the same for sand and
pebbles:

* ``imported``: every rigid grain of the file is a mesh object in Blender;
* ``mass``: the rigid bodies' total mass is the sum of the masses in the file;
* ``finite``: no invalid coordinate;
* ``ground``: no grain below the ground by more than a quarter of its
  thickness;
* ``overlap``: at rest, no grain's centre inside another grain's convex hull;
* ``energy``: potential + kinetic energy, sampled every frame, never above its
  initial value by more than 1 % of the energy released (no explosion);
* ``rest``: at the end, the fastest grain moves slower than 5 % of the speed
  of a fall from its own thickness, and the kinetic energy left is below
  0.1 % of the potential energy released.

Exit code 0 when every check passes, 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import bpy
import numpy as np
from pxr import Usd, UsdGeom, UsdPhysics, UsdShade

G = 9.81
TARGET_SIZE = 0.1  # m: grains are run at least this big
TARGET_MASS = 0.05  # kg
MAX_IMPORT_SCALE = 1000.0  # the largest scale Blender's USD importer accepts
MARGIN = 0.01  # collision margin, as a fraction of the grain size
SETTLE = 200  # settling time after the fall, in units of sqrt(size / g)
GROUND_TOL = 0.25  # of the grain thickness
ENERGY_TOL = 0.01  # of the energy released
REST_SPEED = 0.05  # of sqrt(2 g thickness)
REST_ENERGY = 1e-3  # of the energy released
FPS = 24
HULL_VERTICES = 64  # PhysX's default limit for a convex hull


# ----------------------------------------------------------------- inputs


def find_usd(path: Path) -> Path:
    if path.is_dir():
        found = sorted(path.glob("granulaire_*.usd*"))
        if not found:
            raise SystemExit(f"no granulaire_*.usd* file in {path}")
        return found[0]
    return path


def _material(prim):
    mat, _ = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial("physics")
    if not mat:
        return 0.5, 0.0
    api = UsdPhysics.MaterialAPI(mat.GetPrim())
    mu, e = api.GetDynamicFrictionAttr().Get(), api.GetRestitutionAttr().Get()
    return float(0.5 if mu is None else mu), float(0.0 if e is None else e)


def _thickness(points):
    c = points - points.mean(axis=0)
    _, _, vt = np.linalg.svd(c, full_matrices=False)
    p = c @ vt.T
    return float((p.max(axis=0) - p.min(axis=0)).min())


def read_grains(usd: Path, limit=None):
    """The rigid grains of the file: name, world position, mass, friction, restitution, size, thickness."""
    stage = Usd.Stage.Open(str(usd))
    cache = UsdGeom.XformCache()
    root = stage.GetPrimAtPath("/World/Grains")
    grains, deformable, thick = [], 0, {}
    for prim in root.GetChildren() if root else []:
        if prim.HasAttribute("omniphysics:mass"):
            deformable += 1
            continue
        if not prim.HasAPI(UsdPhysics.RigidBodyAPI):
            continue
        geom = next((c for c in prim.GetChildren() if c.HasAPI(UsdPhysics.CollisionAPI)), None)
        if geom is None:
            continue
        proto = int(prim.GetAttribute("granulaire:prototype").Get() or 0)
        if proto not in thick:
            thick[proto] = _thickness(np.array(UsdGeom.Mesh(geom).GetPointsAttr().Get(), float))
        mu, e = _material(geom)
        grains.append(
            {
                "name": prim.GetName(),
                "position": np.array(cache.GetLocalToWorldTransform(prim).ExtractTranslation(), float),
                "mass": float(UsdPhysics.MassAPI(prim).GetMassAttr().Get()),
                "friction": mu,
                "restitution": e,
                "size": float(prim.GetAttribute("granulaire:diameterNominal").Get()),
                "thickness": thick[proto],
            }
        )
        if limit and len(grains) >= limit:
            break
    ground = stage.GetPrimAtPath("/World/Ground")
    return grains, deformable, _material(ground)


# -------------------------------------------------------------- the scene


def world_points(o):
    me = o.data
    co = np.empty(len(me.vertices) * 3, np.float64)
    me.vertices.foreach_get("co", co)
    m = np.array(o.matrix_world)
    return co.reshape(-1, 3) @ m[:3, :3].T + m[:3, 3]


def hull_planes(o):
    """Outward planes (n, d) of the object's convex hull, in its local frame."""
    import bmesh  # importable once bpy is loaded

    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.convex_hull(bm, input=bm.verts)
    bm.faces.ensure_lookup_table()
    n = np.array([f.normal[:] for f in bm.faces])
    d = np.array([f.normal.dot(f.verts[0].co) for f in bm.faces])
    bm.free()
    return n, d


def _spread(points, n):
    """n of the points, each as far as possible from those already chosen."""
    if len(points) <= n:
        return points
    chosen = [int(np.argmax(np.linalg.norm(points - points.mean(axis=0), axis=1)))]
    d = np.linalg.norm(points - points[chosen[0]], axis=1)
    for _ in range(n - 1):
        chosen.append(int(np.argmax(d)))
        d = np.minimum(d, np.linalg.norm(points - points[chosen[-1]], axis=1))
    return points[chosen]


def to_hull(o, max_vertices=HULL_VERTICES):
    """Replace the object's mesh by its convex hull (the file's ``convexHull``
    collision approximation), reduced to at most ``max_vertices`` vertices as
    PhysX does by default: Bullet uses every point it is given."""
    import bmesh  # importable once bpy is loaded

    co = np.empty(len(o.data.vertices) * 3)
    o.data.vertices.foreach_get("co", co)
    pts = _spread(co.reshape(-1, 3), max_vertices)
    bm = bmesh.new()
    verts = [bm.verts.new(p) for p in pts]
    res = bmesh.ops.convex_hull(bm, input=verts)
    bmesh.ops.delete(bm, geom=list(set(res["geom_interior"]) | set(res["geom_unused"])), context="VERTS")
    bm.to_mesh(o.data)
    bm.free()


def to_slab(o):
    """Give the ground a thickness below its surface (half its width): a
    zero-thickness plane is unreliable in Bullet, small fast grains pass
    through it. The top surface stays where the file puts it."""
    import bmesh  # importable once bpy is loaded

    bm = bmesh.new()
    bm.from_mesh(o.data)
    width = max(v.co.x for v in bm.verts) - min(v.co.x for v in bm.verts)
    res = bmesh.ops.extrude_face_region(bm, geom=bm.faces[:])
    moved = [e for e in res["geom"] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=moved, vec=(0.0, 0.0, -0.5 * width))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(o.data)
    bm.free()


def run(target, out_dir=None, grains=None) -> dict:
    usd = find_usd(Path(target))
    out = Path(out_dir) if out_dir else usd.parent / "blender_test"
    out.mkdir(parents=True, exist_ok=True)
    data, deformable, (g_mu, g_e) = read_grains(usd, grains)
    if not data:
        raise SystemExit(f"{usd}: no rigid grain (deformable presets: generate with --no-deformable)")
    size = float(np.median([g["size"] for g in data]))
    thick = float(np.median([g["thickness"] for g in data]))
    k = min(MAX_IMPORT_SCALE, max(1.0, TARGET_SIZE / size))
    km = max(1.0, TARGET_MASS / float(np.median([g["mass"] for g in data])))
    grav = G * k

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.usd_import(filepath=str(usd), scale=k)
    sc = bpy.context.scene
    sc.render.fps = FPS
    sc.gravity = (0.0, 0.0, -grav)

    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    ground = next((o for o in meshes if o.name.startswith("Ground")), None)
    candidates = [o for o in meshes if o is not ground]
    # the importer names every grain "geom": match them to the file by position
    pos = (
        np.array([np.array(o.matrix_world.translation) for o in candidates])
        if candidates
        else np.zeros((0, 3))
    )
    objs, used = [], set()
    for g in data:
        j = int(np.argmin(np.linalg.norm(pos - g["position"] * k, axis=1)))
        if j in used or np.linalg.norm(pos[j] - g["position"] * k) > 0.05 * g["size"] * k:
            continue
        used.add(j)
        objs.append((g, candidates[j]))
    for o in candidates:  # grains beyond --grains are removed
        if o not in [b for _, b in objs]:
            bpy.data.objects.remove(o, do_unlink=True)

    bpy.ops.rigidbody.world_add()
    world = sc.rigidbody_world
    top = max(float(g["position"][2]) for g in data) * k
    v_impact = math.sqrt(2 * grav * top)
    dt = 0.1 * thick * k / v_impact
    world.substeps_per_frame = int(min(1000, max(10, math.ceil(1 / (FPS * dt)))))
    world.solver_iterations = 20
    world.use_split_impulse = True
    duration = math.sqrt(2 * top / grav) + SETTLE * math.sqrt(size * k / grav)
    frames = int(math.ceil(duration * FPS)) + 1
    sc.frame_start, sc.frame_end = 1, frames
    world.point_cache.frame_start, world.point_cache.frame_end = 1, frames

    # rigid bodies are top-level objects with the import scale applied to their
    # mesh: Blender's rigid bodies mishandle a scaled object under a strong
    # gravity (the grains fall through the ground)
    bodies = [o for _, o in objs] + ([ground] if ground is not None else [])
    for o in bodies:
        mw = o.matrix_world.copy()
        o.parent = None
        o.matrix_world = mw
    bpy.ops.object.select_all(action="DESELECT")
    for o in bodies:
        o.select_set(True)
    bpy.context.view_layer.objects.active = bodies[0]
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for _, o in objs:
        to_hull(o)
    bpy.ops.object.select_all(action="DESELECT")
    for _, o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0][1]
    bpy.ops.rigidbody.objects_add(type="ACTIVE")
    for g, o in objs:
        rb = o.rigid_body
        rb.collision_shape = "CONVEX_HULL"
        rb.mass = g["mass"] * km
        rb.friction = math.sqrt(g["friction"])
        rb.restitution = math.sqrt(g["restitution"])
        rb.use_margin = True
        rb.collision_margin = MARGIN * g["size"] * k
    if ground is not None:
        bpy.ops.object.select_all(action="DESELECT")
        ground.select_set(True)
        bpy.context.view_layer.objects.active = ground
        to_slab(ground)
        # Blender centres a box collider on the object's origin: put it at the slab's centre
        bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
        bpy.ops.rigidbody.objects_add(type="PASSIVE")
        ground.rigid_body.collision_shape = "BOX"
        ground.rigid_body.friction = math.sqrt(g_mu)
        ground.rigid_body.restitution = math.sqrt(g_e)
        ground.rigid_body.use_margin = True
        ground.rigid_body.collision_margin = MARGIN * size * k

    masses = np.array([o.rigid_body.mass for _, o in objs])
    z0 = np.array([o.matrix_world.translation.z for _, o in objs])
    e0 = float(np.sum(masses * grav * z0))
    e_max, prev = e0, None
    t0 = time.time()
    for f in range(1, frames + 1):
        sc.frame_set(f)
        cur = np.array([np.array(o.matrix_world.translation) for _, o in objs])
        if prev is not None:
            v = np.linalg.norm(cur - prev, axis=1) * FPS
            e = float(np.sum(masses * grav * cur[:, 2]) + 0.5 * np.sum(masses * v**2))
            e_max = max(e_max, e)
        prev, last = (cur if f < frames else prev), cur
    wall = time.time() - t0

    speed = np.linalg.norm(last - prev, axis=1) * FPS
    kinetic = 0.5 * float(np.sum(masses * speed**2))
    released = float(np.sum(masses * grav * (z0 - last[:, 2])))
    finite = bool(np.isfinite(last).all())
    lowest = np.array([world_points(o)[:, 2].min() for _, o in objs])
    thick_each = np.array([g["thickness"] for g, _ in objs]) * k
    # at rest, no grain's centre inside another grain's hull
    planes = {}
    inside = 0
    for i, (gi, oi) in enumerate(objs):
        near = np.nonzero(np.linalg.norm(last - last[i], axis=1) < 1.5 * gi["size"] * k)[0]
        for j in near:
            if j == i:
                continue
            oj = objs[j][1]
            if oj.data.name not in planes:
                planes[oj.data.name] = hull_planes(oj)
            n, d = planes[oj.data.name]
            local = np.array(oj.matrix_world.inverted() @ oi.matrix_world.translation)
            inside += bool((n @ local - d < 0).all())
    rest_speed = REST_SPEED * math.sqrt(2 * grav * thick * k)
    checks = {
        "imported": len(objs) == len(data),
        "mass": bool(abs(masses.sum() - sum(g["mass"] for g in data) * km) <= 1e-5 * masses.sum()),
        "finite": finite,
        "ground": bool(finite and (lowest >= -GROUND_TOL * thick_each).all()),
        "overlap": inside == 0,
        "energy": bool(e_max - e0 <= ENERGY_TOL * max(released, 1e-30)),
        "rest": bool(finite and speed.max() <= rest_speed and kinetic <= REST_ENERGY * max(released, 1e-30)),
    }
    report = {
        "engine": f"Blender {bpy.app.version_string}",
        "usd": str(usd),
        "preset": usd.stem.removeprefix("granulaire_"),
        "grains": len(objs),
        "deformable_skipped": deformable,
        "size_m": size,
        "thickness_m": thick,
        "length_factor": k,
        "mass_factor": km,
        "substeps_per_frame": world.substeps_per_frame,
        "frames": frames,
        "simulated_s": frames / FPS,
        "wall_s": round(wall, 2),
        "max_speed_rel": float(speed.max() / math.sqrt(2 * grav * thick * k)),
        "kinetic_over_released": kinetic / max(released, 1e-30),
        "energy_gain_over_released": (e_max - e0) / max(released, 1e-30),
        "lowest_point_rel": float((lowest / thick_each).min()),
        "centres_inside_another": inside,
        "checks": checks,
        "passed": all(checks.values()),
    }
    (out / "blender_test.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    report["report"] = str(out / "blender_test.json")
    return report


def summary(report) -> str:
    failed = [k for k, v in report["checks"].items() if not v]
    return (
        f"{'PASS' if report['passed'] else 'FAIL'}  {report['preset']:<17} {report['grains']:4d} grains  "
        f"x{report['length_factor']:.3g} length  {report['substeps_per_frame']} substeps  "
        f"speed {report['max_speed_rel']:.3f}  {report['wall_s']:.1f} s"
        + (f"  failed: {', '.join(failed)}" if failed else "")
    )


def build_parser():
    ap = argparse.ArgumentParser(prog="pile_test.py", description="Granulaire pile test in Blender")
    ap.add_argument("target", help="generated folder (or its granulaire_*.usdc file)")
    ap.add_argument("--out", default=None, help="output folder (default: <folder>/blender_test)")
    ap.add_argument("--grains", type=int, default=None, help="test only the first N grains")
    return ap


def main(argv=None) -> int:
    if argv is None:
        argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    args = build_parser().parse_args(argv)
    report = run(args.target, args.out, args.grains)
    print(summary(report))
    print(f"report: {report['report']}")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
