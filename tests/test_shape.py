import numpy as np
import pytest
import trimesh

from granulat.measure import measure
from granulat.shape import make_grain

BASE = {
    "elongation": 0.7,
    "flatness": 0.7,
    "facets": 14,
    "roundness_p": 6.0,
    "roughness": 0.0,
    "diameter_m": 0.008,
    "subdivisions": 3,
}


def test_grain_has_target_nominal_diameter():
    verts, faces = make_grain(np.random.default_rng(0), BASE)
    assert measure(verts, faces)["diameter_nominal_m"] == pytest.approx(0.008, rel=1e-6)


def test_grain_is_centred_and_convex():
    verts, faces = make_grain(np.random.default_rng(1), BASE)
    m = measure(verts, faces)
    assert m["convexity"] > 0.99
    centre = trimesh.Trimesh(verts, faces, process=False).center_mass
    assert np.abs(centre).max() < 1e-9


def test_sharper_edges_lower_sphericity():
    rounded = measure(*make_grain(np.random.default_rng(2), {**BASE, "roundness_p": 2.0}))
    sharp = measure(*make_grain(np.random.default_rng(2), {**BASE, "roundness_p": 40.0}))
    assert sharp["sphericity"] < rounded["sphericity"]


def test_sphere_reference_is_a_sphere():
    verts, faces = make_grain(np.random.default_rng(3), {**BASE, "sphere": True})
    m = measure(verts, faces)
    assert m["sphericity"] > 0.99
    assert m["elongation_IL"] == pytest.approx(1.0, abs=0.02)


def test_irregularity_breaks_convexity_and_chips_cut_flat_faces():
    smooth = measure(*make_grain(np.random.default_rng(4), BASE))
    pitted = measure(*make_grain(np.random.default_rng(4), {**BASE, "lumpiness": 0.15, "pits": 6}))
    assert pitted["convexity"] < smooth["convexity"] - 0.01

    verts, faces = make_grain(np.random.default_rng(5), {**BASE, "roundness_p": 2.0, "chips": 3})
    normals = trimesh.Trimesh(verts, faces, process=False).face_normals
    # a fracture plane shows up as many faces sharing one normal
    _, counts = np.unique(np.round(normals, 2), axis=0, return_counts=True)
    assert counts.max() > 50


def test_grain_mesh_is_watertight():
    params = {**BASE, "chips": 4, "lumpiness": 0.1, "pits": 3, "taper": 0.2}
    verts, faces = make_grain(np.random.default_rng(6), params)
    assert trimesh.Trimesh(verts, faces, process=False).is_watertight
