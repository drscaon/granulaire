"""What the physics checks read from a generated OpenUSD scene.

Only the file is used, as an engine would: every grain under ``/World/Grains``
with its world transform, its collision mesh (convex hull approximation), its
mass (``UsdPhysics.MassAPI``, through the grain's moisture variant), friction
and restitution of its bound physics material, and the ground.

Grains are generated at their real size, down to 0.07 mm. Rigid-body engines
have absolute tolerances (collision margins, contact offsets, minimum masses
and inertias) tuned for objects of a few centimetres or more, so the checks
run the scene in **scaled units**: every length and the gravity are
multiplied by the same factor ``k_len``, and every mass by ``k_mass``. With
gravity and frictional contact as the only forces, this leaves the motion
unchanged in time (same Froude number ``v² / (g L)``, same mass ratios, same
friction and restitution coefficients); only the numbers the engine sees
change. Grains of a few centimetres run at their real scale (factors of 1).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from pxr import Usd, UsdGeom, UsdPhysics, UsdShade

G = 9.81  # m/s²


@dataclass
class Grain:
    name: str
    prototype: int
    points: np.ndarray  # collision mesh vertices in the grain frame (m)
    position: np.ndarray  # world position of the grain frame (m)
    quat: np.ndarray  # world orientation (w, x, y, z)
    mass: float  # kg
    friction: float
    restitution: float
    size: float  # nominal diameter (m)
    thickness: float  # smallest extent of the collision hull (m)


@dataclass
class Scene:
    path: Path
    preset: str
    grains: list[Grain]
    deformable: int  # grains with the OmniPhysics deformable schema (not rigid bodies)
    ground_half: float  # half side of the square ground (m)
    ground_friction: float
    ground_restitution: float
    k_len: float = 1.0
    k_mass: float = 1.0
    extra: dict = field(default_factory=dict)

    @property
    def size(self) -> float:
        """Median nominal diameter of the grains (m)."""
        return float(np.median([g.size for g in self.grains]))

    @property
    def thickness(self) -> float:
        """Median smallest extent of the grains (m): what matters for tunnelling."""
        return float(np.median([g.thickness for g in self.grains]))


def find_usd(path) -> Path:
    path = Path(path)
    if path.is_dir():
        found = sorted(path.glob("granulaire_*.usd*"))
        if not found:
            raise FileNotFoundError(f"no granulaire_*.usd* file in {path}")
        return found[0]
    return path


def _material(prim):
    mat, _ = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial("physics")
    if not mat:
        return 0.5, 0.0
    api = UsdPhysics.MaterialAPI(mat.GetPrim())
    mu = api.GetDynamicFrictionAttr().Get()
    e = api.GetRestitutionAttr().Get()
    return float(mu if mu is not None else 0.5), float(e if e is not None else 0.0)


def _extent_min(points: np.ndarray) -> float:
    """Smallest extent of a point cloud along its principal axes."""
    c = points - points.mean(axis=0)
    _, _, vt = np.linalg.svd(c, full_matrices=False)
    proj = c @ vt.T
    return float((proj.max(axis=0) - proj.min(axis=0)).min())


def read_scene(path, grains: int | None = None) -> Scene:
    """The rigid grains of a scene (the first ``grains`` of them when given)."""
    usd = find_usd(path)
    stage = Usd.Stage.Open(str(usd))
    cache = UsdGeom.XformCache()
    root = stage.GetPrimAtPath("/World/Grains")
    out, deformable = [], 0
    hulls: dict[int, tuple[np.ndarray, float]] = {}
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
        if proto not in hulls:
            pts = np.array(UsdGeom.Mesh(geom).GetPointsAttr().Get(), float)
            # the geom's transform relative to the grain (identity as generated)
            rel = np.array(
                cache.GetLocalToWorldTransform(geom) * cache.GetLocalToWorldTransform(prim).GetInverse()
            )
            pts = np.c_[pts, np.ones(len(pts))] @ rel
            hulls[proto] = (pts[:, :3], _extent_min(pts[:, :3]))
        pts, thick = hulls[proto]
        m = cache.GetLocalToWorldTransform(prim)
        q = m.ExtractRotationQuat()
        mu, e = _material(geom)
        out.append(
            Grain(
                name=prim.GetName(),
                prototype=proto,
                points=pts,
                position=np.array(m.ExtractTranslation(), float),
                quat=np.array([q.GetReal(), *q.GetImaginary()], float),
                mass=float(UsdPhysics.MassAPI(prim).GetMassAttr().Get()),
                friction=mu,
                restitution=e,
                size=float(prim.GetAttribute("granulaire:diameterNominal").Get()),
                thickness=thick,
            )
        )
        if grains is not None and len(out) >= grains:
            break
    ground = stage.GetPrimAtPath("/World/Ground")
    gpts = np.array(UsdGeom.Mesh(ground).GetPointsAttr().Get(), float)
    gmu, ge = _material(ground)
    preset = usd.stem.removeprefix("granulaire_")
    return Scene(usd, preset, out, deformable, float(np.abs(gpts[:, :2]).max()), gmu, ge)


def scale_units(scene: Scene, target_size: float, target_mass: float) -> Scene:
    """Choose the factors so that the median grain is at least ``target_size`` m
    and ``target_mass`` kg in the engine; factors are never below 1."""
    m = float(np.median([g.mass for g in scene.grains]))
    scene.k_len = max(1.0, target_size / scene.size)
    scene.k_mass = max(1.0, target_mass / m)
    return scene


def quat_to_matrix(q) -> np.ndarray:
    w, x, y, z = q
    return np.array(
        [
            [1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)],
            [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)],
            [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)],
        ]
    )
