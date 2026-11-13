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
      /geom                    render Mesh
      /collision               convex hull of the grain, at most 64 points
                               (purpose guide), CollisionAPI, convexHull
  /Grains
    /g_0000 ...                internal reference to a prototype, with its own
                               position, orientation and moisture state
  /Ground                      the shared ground: a 2 cm box, its top at z = 0 (ground.py)
  /GroundMaterial              its physics material

Composition rule relied on: a local opinion is stronger than a variant. When
moisture is enabled, mass and material bindings are therefore authored ONLY
inside the variants, never directly on the prototype; each grain picks its
variant through a local selection.

Deformable grains (packing peanuts, cherry tomatoes) are rigid bodies here like the others:
core OpenUSD has no deformable-body schema yet, so what makes them deformable follows NVIDIA's
OmniPhysics schema and is kept out of this file, in a layer over it (omniphysics.py).
"""

from pathlib import Path

import numpy as np
import trimesh
from pxr import Gf, Sdf, Usd, UsdGeom, UsdPhysics, UsdSemantics, UsdShade, Vt
from scipy.spatial import ConvexHull

from .contract import set_group, write_identity, write_labels, write_measured, write_variation
from .ground import ground, physics_scene
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


HULL_POINTS = 64  # PhysX's default hull vertex limit (physxConvexHullCollision:hullVertexLimit)
# first points of a reduced hull: the extremes along the axes and the diagonals
_SEED_DIRS = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 1, 1], [1, 1, -1], [1, -1, 1], [-1, 1, 1]], float)


def collision_hull(verts: np.ndarray, max_points: int = HULL_POINTS) -> tuple[np.ndarray, np.ndarray]:
    """The grain's convex hull with at most ``max_points`` vertices, so that every engine collides
    with the same shape (PhysX would otherwise rebuild a hull of 64 vertices on its own, MuJoCo and
    Blender keep them all). Greedy: from the extreme points along the axes and the diagonals, add
    the hull vertex farthest outside the current hull until the budget is spent. The result lies
    inside the true hull; it is then scaled about its centroid to the true hull's volume, so the
    grains pack as densely and engines that take inertia from the collider get it right. Returns
    (points, triangles)."""
    pts = np.asarray(verts, float)
    cand = pts[ConvexHull(pts).vertices]
    if len(cand) <= max_points:
        chosen = list(range(len(cand)))
    else:
        c = cand - cand.mean(axis=0)
        chosen = sorted({int(i) for d in _SEED_DIRS for i in ((c @ d).argmax(), (c @ d).argmin())})
        while len(chosen) < max_points:
            eq = ConvexHull(cand[chosen]).equations
            dist = (cand @ eq[:, :3].T + eq[:, 3]).max(axis=1)  # how far outside the current hull
            dist[chosen] = -np.inf
            k = int(dist.argmax())
            if dist[k] <= 0:
                break
            chosen.append(k)
    sub = cand[chosen]
    hull = ConvexHull(sub)
    used = np.unique(hull.simplices)
    remap = np.full(len(sub), -1)
    remap[used] = np.arange(len(used))
    points, tris = sub[used], remap[hull.simplices]
    if len(cand) > max_points:  # back to the true volume
        centre = points.mean(axis=0)
        points = centre + (points - centre) * (ConvexHull(cand).volume / hull.volume) ** (1 / 3)
    # outward winding: counter-clockwise seen from outside (right-handed)
    p = points[tris]
    normal = np.cross(p[:, 1] - p[:, 0], p[:, 2] - p[:, 0])
    flip = (normal * (p.mean(axis=1) - points.mean(axis=0))).sum(axis=1) < 0
    tris[flip] = tris[flip][:, ::-1]
    return points, tris


# drawn per prototype (generator.sample_params and sample_color), in the order they are written
DRAWN = (
    "phi",
    "diameter_m",
    "elongation",
    "flatness",
    "aspect",
    "lumpiness",
    "taper",
    "chips",
    "pits",
    "facets",
    "roundness_p",
)


def drawn_values(proto) -> dict:
    """What was drawn for a prototype: its shape parameters, its mineral and its colour."""
    params = proto.get("params", {})
    values = {name: params[name] for name in DRAWN if name in params}
    if "aspect" in values:  # the grain's width over thickness, not a variation aspect
        values["aspect_ratio"] = values.pop("aspect")
    values["mineral"] = proto.get("mineral")
    values["color_rgb"] = proto.get("color")
    return values


# measured on each generated prototype (measure.py): the names they are written under
MEASURED = {
    "diameter_nominal_m": "diameter_nominal_m",
    "volume_m3": "volume_m3",
    "area_m2": "area_m2",
    "L_m": "long_axis_m",
    "I_m": "intermediate_axis_m",
    "S_m": "short_axis_m",
    "elongation_IL": "elongation",
    "flatness_SI": "flatness",
    "sphericity": "sphericity",
    "convexity": "convexity",
    "angularity_deg": "angularity_deg",
}


def measured_values(proto, states=None) -> dict:
    """What was measured on a prototype once generated: its mass (dry, and in each moisture
    state) and its shape descriptors."""
    values = {"mass_kg": float(proto["mass"])}
    metrics = proto.get("metrics", {})
    values.update({name: float(metrics[key]) for key, name in MEASURED.items() if key in metrics})
    for state in states or ():
        values[f"mass_{state}_kg"] = float(proto["moisture"][state]["mass"])
    return values


def export_stage(
    path,
    preset,
    prototypes,
    instances,
    ground_size,
    states=None,
    preset_key=None,
    seed=0,
    aspects=(),
):
    """prototypes: list of dicts {verts, faces, color, mineral, mass, metrics,
    moisture: {state: {mass, water_mass, cohesion}}}
    instances: list of dicts {proto, position, orient (w, x, y, z), state}
    states: list of exported moisture states, or None (no variant set).
    preset_key, seed: the preset's key and the scene's seed, written as each grain's identity
    (Primvaria contract: kind component, assetInfo, primvaria:* attributes).
    aspects: the variations that were switched on; with each prototype's drawn values they are
    its ground truth (primvaria:variation:*). A grain adds its own drawn moisture state."""
    stage = Usd.Stage.CreateNew(str(path))
    UsdGeom.SetStageMetersPerUnit(stage, 1.0)
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
    UsdPhysics.SetStageKilogramsPerUnit(stage, 1.0)

    world = UsdGeom.Xform.Define(stage, "/World")
    stage.SetDefaultPrim(world.GetPrim())
    set_group(world.GetPrim(), assembly=True)
    physics_scene(stage)
    UsdGeom.Scope.Define(stage, "/World/Looks")

    mu = preset.get("friction", 0.6)
    surface_rough = preset.get("surface_roughness", STATE_PARAMS["dry"]["rough"])
    e = preset.get("restitution", 0.1)

    def phys_material(path, state):
        k_mu = STATE_PARAMS[state]["mu"] if state else 1.0
        k_e = STATE_PARAMS[state]["e"] if state else 1.0
        return _make_phys_material(stage, path, mu * k_mu, e * k_e)

    if states:
        phys = {s: phys_material(f"/World/Looks/Phys_{s}", s) for s in states}
    else:
        phys = {None: phys_material("/World/Looks/Phys", None)}

    set_group(stage.CreateClassPrim("/World/Prototypes"))
    for i, proto in enumerate(prototypes):
        root_path = f"/World/Prototypes/Grain_{i:03d}"
        prim = UsdGeom.Xform.Define(stage, root_path).GetPrim()
        write_identity(
            prim,
            name=f"Grain_{i:03d}",
            preset=preset_key or preset["label"],
            seed=seed,
            identifier=f"./{Path(path).name}",
        )
        write_labels(prim, ("grain", preset_key or preset["label"]))  # the grains name themselves below
        write_variation(prim, aspects, drawn_values(proto))
        write_measured(prim, measured_values(proto, states))
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
        # the collider: a reduced convex hull, not the render mesh (see collision_hull)
        hp, ht = collision_hull(verts)
        col = UsdGeom.Mesh.Define(stage, root_path + "/collision")
        col.CreatePointsAttr(Vt.Vec3fArray.FromNumpy(hp.astype(np.float32)))
        col.CreateFaceVertexCountsAttr(Vt.IntArray([3] * len(ht)))
        col.CreateFaceVertexIndicesAttr(Vt.IntArray.FromNumpy(ht.astype(np.int32).ravel()))
        col.CreateSubdivisionSchemeAttr(UsdGeom.Tokens.none)
        col.CreateExtentAttr([Gf.Vec3f(*hp.min(axis=0)), Gf.Vec3f(*hp.max(axis=0))])
        col.CreatePurposeAttr(UsdGeom.Tokens.guide)
        UsdPhysics.CollisionAPI.Apply(col.GetPrim())
        UsdPhysics.MeshCollisionAPI.Apply(col.GetPrim()).CreateApproximationAttr(UsdPhysics.Tokens.convexHull)
        UsdShade.MaterialBindingAPI.Apply(col.GetPrim())

        geom_prim = mesh.GetPrim()
        col_prim = stage.GetPrimAtPath(root_path + "/collision")

        def bind(visual, physics, geom=geom_prim, col=col_prim):
            UsdShade.MaterialBindingAPI(geom).Bind(visual)
            UsdShade.MaterialBindingAPI(col).Bind(physics, UsdShade.Tokens.weakerThanDescendants, "physics")

        if not states:
            mass_attr.Set(float(proto["mass"]))
            mat = _make_material(stage, f"/World/Looks/Mat_{i:03d}", proto["color"], surface_rough)
            mesh.CreateDisplayColorAttr([Gf.Vec3f(*proto["color"])])
            bind(mat, phys[None])
            continue

        # one material per state, created outside the variants (separate prims)
        mats = {}
        for s in states:
            p = STATE_PARAMS[s]
            mats[s] = _make_material(
                stage,
                f"/World/Looks/Mat_{i:03d}_{s}",
                wet_color(proto["color"], s),
                min(p["rough"], surface_rough),
                p["coat"],
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

    set_group(UsdGeom.Xform.Define(stage, "/World/Grains").GetPrim())
    for j, inst in enumerate(instances):
        p = f"/World/Grains/g_{j:04d}"
        xf = UsdGeom.Xform.Define(stage, p)
        prim = xf.GetPrim()
        prim.GetReferences().AddInternalReference(Sdf.Path(f"/World/Prototypes/Grain_{inst['proto']:03d}"))
        xf.AddTranslateOp().Set(Gf.Vec3d(*inst["position"]))
        w, x, y, z = inst["orient"]
        xf.AddOrientOp().Set(Gf.Quatf(float(w), float(x), float(y), float(z)))
        prim.CreateAttribute("granulaire:prototype", Sdf.ValueTypeNames.Int).Set(int(inst["proto"]))
        UsdSemantics.LabelsAPI.Apply(prim, "instance").CreateLabelsAttr([prim.GetName()])
        if states:
            write_variation(prim, aspects, {"moisture": inst["state"]})
            prim.GetVariantSets().GetVariantSet("moisture").SetVariantSelection(inst["state"])

    h = ground_size / 2  # the pile's footprint; the shared ground adds its margin
    ground(stage, (-h, -h), (h, h))

    stage.GetRootLayer().Save()
    return stage
