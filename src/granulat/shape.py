"""Grain shape generation.

Each grain is an implicit volume, meshed with marching cubes:

1. Base body: draw points on an ellipsoid (axes L >= I >= S set by the Zingg
   ratios) and take their convex hull, a polyhedron whose number of facets
   sets the angularity. Its *gauge* g(x) = max_f (n_f . x) / d_f is 1 on the
   surface; replacing that max with a p-norm rounds edges and corners (low p =
   rounded grain, high p = sharp edges).
2. Fracture chips: random planes cut the body, g = max(g, (n_c . x) / d_c),
   leaving flat broken faces with sharp edges, as on crushed stone or broken
   pebbles.
3. Egg taper: the cross-section grows along the long axis (coordinate warp).
4. Non-convex irregularity as a height field on the direction u = x/|x|:
   low-frequency lumps, pits (vesicles of scoria, dents of flint) and a light
   surface roughness. The surface is g(x) = 1 + h(u).
5. Mesh the zero level set with marching cubes, recentre on the centre of mass
   and scale to the target nominal diameter (diameter of the equal-volume
   sphere).

Meshing the volume rather than displacing a sphere keeps triangles evenly
shaped everywhere: flat fracture faces and sharp creases need no special case.
"""

import numpy as np
import trimesh
from scipy.spatial import ConvexHull
from skimage.measure import marching_cubes

_ICO_CACHE = {}


def icosphere(subdivisions):
    if subdivisions not in _ICO_CACHE:
        ico = trimesh.creation.icosphere(subdivisions=subdivisions)
        _ICO_CACHE[subdivisions] = (np.asarray(ico.vertices), np.asarray(ico.faces))
    return _ICO_CACHE[subdivisions]


def _random_unit_vectors(rng, n):
    v = rng.normal(size=(n, 3))
    return v / np.linalg.norm(v, axis=1, keepdims=True)


class _Noise:
    """Smooth noise on the sphere: a sum of plane waves of varied frequencies."""

    def __init__(self, rng, n_waves=24, freq_range=(3.0, 9.0)):
        self.k = _random_unit_vectors(rng, n_waves)
        self.freq = rng.uniform(*freq_range, size=n_waves)
        self.phase = rng.uniform(0, 2 * np.pi, size=n_waves)
        probe = _random_unit_vectors(np.random.default_rng(0), 4000)
        self.norm = np.abs(self._raw(probe)).max() + 1e-12

    def _raw(self, u):
        return (np.sin(u @ self.k.T * self.freq + self.phase) / self.freq).sum(axis=1)

    def __call__(self, u):
        return self._raw(u) / self.norm


def _base_polyhedron(rng, params):
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
            return normals, offsets
    raise RuntimeError("could not build a valid polyhedron")


def _rounded_gauge(x, normals, offsets, p):
    """p-norm softened gauge of the polyhedron; homogeneous of degree 1."""
    s = np.clip(x @ normals.T / offsets, 0.0, None)
    smax = s.max(axis=1, keepdims=True)
    safe = np.where(smax > 0, smax, 1.0)
    return smax[:, 0] * ((s / safe) ** p).sum(axis=1) ** (1.0 / p)


def make_grain(rng, params):
    """Return (vertices, faces) for one grain drawn according to `params`.

    params: dict with elongation (I/L), flatness (S/I), facets, roundness_p,
    roughness, diameter_m (target nominal diameter, metres), and optionally:
    lumpiness, taper, chips, chip_depth, pits, pit_depth, pit_size
    (irregularity, all off by default), resolution (marching-cubes cells
    along the longest axis, default 48), sphere=True for an exact sphere
    (meshed as an icosphere of `subdivisions`).
    """
    target_volume = np.pi * params["diameter_m"] ** 3 / 6.0
    if params.get("sphere"):
        dirs, faces = icosphere(params.get("subdivisions", 4))
        mesh = trimesh.Trimesh(dirs, faces, process=False)
        return dirs * (target_volume / abs(mesh.volume)) ** (1.0 / 3.0), faces

    normals, offsets = _base_polyhedron(rng, params)
    p = params["roundness_p"]

    # support of the rounded body, sampled on directions, to place the cuts
    dirs, _ = icosphere(4)
    radius = 1.0 / _rounded_gauge(dirs, normals, offsets, p)

    cuts = []
    for _ in range(params.get("chips", 0)):
        n = _random_unit_vectors(rng, 1)[0]
        depth = rng.uniform(*params.get("chip_depth", (0.6, 0.85)))
        cuts.append((n, depth * np.max(radius * (dirs @ n))))

    taper = params.get("taper", 0.0)
    x_extent = np.max(np.abs(radius * dirs[:, 0]))

    lump = params.get("lumpiness", 0.0)
    lump_noise = _Noise(rng, n_waves=8, freq_range=(1.2, 3.2)) if lump > 0 else None
    pits = []
    for _ in range(params.get("pits", 0)):
        centre = _random_unit_vectors(rng, 1)[0]
        depth = rng.uniform(*params.get("pit_depth", (0.08, 0.2)))
        size = rng.uniform(*params.get("pit_size", (0.2, 0.4)))
        pits.append((centre, depth, size))
    rough = params.get("roughness", 0.0)
    rough_noise = _Noise(rng) if rough > 0 else None

    def field(x):
        """Negative inside, positive outside."""
        if taper:
            scale = 1.0 + taper * np.clip(x[:, 0] / x_extent, -1.0, 1.0)
            x = np.column_stack([x[:, 0], x[:, 1] / scale, x[:, 2] / scale])
        g = _rounded_gauge(x, normals, offsets, p)
        for n, d in cuts:
            g = np.maximum(g, (x @ n) / d)
        u = x / (np.linalg.norm(x, axis=1, keepdims=True) + 1e-30)
        h = np.zeros(len(x))
        if lump_noise is not None:
            h += lump * lump_noise(u)
        for centre, depth, size in pits:
            angle = np.arccos(np.clip(u @ centre, -1.0, 1.0))
            h -= depth * np.exp(-((angle / size) ** 2))
        if rough_noise is not None:
            h += rough * rough_noise(u)
        return g - np.clip(1.0 + h, 0.35, None)

    # grid: uniform spacing, fine enough for the thinnest axis
    extent = np.max(np.abs(radius[:, None] * dirs), axis=0)
    extent *= 1.0 + abs(taper) + lump + 0.05
    res = params.get("resolution", 48)
    step = min(2 * extent.max() / res, 2 * extent.min() / 14)
    n_cells = np.ceil(2 * extent / step).astype(int) + 3
    origin = -(n_cells - 1) * step / 2
    axes = [origin[k] + step * np.arange(n_cells[k]) for k in range(3)]
    grid = np.stack(np.meshgrid(*axes, indexing="ij"), axis=-1).reshape(-1, 3)
    volume = field(grid).reshape(n_cells)

    verts, faces, _, _ = marching_cubes(volume, level=0.0, spacing=(step, step, step))
    verts += origin
    mesh = trimesh.Trimesh(verts, faces, process=True)
    if mesh.volume < 0:
        mesh.invert()
    # keep the main piece if a deep pit ever detached a sliver
    parts = mesh.split(only_watertight=False)
    if len(parts) > 1:
        mesh = max(parts, key=lambda m: abs(m.volume))
    verts = np.asarray(mesh.vertices) - mesh.center_mass
    verts *= (target_volume / abs(mesh.volume)) ** (1.0 / 3.0)
    return verts, np.asarray(mesh.faces)
