"""Grain shape generation.

Method:
1. Draw points on an ellipsoid (axes L >= I >= S set by the Zingg ratios) and
   take their convex hull: a polyhedron whose number of facets sets the
   angularity.
2. Evaluate the *gauge* of that polyhedron in every direction u of an
   icosphere: 1/r(u) = max_f (n_f . u) / d_f. Replacing that max with a
   p-norm rounds edges and corners: low p = rounded grain, high p = sharp
   edges. A p-norm of convex functions stays convex, so the grain stays
   convex up to the roughness noise (its convex hull is a good collision
   shape).
3. A light surface noise adds roughness.
4. Recentre on the centre of mass and scale to the target nominal diameter
   (diameter of the sphere of equal volume).

Sampling directions come from an icosphere; the final triangulation is that
of the convex hull (clean along sharp edges).
"""

import numpy as np
import trimesh
from scipy.spatial import ConvexHull

_ICO_CACHE = {}


def icosphere(subdivisions):
    if subdivisions not in _ICO_CACHE:
        ico = trimesh.creation.icosphere(subdivisions=subdivisions)
        _ICO_CACHE[subdivisions] = (np.asarray(ico.vertices), np.asarray(ico.faces))
    return _ICO_CACHE[subdivisions]


def _random_unit_vectors(rng, n):
    v = rng.normal(size=(n, 3))
    return v / np.linalg.norm(v, axis=1, keepdims=True)


def _surface_noise(rng, dirs, n_waves=24):
    """Smooth noise on the sphere: a sum of plane waves of varied frequencies."""
    k = _random_unit_vectors(rng, n_waves)
    freq = rng.uniform(3.0, 9.0, size=n_waves)
    phase = rng.uniform(0, 2 * np.pi, size=n_waves)
    amp = 1.0 / freq  # less energy at high frequencies
    n = (np.sin(dirs @ k.T * freq + phase) * amp).sum(axis=1)
    return n / (np.abs(n).max() + 1e-12)


def make_grain(rng, params):
    """Return (vertices, faces) for one grain drawn according to `params`.

    params: dict with elongation (I/L), flatness (S/I), facets, roundness_p,
    roughness, diameter_m (target nominal diameter, metres), subdivisions,
    and optionally sphere=True for an exact sphere.
    """
    dirs, faces = icosphere(params["subdivisions"])
    if params.get("sphere"):
        # reference: exact sphere (up to meshing), no shape draw
        mesh = trimesh.Trimesh(dirs, faces, process=False)
        target_volume = np.pi * params["diameter_m"] ** 3 / 6.0
        verts = dirs * (target_volume / abs(mesh.volume)) ** (1.0 / 3.0)
        return verts, faces
    axes = np.array([1.0, params["elongation"], params["elongation"] * params["flatness"]])

    for _ in range(20):
        pts = _random_unit_vectors(rng, params["facets"]) * axes
        pts *= rng.uniform(0.85, 1.0, size=(len(pts), 1))  # irregular facets
        pts -= pts.mean(axis=0)
        try:
            hull = ConvexHull(pts)
        except Exception:
            continue
        normals = hull.equations[:, :3]
        offsets = -hull.equations[:, 3]  # distance from the origin to each plane
        if np.all(offsets > 1e-3 * axes.min()):
            break
    else:
        raise RuntimeError("could not build a valid polyhedron")

    # softened gauge: p-norm of the positive contributions
    s = np.clip(dirs @ normals.T / offsets, 0.0, None)
    p = params["roundness_p"]
    smax = s.max(axis=1, keepdims=True)
    gauge = smax[:, 0] * ((s / smax) ** p).sum(axis=1) ** (1.0 / p)
    r = 1.0 / gauge

    # Triangulation: use the convex hull of the smooth points rather than the
    # icosphere connectivity, which leaves saw-teeth along the sharp edges of
    # flat grains. All points lie on a convex surface, so all are hull vertices.
    smooth = dirs * r[:, None]
    hull = trimesh.convex.convex_hull(smooth)
    verts = np.asarray(hull.vertices)
    faces = np.asarray(hull.faces)

    # roughness: small radial displacement, applied after triangulation
    u = verts / np.linalg.norm(verts, axis=1, keepdims=True)
    verts = verts * (1.0 + params["roughness"] * _surface_noise(rng, u))[:, None]

    mesh = trimesh.Trimesh(verts, faces, process=False)
    verts = verts - mesh.center_mass
    target_volume = np.pi * params["diameter_m"] ** 3 / 6.0
    verts *= (target_volume / abs(mesh.volume)) ** (1.0 / 3.0)
    return verts, faces
