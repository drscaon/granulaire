"""OpenUSD export: a library of prototypes plus grains that reference them.

Scene layout (units: metres, kilograms, Z up):

/World
  /PhysicsScene
  /Looks/Mat_000[_<state>]     UsdPreviewSurface materials (prototype x state)
  /Looks/Phys[_<state>]        physics materials (friction, restitution)
  /Prototypes        (class)   N shapes, not rendered directly
    /Grain_000                 RigidBody + Mass + granulat:* attributes
      variantSet "moisture"    (when enabled) dry | damp | wet | saturated:
                               mass, granulat:waterMass,
                               granulat:capillaryCohesion, bound materials
      /geom                    Mesh + Collision (convex hull)
  /Grains
    /g_0000 ...                internal reference to a prototype, with its own
                               position, orientation and moisture state
  /Ground                      static collision plane

Composition rule relied on: a local opinion is stronger than a variant. When
moisture is enabled, mass and material bindings are therefore authored ONLY
inside the variants, never directly on the prototype; each grain picks its
variant through a local selection.
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


def _bind(geom_prim, visual, physics):
    api = UsdShade.MaterialBindingAPI(geom_prim)
    api.Bind(visual)
    api.Bind(physics, UsdShade.Tokens.weakerThanDescendants, "physics")


def export_stage(path, preset, prototypes, instances, ground_size, states=None):
    """prototypes: list of dicts {verts, faces, color, mineral, mass, metrics,
    moisture: {state: {mass, water_mass, cohesion}}}
    instances: list of dicts {proto, position, orient (w, x, y, z), state}
    states: list of exported moisture states, or None (no variant set)."""
    stage = Usd.Stage.CreateNew(str(path))
    UsdGeom.SetStageMetersPerUnit(stage, 1.0)
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
    UsdPhysics.SetStageKilogramsPerUnit(stage, 1.0)

    world = UsdGeom.Xform.Define(stage, "/World")
    stage.SetDefaultPrim(world.GetPrim())
    world.GetPrim().SetCustomDataByKey("granulat:preset", preset["label"])
    UsdPhysics.Scene.Define(stage, "/World/PhysicsScene")
    UsdGeom.Scope.Define(stage, "/World/Looks")

    mu = preset.get("friction", 0.6)
    e = preset.get("restitution", 0.1)
    if states:
        phys = {
            s: _make_phys_material(
                stage, f"/World/Looks/Phys_{s}", mu * STATE_PARAMS[s]["mu"], e * STATE_PARAMS[s]["e"]
            )
            for s in states
        }
    else:
        phys = {None: _make_phys_material(stage, "/World/Looks/Phys", mu, e)}

    stage.CreateClassPrim("/World/Prototypes")
    for i, proto in enumerate(prototypes):
        root_path = f"/World/Prototypes/Grain_{i:03d}"
        prim = UsdGeom.Xform.Define(stage, root_path).GetPrim()
        UsdPhysics.RigidBodyAPI.Apply(prim)
        mass_api = UsdPhysics.MassAPI.Apply(prim)

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
            prim.CreateAttribute(f"granulat:{key}", Sdf.ValueTypeNames.Float).Set(float(value))
        prim.CreateAttribute("granulat:mineral", Sdf.ValueTypeNames.String).Set(proto["mineral"])

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
        UsdPhysics.CollisionAPI.Apply(mesh.GetPrim())
        UsdPhysics.MeshCollisionAPI.Apply(mesh.GetPrim()).CreateApproximationAttr(
            UsdPhysics.Tokens.convexHull
        )
        UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim())

        if not states:
            mass_api.CreateMassAttr(float(proto["mass"]))
            mat = _make_material(stage, f"/World/Looks/Mat_{i:03d}", proto["color"], 0.85)
            mesh.CreateDisplayColorAttr([Gf.Vec3f(*proto["color"])])
            _bind(mesh.GetPrim(), mat, phys[None])
            continue

        # one material per state, created outside the variants (separate prims)
        mats = {}
        for s in states:
            p = STATE_PARAMS[s]
            mats[s] = _make_material(
                stage, f"/World/Looks/Mat_{i:03d}_{s}", wet_color(proto["color"], s), p["rough"], p["coat"]
            )
        # attribute declared without a local value: a value here would hide the variants
        mass_api.CreateMassAttr()

        vset = prim.GetVariantSets().AddVariantSet("moisture")
        for s in states:
            vset.AddVariant(s)
            vset.SetVariantSelection(s)
            info = proto["moisture"][s]
            with vset.GetVariantEditContext():
                prim.GetAttribute("physics:mass").Set(float(info["mass"]))
                prim.CreateAttribute("granulat:moisture", Sdf.ValueTypeNames.Token).Set(s)
                prim.CreateAttribute("granulat:waterMass", Sdf.ValueTypeNames.Float).Set(
                    float(info["water_mass"])
                )
                prim.CreateAttribute("granulat:capillaryCohesion", Sdf.ValueTypeNames.Float).Set(
                    float(info["cohesion"])
                )
                mesh.CreateDisplayColorAttr([Gf.Vec3f(*wet_color(proto["color"], s))])
                _bind(mesh.GetPrim(), mats[s], phys[s])
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
        prim.CreateAttribute("granulat:prototype", Sdf.ValueTypeNames.Int).Set(int(inst["proto"]))
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
