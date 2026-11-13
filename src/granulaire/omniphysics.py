"""Deformable grains for NVIDIA OmniPhysics (Omniverse, Isaac Sim 5+), as a layer over the file.

Core OpenUSD has no deformable-body schema yet (UsdPhysics covers rigid bodies). The main
file therefore holds packing peanuts and cherry tomatoes as rigid bodies, like every other
grain, and what makes them deformable is written here, in `<file>_omniphysics.usdc`: a layer
whose only sublayer is the main file. On each prototype (and so on every grain) it

* takes the rigid body away: `PhysicsRigidBodyAPI` and `PhysicsMassAPI` removed from the root,
  the convex-hull collider deactivated;
* makes the root a deformable body (`OmniPhysicsDeformableBodyAPI`, `omniphysics:mass`);
* adds the simulation mesh `sim`, a `UsdGeom.TetMesh` with `OmniPhysicsVolumeDeformableSimAPI`
  and the collider, and skins the render mesh to it through a bind pose;
* binds a deformable material (`/World/Looks/Soft[_<state>]`: Young's modulus, Poisson's
  ratio, density, friction, PhysX elasticity damping).

With moisture states, mass and material are written inside each `moisture` variant, as in
the file. The API schemas are applied by name: the layer is valid OpenUSD for any tool.

Open the layer instead of the file (Isaac Sim: File > Open).

    python -m granulaire.omniphysics output/packing_peanuts     # check the layer of a pack

Not simulated here: OmniPhysics needs Isaac Sim and an NVIDIA RTX GPU. The check is structural.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from pxr import Gf, Sdf, Usd, UsdGeom, UsdPhysics, UsdShade, Vt

from .moisture import STATE_PARAMS

SUFFIX = "_omniphysics"
BODY_API = "OmniPhysicsDeformableBodyAPI"
SIM_API = "OmniPhysicsVolumeDeformableSimAPI"
POSE_API = "OmniPhysicsDeformablePoseAPI:custom"
MATERIAL_APIS = (
    "OmniPhysicsBaseMaterialAPI",
    "OmniPhysicsDeformableMaterialAPI",
    "PhysxDeformableMaterialAPI",
)
RIGID_APIS = ("PhysicsRigidBodyAPI", "PhysicsMassAPI")
_F = Sdf.ValueTypeNames


def overlay_path(usd) -> Path:
    return Path(usd).with_name(f"{Path(usd).stem}{SUFFIX}.usdc")  # binary: tetrahedral meshes are large


def _material(stage, path, friction, density, soft):
    """Deformable material: OmniPhysics elasticity on top of the OmniPhysics base material, plus
    PhysX elasticity damping (1/s), which sets how much a deformable grain bounces back."""
    prim = UsdShade.Material.Define(stage, path).GetPrim()
    for schema in MATERIAL_APIS:
        prim.AddAppliedSchema(schema)
    for name, value in [
        ("omniphysics:youngsModulus", soft["youngs_modulus"]),
        ("omniphysics:poissonsRatio", soft["poissons_ratio"]),
        ("omniphysics:density", density),
        # PhysX deformables ignore static friction: use dynamic friction
        ("omniphysics:dynamicFriction", friction),
        ("omniphysics:staticFriction", friction),
        ("physxDeformableMaterial:elasticityDamping", soft.get("elasticity_damping", 0.0)),
    ]:
        prim.CreateAttribute(name, _F.Float).Set(float(value))
    return UsdShade.Material(prim)


def _bind_pose(prim, points):
    prim.AddAppliedSchema(POSE_API)
    prim.CreateAttribute("deformablePose:custom:omniphysics:purposes", _F.TokenArray).Set(["bindPose"])
    prim.CreateAttribute("deformablePose:custom:omniphysics:points", _F.Point3fArray).Set(
        Vt.Vec3fArray.FromNumpy(points.astype(np.float32))
    )


def _tet_mesh(stage, path, points, tets):
    tet = UsdGeom.TetMesh.Define(stage, path)
    pts = Vt.Vec3fArray.FromNumpy(points.astype(np.float32))
    idx = Vt.Vec4iArray.FromNumpy(tets.astype(np.int32))
    tet.CreatePointsAttr(pts)
    tet.CreateTetVertexIndicesAttr(idx)
    tet.CreateSurfaceFaceVertexIndicesAttr(UsdGeom.TetMesh.ComputeSurfaceFaces(tet))
    tet.CreateExtentAttr([Gf.Vec3f(*points.min(axis=0)), Gf.Vec3f(*points.max(axis=0))])
    prim = tet.GetPrim()
    prim.AddAppliedSchema(SIM_API)
    prim.CreateAttribute("omniphysics:restShapePoints", _F.Point3fArray).Set(pts)
    prim.CreateAttribute("omniphysics:restTetVtxIndices", _F.Int4Array).Set(idx)
    _bind_pose(prim, points)
    UsdPhysics.CollisionAPI.Apply(prim)
    tet.CreatePurposeAttr(UsdGeom.Tokens.guide)  # simulation mesh: hidden in renders


def write_overlay(usd, preset, prototypes, states=None) -> Path:
    """Write `<file>_omniphysics.usdc` beside the file exported from the same prototypes (each
    with its tet_points and tets), and return its path."""
    usd = Path(usd)
    soft = preset["deformable"]
    out = overlay_path(usd)
    out.unlink(missing_ok=True)
    layer = Sdf.Layer.CreateNew(str(out))
    layer.subLayerPaths.append(f"./{usd.name}")
    stage = Usd.Stage.Open(layer)
    UsdGeom.SetStageMetersPerUnit(stage, 1.0)
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
    UsdPhysics.SetStageKilogramsPerUnit(stage, 1.0)
    stage.SetDefaultPrim(stage.GetPrimAtPath("/World"))
    mu = preset.get("friction", 0.6)
    materials = {
        s: _material(
            stage,
            f"/World/Looks/Soft_{s}" if s else "/World/Looks/Soft",
            mu * (STATE_PARAMS[s]["mu"] if s else 1.0),
            preset["density"],
            soft,
        )
        for s in (states or [None])
    }
    for i, proto in enumerate(prototypes):
        root = stage.GetPrimAtPath(f"/World/Prototypes/Grain_{i:03d}")
        for api in RIGID_APIS:  # no longer a rigid body
            root.RemoveAppliedSchema(api)
        root.GetChild("collision").SetActive(False)  # nor its convex-hull collider
        root.AddAppliedSchema(BODY_API)
        root.CreateAttribute("omniphysics:deformableBodyEnabled", _F.Bool).Set(True)
        mass = root.CreateAttribute("omniphysics:mass", _F.Float)
        UsdShade.MaterialBindingAPI.Apply(root)
        _bind_pose(root.GetChild("geom"), proto["verts"])  # render mesh skinned to the simulation mesh
        _tet_mesh(stage, f"{root.GetPath()}/sim", proto["tet_points"], proto["tets"])

        def bind(material, root=root):
            UsdShade.MaterialBindingAPI(root).Bind(material, UsdShade.Tokens.weakerThanDescendants, "physics")

        if not states:
            mass.Set(float(proto["mass"]))
            bind(materials[None])
            continue
        vset = root.GetVariantSet("moisture")  # mass and material differ by state, as in the file
        for s in states:
            with Usd.EditContext(stage, stage.GetSessionLayer()):
                vset.SetVariantSelection(s)
            with Usd.EditContext(stage, vset.GetVariantEditTarget(layer)):
                mass.Set(float(proto["moisture"][s]["mass"]))
                bind(materials[s])
    stage.GetSessionLayer().Clear()
    layer.Save()
    return out


def _schemas(prim) -> list[str]:
    """Applied API schemas as composed, including ones not registered in this OpenUSD build."""
    listed = prim.GetMetadata("apiSchemas")
    return list(listed.ApplyOperations([])) if listed else []


def engine_data(stage) -> list[str]:
    """What a stage holds that only OmniPhysics or PhysX read: 'path: name' lines (empty for a main file)."""
    found = []
    for prim in Usd.PrimRange.AllPrims(stage.GetPseudoRoot()):
        found += [f"{prim.GetPath()}: {s}" for s in _schemas(prim) if s.startswith(("OmniPhysics", "Physx"))]
        names = [a.GetName() for a in prim.GetAttributes()]
        found += [f"{prim.GetPath()}: {n}" for n in names if "omniphysics:" in n or n.startswith("physx")]
    return found


def check(path) -> list[str]:
    """Structural problems of an OmniPhysics layer (empty: none)."""
    path = Path(path)
    main = path.with_name(path.stem.removesuffix(SUFFIX) + ".usdc")
    layer = Sdf.Layer.FindOrOpen(str(path))
    if list(layer.subLayerPaths) != [f"./{main.name}"]:
        return [f"its only sublayer must be ./{main.name}"]
    problems = []
    base = Usd.Stage.Open(str(main))
    if engine_data(base):
        problems.append(f"{main.name} holds engine data itself")
    stage = Usd.Stage.Open(str(path))
    grains = stage.GetPrimAtPath("/World/Grains").GetChildren()
    if not grains:
        problems.append("no grain")
    states = [None]
    if grains and grains[0].HasVariantSets() and grains[0].GetVariantSets().HasVariantSet("moisture"):
        states = grains[0].GetVariantSet("moisture").GetVariantNames()
    for state in states:
        for grain in grains:
            name = f"{grain.GetName()}[{state}]" if state else grain.GetName()
            if state:
                with Usd.EditContext(stage, stage.GetSessionLayer()):
                    grain.GetVariantSet("moisture").SetVariantSelection(state)
            schemas = _schemas(grain)
            if BODY_API not in schemas or any(api in schemas for api in RIGID_APIS):
                problems.append(f"{name}: must be a deformable body and no longer a rigid one")
            if grain.GetChild("collision").IsActive():
                problems.append(f"{name}: the rigid collider is still active")
            mass = grain.GetAttribute("omniphysics:mass").Get()
            rigid = base.GetPrimAtPath(grain.GetPath())
            if state:
                with Usd.EditContext(base, base.GetSessionLayer()):
                    rigid.GetVariantSet("moisture").SetVariantSelection(state)
            expected = rigid.GetAttribute("physics:mass").Get()
            if mass is None or expected is None or abs(mass - expected) > 1e-6 * max(expected, 1e-12):
                problems.append(f"{name}: mass {mass} differs from the file's {expected}")
            sim = grain.GetChild("sim")
            if (
                not sim.IsA(UsdGeom.TetMesh)
                or SIM_API not in _schemas(sim)
                or not sim.HasAPI(UsdPhysics.CollisionAPI)
            ):
                problems.append(f"{name}: no simulation mesh with its collider")
                continue
            tets = np.array(sim.GetAttribute("tetVertexIndices").Get())
            rest = sim.GetAttribute("omniphysics:restTetVtxIndices").Get()
            if rest is None or not np.array_equal(tets, np.array(rest)) or len(tets) == 0:
                problems.append(f"{name}: rest tetrahedra differ from the mesh")
            if POSE_API not in _schemas(grain.GetChild("geom")):
                problems.append(f"{name}: render mesh without a bind pose")
            material = UsdShade.MaterialBindingAPI(grain).ComputeBoundMaterial("physics")[0]
            if not material or any(api not in _schemas(material.GetPrim()) for api in MATERIAL_APIS):
                problems.append(f"{name}: no deformable material")
            elif not material.GetPrim().GetAttribute("omniphysics:youngsModulus").Get() > 0:
                problems.append(f"{name}: Young's modulus not positive")
    stage.GetSessionLayer().Clear()
    return problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Check the OmniPhysics layers (*_omniphysics.usdc) of packs or files."
    )
    ap.add_argument("paths", nargs="+", type=Path)
    args = ap.parse_args(argv)
    files = []
    for p in args.paths:
        files += sorted(p.rglob(f"*{SUFFIX}.usd*")) if p.is_dir() else [p]
    if not files:
        print("no OmniPhysics layer found")
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
