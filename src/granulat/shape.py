"""Grain shape generation.

Each grain is an implicit volume, meshed with marching cubes:

1. Base body, by `kind`:
   - "rock" (default): draw points on an ellipsoid (axes L >= I >= S set by the Zingg
   ratios) and take their convex hull, a polyhedron whose number of facets
   sets the angularity. Its *gauge* g(x) = max_f (n_f . x) / d_f is 1 on the
   surface; replacing that max with a p-norm rounds edges and corners (low p =
   rounded grain, high p = sharp edges).
   - "superellipsoid": smooth kernels and seeds (wheat, rice, soybean,
     maize); the exponent goes from 2 (ellipsoid) towards boxy shapes.
   - "cylinder": pellets; half-length 1, radius `aspect`, the exponent sets
     how rounded the end edges are.
   - "tube": a rounded tube swept along an S, C or straight curve (packing
     peanuts); radius `aspect`, cross-section flattened by `flatness`.
2. Fracture chips: random planes cut the body, g = max(g, (n_c . x) / d_c),
   leaving flat broken faces with sharp edges, as on crushed stone or broken
   pebbles. With chip_axis="x" the planes are nearly perpendicular to the long
   axis: the broken ends of wood pellets.
3. Egg taper: the cross-section grows along the long axis; bend: the grain
   curves in the length-width plane, giving a kidney shape (beans). Both are
   coordinate warps.
4. Non-convex irregularity as a height field on the direction u = x/|x|:
   low-frequency lumps, pits (vesicles of scoria, dents of flint), a crease
   along the long axis (wheat), a dent at the broad end (maize) and a light
   surface roughness. The surface is g(x) = 1 + h(u).
5. Mesh the zero level set with marching cubes, recentre on the centre of mass
   and scale to the target nominal diameter (diameter of the equal-volume
   sphere).

Meshing the volume rather than displacing a sphere keeps triangles evenly
shaped everywhere: flat fracture faces and sharp creases need no special case.
The same volume can also be filled with tetrahedra (tets=True), the
simulation mesh of a deformable body.
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


def _superellipsoid_gauge(x, axes, e):
    return ((np.abs(x / axes) ** e).sum(axis=1)) ** (1.0 / e)


def _cylinder_gauge(x, radius, ellipticity, e):
    radial = np.sqrt((x[:, 1] / radius) ** 2 + (x[:, 2] / (radius * ellipticity)) ** 2)
    return (np.abs(x[:, 0]) ** e + radial**e) ** (1.0 / e)


def _tube(rng, params):
    """Distance field of a tube swept along a curve, and its bounding extent."""
    curves = params.get("curves") or {"S": 1.0}
    names = list(curves)
    weights = np.array([curves[n] for n in names], dtype=float)
    shape = names[int(rng.choice(len(names), p=weights / weights.sum()))]
    lo, hi = params.get("curve_amplitude", (0.0, 0.0))
    amp = rng.uniform(lo, hi) if params.get("vary", True) else (lo + hi) / 2
    t = np.linspace(-1.0, 1.0, 49)
    if shape == "S":
        y = amp * np.sin(np.pi * t)
    elif shape == "C":
        y = amp * (1.0 - t**2)
        y -= y.mean()
    else:
        y = np.zeros_like(t)
    curve = np.column_stack([t, y, np.zeros_like(t)])
    a, b = curve[:-1], curve[1:]
    ab = b - a
    ab2 = (ab**2).sum(axis=1)
    r = params.get("aspect", 0.3)
    squash = np.array([1.0, 1.0, 1.0 / params["flatness"]])

    def gauge(x):
        out = np.empty(len(x))
        for i in range(0, len(x), 20000):
            p = x[i : i + 20000]
            s = np.clip(((p[:, None, :] - a[None]) * ab[None]).sum(axis=2) / ab2[None], 0.0, 1.0)
            d = (p[:, None, :] - (a[None] + s[..., None] * ab[None])) * squash
            out[i : i + 20000] = np.sqrt((d**2).sum(axis=2)).min(axis=1)
        return out / r

    extent = np.array([1.0 + r, np.abs(y).max() + r, r * params["flatness"]])
    return gauge, extent


def _body(rng, params):
    """Return the base body's gauge function (homogeneous of degree 1)."""
    kind = params.get("kind", "rock")
    if kind == "rock":
        normals, offsets = _base_polyhedron(rng, params)
        p = params["roundness_p"]
        return lambda x: _rounded_gauge(x, normals, offsets, p)
    e = params.get("exponent", 2.0)
    if kind == "superellipsoid":
        axes = np.array([1.0, params["elongation"], params["elongation"] * params["flatness"]])
        return lambda x: _superellipsoid_gauge(x, axes, e)
    if kind == "cylinder":
        aspect, ellipticity = params.get("aspect", 1.0), params["flatness"]
        return lambda x: _cylinder_gauge(x, aspect, ellipticity, e)
    raise ValueError(f"unknown grain kind '{kind}'")


def make_grain(rng, params):
    """Return (vertices, faces) for one grain drawn according to `params`.

    params: dict with elongation (I/L), flatness (S/I), facets, roundness_p,
    roughness, diameter_m (target nominal diameter, metres), and optionally:
    kind ("rock", "superellipsoid", "cylinder") with exponent and aspect,
    lumpiness, taper, chips, chip_depth, chip_axis, pits, pit_depth, pit_size,
    crease (depth, width), dent (depth range, size) with dent_dir (default
    the -x end), bend (range of curvature) (irregularity, all off by
    default), resolution (marching-cubes cells
    along the longest axis, default 48), sphere=True for an exact sphere
    (meshed as an icosphere of `subdivisions`).
    """
    target_volume = np.pi * params["diameter_m"] ** 3 / 6.0
    if params.get("sphere"):
        dirs, faces = icosphere(params.get("subdivisions", 4))
        mesh = trimesh.Trimesh(dirs, faces, process=False)
        return dirs * (target_volume / abs(mesh.volume)) ** (1.0 / 3.0), faces

    tube_extent = None
    if params.get("kind") == "tube":
        gauge, tube_extent = _tube(rng, params)
        for key in ("chips", "taper", "bend"):
            if params.get(key):
                raise ValueError(f"'{key}' is not supported for tube grains")
        dirs = radius = np.zeros((1, 3))
    else:
        gauge = _body(rng, params)
        # support of the body, sampled on directions, to place the cuts
        dirs, _ = icosphere(4)
        radius = 1.0 / gauge(dirs)

    cuts = []
    for _ in range(params.get("chips", 0)):
        if params.get("chip_axis") == "x":
            # nearly perpendicular to the long axis, at either end
            n = np.array([rng.choice([-1.0, 1.0]), *rng.normal(0.0, 0.3, 2)])
            n /= np.linalg.norm(n)
        else:
            n = _random_unit_vectors(rng, 1)[0]
        depth = rng.uniform(*params.get("chip_depth", (0.6, 0.85)))
        cuts.append((n, depth * np.max(radius * (dirs @ n))))

    taper = params.get("taper", 0.0)
    x_extent = np.max(np.abs(radius * dirs[:, 0])) or 1.0
    y_extent = np.max(np.abs(radius * dirs[:, 1])) or 1.0
    bend = rng.uniform(*params["bend"]) if params.get("bend") else 0.0

    lump = params.get("lumpiness", 0.0)
    lump_noise = _Noise(rng, n_waves=8, freq_range=(1.2, 3.2)) if lump > 0 else None
    pits = []
    for _ in range(params.get("pits", 0)):
        centre = _random_unit_vectors(rng, 1)[0]
        depth = rng.uniform(*params.get("pit_depth", (0.08, 0.2)))
        size = rng.uniform(*params.get("pit_size", (0.2, 0.4)))
        pits.append((centre, depth, size))
    crease = params.get("crease")  # (depth, angular width), on the -z side
    dent = None
    if params.get("dent"):
        lo, hi, size = params["dent"]
        direction = np.asarray(params.get("dent_dir") or (-1.0, 0.0, 0.0), dtype=float)
        dent = (rng.uniform(lo, hi), size, direction / np.linalg.norm(direction))
    rough = params.get("roughness", 0.0)
    rough_noise = _Noise(rng) if rough > 0 else None

    def field(x):
        """Negative inside, positive outside."""
        if taper:
            scale = 1.0 + taper * np.clip(x[:, 0] / x_extent, -1.0, 1.0)
            x = np.column_stack([x[:, 0], x[:, 1] / scale, x[:, 2] / scale])
        if bend:
            # ends shifted towards +y: the inner (concave) side faces +y
            shift = bend * y_extent * np.clip(x[:, 0] / x_extent, -1.0, 1.0) ** 2
            x = np.column_stack([x[:, 0], x[:, 1] - shift, x[:, 2]])
        g = gauge(x)
        for n, d in cuts:
            g = np.maximum(g, (x @ n) / d)
        u = x / (np.linalg.norm(x, axis=1, keepdims=True) + 1e-30)
        h = np.zeros(len(x))
        if lump_noise is not None:
            h += lump * lump_noise(u)
        for centre, depth, size in pits:
            angle = np.arccos(np.clip(u @ centre, -1.0, 1.0))
            h -= depth * np.exp(-((angle / size) ** 2))
        if crease is not None:
            depth, width = crease
            ventral = 1.0 / (1.0 + np.exp(12.0 * u[:, 2]))
            h -= depth * np.exp(-((u[:, 1] / width) ** 2)) * ventral
        if dent is not None:
            depth, size, direction = dent
            angle = np.arccos(np.clip(u @ direction, -1.0, 1.0))
            h -= depth * np.exp(-((angle / size) ** 2))
        if rough_noise is not None:
            h += rough * rough_noise(u)
        return g - np.clip(1.0 + h, 0.35, None)

    # grid: uniform spacing, fine enough for the thinnest axis
    if tube_extent is not None:
        extent = tube_extent * (1.0 + lump + rough + 0.05)
    else:
        extent = np.max(np.abs(radius[:, None] * dirs), axis=0)
        extent *= 1.0 + abs(taper) + lump + 0.05
        extent[1] += bend * y_extent
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
    centre = mesh.center_mass
    scale = (target_volume / abs(mesh.volume)) ** (1.0 / 3.0)
    verts = (np.asarray(mesh.vertices) - centre) * scale
    if not params.get("tets"):
        return verts, np.asarray(mesh.faces)
    tet_points, tets = _voxel_tets(field, extent, params.get("tet_resolution", 14))
    return verts, np.asarray(mesh.faces), (tet_points - centre) * scale, tets


# the 6 tetrahedra of a cube sharing its main diagonal (Kuhn / Freudenthal):
# neighbouring cubes split their shared faces the same way, so the mesh conforms
_CUBE = np.array([[i, j, k] for i in (0, 1) for j in (0, 1) for k in (0, 1)])
_KUHN = []
for _perm in ((0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)):
    _corner = np.zeros(3, dtype=int)
    _path = [_corner.copy()]
    for _axis in _perm:
        _corner[_axis] = 1
        _path.append(_corner.copy())
    _KUHN.append([int(np.flatnonzero((_CUBE == c).all(axis=1))[0]) for c in _path])
_KUHN = np.array(_KUHN)


def _voxel_tets(field, extent, resolution):
    """Tetrahedral mesh of the volume: inside voxels split into 6 tets each."""
    step = 2 * extent.max() / resolution
    n = np.ceil(2 * extent / step).astype(int) + 2
    origin = -n * step / 2
    centres = np.stack(
        np.meshgrid(*[origin[k] + step * (np.arange(n[k]) + 0.5) for k in range(3)], indexing="ij"),
        axis=-1,
    ).reshape(-1, 3)
    inside = np.flatnonzero(field(centres) < 0.0)
    if len(inside) == 0:
        raise RuntimeError("no voxel inside the grain; raise tet_resolution")
    ijk = np.stack(np.unravel_index(inside, n), axis=1)
    corners = ijk[:, None, :] + _CUBE[None]  # (cells, 8, 3) node indices
    node_ids = np.ravel_multi_index(corners.reshape(-1, 3).T, n + 1).reshape(-1, 8)
    tets = node_ids[:, _KUHN].reshape(-1, 4)
    used, tets = np.unique(tets, return_inverse=True)
    tets = tets.reshape(-1, 4)
    points = origin + step * np.stack(np.unravel_index(used, n + 1), axis=1)
    # positive orientation
    p = points[tets]
    vol = np.einsum("ij,ij->i", np.cross(p[:, 1] - p[:, 0], p[:, 2] - p[:, 0]), p[:, 3] - p[:, 0])
    flip = vol < 0
    tets[flip] = tets[flip][:, [0, 2, 1, 3]]
    return points, tets.astype(np.int32)
