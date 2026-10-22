"""Shape descriptors measured on the mesh actually generated.

We do not trust the input parameters: we measure what comes out.
Measurements are taken on a copy scaled to unit size, then converted back:
trimesh uses absolute tolerances (~1e-8) that break on micron-sized grains.
"""

import numpy as np
import trimesh


def measure(verts, faces):
    scale = float(np.ptp(verts, axis=0).max())
    mesh = trimesh.Trimesh(verts / scale, faces, process=False)
    volume = abs(mesh.volume)
    area = mesh.area

    # dimensions L >= I >= S: bounding box along the principal axes of the
    # surface (a caliper-like measure; much faster than a minimum-volume box)
    pts = mesh.vertices - mesh.vertices.mean(axis=0)
    axes = np.linalg.svd(pts, full_matrices=False)[2]
    extents = np.sort(np.ptp(pts @ axes.T, axis=0))[::-1]
    L, I, S = extents  # noqa: E741 - standard sedimentology notation

    # Wadell sphericity: area of the equal-volume sphere / actual area
    sphericity = (np.pi ** (1 / 3)) * (6 * volume) ** (2 / 3) / area

    # convexity: volume / convex hull volume
    convexity = volume / mesh.convex_hull.volume

    # angularity (proxy): 95th percentile of dihedral angles between adjacent
    # faces, in degrees. Only comparable between grains of the same mesh
    # resolution; not a reliable roundness metric yet.
    angles = np.degrees(mesh.face_adjacency_angles)
    angularity = float(np.percentile(angles, 95))

    return {
        "diameter_nominal_m": (6 * volume / np.pi) ** (1 / 3) * scale,
        "volume_m3": volume * scale**3,
        "area_m2": area * scale**2,
        "L_m": L * scale,
        "I_m": I * scale,
        "S_m": S * scale,
        "elongation_IL": I / L,
        "flatness_SI": S / I,
        "sphericity": sphericity,
        "convexity": convexity,
        "angularity_deg": angularity,
    }
