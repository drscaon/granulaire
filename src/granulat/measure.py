"""Shape descriptors measured on the mesh actually generated.

We do not trust the input parameters: we measure what comes out.
"""

import numpy as np
import trimesh


def measure(verts, faces):
    mesh = trimesh.Trimesh(verts, faces, process=False)
    volume = abs(mesh.volume)
    area = mesh.area

    # dimensions L >= I >= S: oriented bounding box
    extents = np.sort(mesh.bounding_box_oriented.primitive.extents)[::-1]
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
        "diameter_nominal_m": (6 * volume / np.pi) ** (1 / 3),
        "volume_m3": volume,
        "area_m2": area,
        "L_m": L,
        "I_m": I,
        "S_m": S,
        "elongation_IL": I / L,
        "flatness_SI": S / I,
        "sphericity": sphericity,
        "convexity": convexity,
        "angularity_deg": angularity,
    }
