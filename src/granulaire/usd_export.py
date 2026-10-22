"""OpenUSD export: a library of prototypes plus grains that reference them.

Scene layout (units: metres, kilograms, Z up):

/World
  /PhysicsScene
  /Looks/Mat_000[_<state>]     UsdPreviewSurface materials (prototype x state)
  /Looks/Phys[_<state>]        physics materials (friction, restitution)
  /Prototypes        (class)   N shapes, not rendered directly
    /Grain_000                 RigidBody + Mass + granulaire:* attributes
      variantSet "moisture"    (when enabled) dry | damp | wet | saturated:
                               mass, granulaire:waterMass,
                               granulaire:capillaryCohesion, bound materials
      /geom                    Mesh + Collision (convex hull)
  /Grains
    /g_0000 ...                internal reference to a prototype, with its own
                               position, orientation and moisture state
  /Ground                      static collision plane

Composition rule relied on: a local opinion is stronger than a variant. When
moisture is enabled, mass and material bindings are therefore authored ONLY
inside the variants, never directly on the prototype; each grain picks its
variant through a local selection.

Deformable grains (packing peanuts). Core OpenUSD has no deformable-body
schema yet (UsdPhysics covers rigid bodies), so these follow NVIDIA's
OmniPhysics deformable schema (Omniverse / Isaac Sim 5), built on the core
UsdGeom.TetMesh. The API schemas are applied by name: the file stays valid
OpenUSD for any tool, and engines that know the schema simulate it.

  /Grain_000                   Xform + OmniPhysicsDeformableBodyAPI
                               (omniphysics:mass), physics material bound
    /geom                      render Mesh + OmniPhysicsDeformablePoseAPI:custom
    /sim                       TetMesh + OmniPhysicsVolumeDeformableSimAPI
                               + OmniPhysicsDeformablePoseAPI:custom
                               + UsdPhysics CollisionAPI (single collider)
  /Looks/Phys[_<state>]        OmniPhysicsDeformableMaterialAPI: Young's
                               modulus, Poisson's ratio, density, friction
"""

import numpy as np
import trimesh
from pxr import Gf, Sdf, Usd, UsdGeom, UsdPhysics, UsdShade, Vt

from .moisture import STATE_PARAMS, wet_color


def _make_material(stage, path, color, roughness, clearcoat=0.0):
    mat = UsdShade.Material.Define(stage, path)
    shader = UsdShade.Shader.Define(stage, path + "/Surface")
    shader.CreateIdAttr("UsdPreviewSurface")
    shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*color))
    shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(float(roughness))
    shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)
    if clearcoat > 0:
        shader.CreateInput("clearcoat", Sdf.ValueTypeNames.Float).Set(float(clearcoat))
        shader.CreateInput("clearcoatRoughness", Sdf.ValueTypeNames.Float).Set(0.05)
    mat.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
    return mat


def _make_phys_material(stage, path, friction, restitution):
    mat = UsdShade.Material.Define(stage, path)
    pm = UsdPhysics.MaterialAPI.Apply(mat.GetPrim())
    pm.CreateStaticFrictionAttr(float(friction))
    pm.CreateDynamicFrictionAttr(float(friction) * 0.9)
    pm.CreateRestitutionAttr(float(restitution))
    return mat


def _make_deformable_material(stage, path, friction, density, youngs_modulus, poissons_ratio):
    mat = UsdShade.Material.Define(stage, path)
    prim = mat.GetPrim()
    prim.AddAppliedSchema("OmniPhysicsDeformableMaterialAPI")
    for name, value in [
        ("omniphysics:youngsModulus", youngs_modulus),
        ("omniphysics:poissonsRatio", poissons_ratio),
        ("omniphysics:density", density),
        # PhysX deformables ignore static friction: use dynamic friction
        ("omniphysics:dynamicFriction", friction),
        ("omniphysics:staticFriction", friction),
    ]:
        prim.CreateAttribute(name, Sdf.ValueTypeNames.Float).Set(float(value))
    return mat


def _set_bind_pose(prim, points):
    prim.AddAppliedSchema("OmniPhysicsDeformablePoseAPI:custom")
    prim.CreateAttribute("deformablePose:custom:omniphysics:purposes", Sdf.ValueTypeNames.TokenArray).Set(
        ["bindPose"]
    )
    prim.CreateAttribute("deformablePose:custom:omniphysics:points", Sdf.ValueTypeNames.Point3fArray).Set(
        Vt.Vec3fArray.FromNumpy(points.astype(np.float32))
    )


def _make_tet_mesh(stage, path, points, tets):
    tet = UsdGeom.TetMesh.Define(stage, path)
    pts = Vt.Vec3fArray.FromNumpy(points.astype(np.float32))
    idx = Vt.Vec4iArray.FromNumpy(tets.astype(np.int32))
    tet.CreatePointsAttr(pts)
    tet.CreateTetVertexIndicesAttr(idx)
    tet.CreateSurfaceFaceVertexIndicesAttr(UsdGeom.TetMesh.ComputeSurfaceFaces(tet))
    lo, hi = points.min(axis=0), points.max(axis=0)
    tet.CreateExtentAttr([Gf.Vec3f(*lo), Gf.Vec3f(*hi)])
    prim = tet.GetPrim()
    prim.AddAppliedSchema("OmniPhysicsVolumeDeformableSimAPI")
    prim.CreateAttribute("omniphysics:restShapePoints", Sdf.ValueTypeNames.Point3fArray).Set(pts)
    prim.CreateAttribute("omniphysics:restTetVtxIndices", Sdf.ValueTypeNames.Int4Array).Set(idx)
    _set_bind_pose(prim, points)
    UsdPhysics.CollisionAPI.Apply(prim)
    tet.CreatePurposeAttr(UsdGeom.Tokens.guide)  # simulation mesh: hidden in renders
    return tet


def _bind(geom_prim, visual, physics):
    api = UsdShade.MaterialBindingAPI(geom_prim)
    api.Bind(visual)
    api.Bind(physics, UsdShade.Tokens.weakerThanDescendants, "physics")


def export_stage(path, preset, prototypes, instances, ground_size, states=None, deformable=None):
    """prototypes: list of dicts {verts, faces, color, mineral, mass, metrics,
    moisture: {state: {mass, water_mass, cohesion}}, and for deformables
    tet_points, tets}
    instances: list of dicts {proto, position, orient (w, x, y, z), state}
    states: list of exported moisture states, or None (no variant set).
    deformable: the preset's deformable settings, or None for rigid bodies."""
    stage = Usd.Stage.CreateNew(str(path))
    UsdGeom.SetStageMetersPerUnit(stage, 1.0)
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
    UsdPhysics.SetStageKilogramsPerUnit(stage, 1.0)

    world = UsdGeom.Xform.Define(stage, "/World")
    stage.SetDefaultPrim(world.GetPrim())
    world.GetPrim().SetCustomDataByKey("granulaire:preset", preset["label"])
    UsdPhysics.Scene.Define(stage, "/World/PhysicsScene")
    UsdGeom.Scope.Define(stage, "/World/Looks")

    mu = preset.get("friction", 0.6)
    e = preset.get("restitution", 0.1)

    def phys_material(path, state):
        k_mu = STATE_PARAMS[state]["mu"] if state else 1.0
        k_e = STATE_PARAMS[state]["e"] if state else 1.0
        if deformable:
            return _make_deformable_material(
                stage,
                path,
                mu * k_mu,
                preset["density"],
                deformable["youngs_modulus"],
                deformable["poissons_ratio"],
            )
        return _make_phys_material(stage, path, mu * k_mu, e * k_e)

    if states:
        phys = {s: phys_material(f"/World/Looks/Phys_{s}", s) for s in states}
    else:
        phys = {None: phys_material("/World/Looks/Phys", None)}

    stage.CreateClassPrim("/World/Prototypes")
    for i, proto in enumerate(prototypes):
        root_path = f"/World/Prototypes/Grain_{i:03d}"
        prim = UsdGeom.Xform.Define(stage, root_path).GetPrim()
        if deformable:
            prim.AddAppliedSchema("OmniPhysicsDeformableBodyAPI")
            prim.CreateAttribute("omniphysics:deformableBodyEnabled", Sdf.ValueTypeNames.Bool).Set(True)
            mass_attr = prim.CreateAttribute("omniphysics:mass", Sdf.ValueTypeNames.Float)
            UsdShade.MaterialBindingAPI.Apply(prim)
        else:
            UsdPhysics.RigidBodyAPI.Apply(prim)
            mass_attr = UsdPhysics.MassAPI.Apply(prim).CreateMassAttr()

        m = proto["metrics"]
        for key, value in [
            ("diameterNominal", m["diameter_nominal_m"]),
            ("elongation", m["elongation_IL"]),
            ("flatness", m["flatness_SI"]),
            ("sphericity", m["sphericity"]),
            ("angularity", m["angularity_deg"]),
            ("convexity", m["convexity"]),
            ("dryMass", proto["mass"]),
        ]:
            prim.CreateAttribute(f"granulaire:{key}", Sdf.ValueTypeNames.Float).Set(float(value))
        prim.CreateAttribute("granulaire:mineral", Sdf.ValueTypeNames.String).Set(proto["mineral"])

        verts, faces = proto["verts"], proto["faces"]
        normals = trimesh.Trimesh(verts, faces, process=False).vertex_normals
        mesh = UsdGeom.Mesh.Define(stage, root_path + "/geom")
        mesh.CreatePointsAttr(Vt.Vec3fArray.FromNumpy(verts.astype(np.float32)))
        mesh.CreateFaceVertexCountsAttr(Vt.IntArray([3] * len(faces)))
        mesh.CreateFaceVertexIndicesAttr(Vt.IntArray.FromNumpy(faces.astype(np.int32).ravel()))
        mesh.CreateNormalsAttr(Vt.Vec3fArray.FromNumpy(normals.astype(np.float32)))
        mesh.SetNormalsInterpolation(UsdGeom.Tokens.vertex)
        mesh.CreateSubdivisionSchemeAttr(UsdGeom.Tokens.none)
        lo, hi = verts.min(axis=0), verts.max(axis=0)
        mesh.CreateExtentAttr([Gf.Vec3f(*lo), Gf.Vec3f(*hi)])
        UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim())
        if deformable:
            # render mesh skinned to the simulation mesh through the bind pose
            _set_bind_pose(mesh.GetPrim(), verts)
            _make_tet_mesh(stage, root_path + "/sim", proto["tet_points"], proto["tets"])
        else:
            UsdPhysics.CollisionAPI.Apply(mesh.GetPrim())
            UsdPhysics.MeshCollisionAPI.Apply(mesh.GetPrim()).CreateApproximationAttr(
                UsdPhysics.Tokens.convexHull
            )

        geom_prim = mesh.GetPrim()

        def bind(visual, physics, geom=geom_prim, root=prim):
            if deformable:
                # visual material on the render mesh, physics material on the body root
                UsdShade.MaterialBindingAPI(geom).Bind(visual)
                UsdShade.MaterialBindingAPI(root).Bind(
                    physics, UsdShade.Tokens.weakerThanDescendants, "physics"
                )
            else:
                _bind(geom, visual, physics)

        if not states:
            mass_attr.Set(float(proto["mass"]))
            mat = _make_material(stage, f"/World/Looks/Mat_{i:03d}", proto["color"], 0.85)
            mesh.CreateDisplayColorAttr([Gf.Vec3f(*proto["color"])])
            bind(mat, phys[None])
            continue

        # one material per state, created outside the variants (separate prims)
        mats = {}
        for s in states:
            p = STATE_PARAMS[s]
            mats[s] = _make_material(
                stage, f"/World/Looks/Mat_{i:03d}_{s}", wet_color(proto["color"], s), p["rough"], p["coat"]
            )
        # mass attribute declared above without a local value: one here would hide the variants

        vset = prim.GetVariantSets().AddVariantSet("moisture")
        for s in states:
            vset.AddVariant(s)
            vset.SetVariantSelection(s)
            info = proto["moisture"][s]
            with vset.GetVariantEditContext():
                mass_attr.Set(float(info["mass"]))
                prim.CreateAttribute("granulaire:moisture", Sdf.ValueTypeNames.Token).Set(s)
                prim.CreateAttribute("granulaire:waterMass", Sdf.ValueTypeNames.Float).Set(
                    float(info["water_mass"])
                )
                prim.CreateAttribute("granulaire:capillaryCohesion", Sdf.ValueTypeNames.Float).Set(
                    float(info["cohesion"])
                )
                mesh.CreateDisplayColorAttr([Gf.Vec3f(*wet_color(proto["color"], s))])
                bind(mats[s], phys[s])
        vset.SetVariantSelection(states[0])

    UsdGeom.Xform.Define(stage, "/World/Grains")
    for j, inst in enumerate(instances):
        p = f"/World/Grains/g_{j:04d}"
        xf = UsdGeom.Xform.Define(stage, p)
        prim = xf.GetPrim()
        prim.GetReferences().AddInternalReference(Sdf.Path(f"/World/Prototypes/Grain_{inst['proto']:03d}"))
        xf.AddTranslateOp().Set(Gf.Vec3d(*inst["position"]))
        w, x, y, z = inst["orient"]
        xf.AddOrientOp().Set(Gf.Quatf(float(w), float(x), float(y), float(z)))
        prim.CreateAttribute("granulaire:prototype", Sdf.ValueTypeNames.Int).Set(int(inst["proto"]))
        if states:
            prim.GetVariantSets().GetVariantSet("moisture").SetVariantSelection(inst["state"])

    h = ground_size / 2
    ground = UsdGeom.Mesh.Define(stage, "/World/Ground")
    ground.CreatePointsAttr([(-h, -h, 0), (h, -h, 0), (h, h, 0), (-h, h, 0)])
    ground.CreateFaceVertexCountsAttr([4])
    ground.CreateFaceVertexIndicesAttr([0, 1, 2, 3])
    ground.CreateExtentAttr([(-h, -h, 0), (h, h, 0)])
    ground.CreateDisplayColorAttr([Gf.Vec3f(0.5, 0.5, 0.5)])
    UsdPhysics.CollisionAPI.Apply(ground.GetPrim())
    ground_phys = _make_phys_material(stage, "/World/Looks/Phys_ground", 0.6, 0.1)
    UsdShade.MaterialBindingAPI.Apply(ground.GetPrim()).Bind(
        ground_phys, UsdShade.Tokens.weakerThanDescendants, "physics"
    )

    stage.GetRootLayer().Save()
    return stage
