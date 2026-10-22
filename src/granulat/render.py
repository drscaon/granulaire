"""CPU previews: shape sheet, mixed-scene preview, metrics chart, moisture states.

Minimal software rendering (no GPU): orthographic projection, Lambert shading
plus an optional Blinn-Phong highlight, back-face culling and depth sorting.
Grains are (nearly) convex, so this is enough for a correct picture.

Requires the optional dependency: pip install "granulat[render]".
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

from .moisture import LABELS, STATE_PARAMS, STATES, wet_color

LIGHT = np.array([-0.4, 0.5, 0.77])
LIGHT /= np.linalg.norm(LIGHT)
HALF = LIGHT + np.array([0.0, 0.0, 1.0])
HALF /= np.linalg.norm(HALF)
VIEW_TILT = np.radians(-35)  # tilted camera: shows the top and one side
R_VIEW = np.array(
    [[1, 0, 0], [0, np.cos(VIEW_TILT), -np.sin(VIEW_TILT)], [0, np.sin(VIEW_TILT), np.cos(VIEW_TILT)]]
)
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]
INK, INK2, GRID = "#1f1f1e", "#5f5e58", "#e6e4dd"


def _plt():
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.collections import PolyCollection
    except ImportError as exc:  # pragma: no cover - depends on the environment
        raise SystemExit('rendering needs matplotlib: pip install "granulat[render]"') from exc
    return plt, PolyCollection


def quat_to_matrix(w, x, y, z):
    return np.array(
        [
            [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
        ]
    )


def _yaw(a):
    return (np.cos(a / 2), 0.0, 0.0, np.sin(a / 2))


def shade_mesh(verts, faces, color, state=None):
    """Visible faces of a mesh already in camera space (z towards the eye)."""
    tri = verts[faces]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-20
    visible = n[:, 2] > 0
    n = n[visible]
    base = np.asarray(wet_color(color, state) if state else color)
    rgb = base[None, :] * (0.28 + 0.85 * np.clip(n @ LIGHT, 0, 1)[:, None])
    if state:
        p = STATE_PARAMS[state]
        shininess = 4 + 300 * (1 - p["rough"]) ** 2
        strength = 0.04 + 0.5 * (1 - p["rough"]) * (0.5 + 0.5 * p["coat"])
        rgb = rgb + (strength * np.clip(n @ HALF, 0, 1) ** shininess)[:, None]
    depth = tri[visible][:, :, 2].mean(axis=1)
    return tri[visible][:, :, :2], np.clip(rgb, 0, 1), depth


def _load(folder: Path):
    summary = json.loads((folder / "summary.json").read_text())
    return summary, np.load(folder / "prototypes.npz")


def shape_sheet(folder: Path) -> Path:
    plt, PolyCollection = _plt()
    summary, data = _load(folder)
    colors = data["colors"]
    n = len(colors)
    cols = 10
    rows = int(np.ceil(n / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 1.25, rows * 1.25 + 0.6), dpi=130, squeeze=False)
    fig.patch.set_facecolor("white")
    rng = np.random.default_rng(0)
    for i, ax in enumerate(axes.ravel()):
        ax.set_axis_off()
        if i >= n:
            continue
        v = data[f"v{i}"]
        # each grain laid flat on its largest face (S axis vertical), seen at three-quarters
        c = np.linalg.svd(v - v.mean(axis=0), full_matrices=False)[2]
        v = (v @ c.T) @ quat_to_matrix(*_yaw(rng.uniform(0, 2 * np.pi))).T @ R_VIEW.T
        poly, rgb, depth = shade_mesh(v, data[f"f{i}"], colors[i])
        order = np.argsort(depth)
        ax.add_collection(
            PolyCollection(poly[order], facecolors=rgb[order], edgecolors="none", antialiased=False)
        )
        r = np.abs(v[:, :2]).max() * 1.05
        ax.set_xlim(-r, r)
        ax.set_ylim(-r, r)
        ax.set_aspect("equal")
        ax.text(0.03, 0.03, f"{i:02d}", transform=ax.transAxes, fontsize=6, color=INK2)
    fig.suptitle(
        f"{summary['label']} — {n} generated shapes (each grain at its own scale)",
        fontsize=12,
        color=INK,
        x=0.01,
        ha="left",
    )
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    out = folder / "shape_sheet.png"
    fig.savefig(out, facecolor="white")
    plt.close(fig)
    return out


def mix_preview(folder: Path, copies: int = 5, seed: int = 3) -> Path:
    """One layer of mixed grains resting on the ground, seen at three-quarters:
    each shape appears `copies` times at its true size with a random orientation."""
    plt, PolyCollection = _plt()
    summary, data = _load(folder)
    colors = data["colors"]
    n_shapes = len(colors)
    rng = np.random.default_rng(seed)
    order = rng.permutation(np.repeat(np.arange(n_shapes), copies))
    proto = [data[f"v{i}"] for i in range(n_shapes)]
    d = np.median([np.ptp(p, axis=0).max() for p in proto])
    side = int(np.ceil(np.sqrt(len(order))))
    pitch = 0.95 * d

    polys, rgbs, depths = [], [], []
    for j, k in enumerate(order):
        pos = np.array([(j % side - side / 2) * pitch, (j // side - side / 2) * pitch, 0.0])
        pos[:2] += rng.uniform(-0.3, 0.3, 2) * pitch
        u1, u2, u3 = rng.random(3)
        a, b = np.sqrt(1 - u1), np.sqrt(u1)
        q = (
            b * np.cos(2 * np.pi * u3),
            a * np.sin(2 * np.pi * u2),
            a * np.cos(2 * np.pi * u2),
            b * np.sin(2 * np.pi * u3),
        )
        v = proto[k] @ quat_to_matrix(*q).T
        v[:, 2] -= v[:, 2].min()
        p, c, z = shade_mesh((v + pos) @ R_VIEW.T, data[f"f{k}"], colors[k])
        polys.append(p)
        rgbs.append(c)
        depths.append(z)
    poly, rgb, depth = np.concatenate(polys), np.concatenate(rgbs), np.concatenate(depths)
    order_z = np.argsort(depth)

    fig, ax = plt.subplots(figsize=(10, 7.5), dpi=150)
    fig.patch.set_facecolor("white")
    ax.add_collection(
        PolyCollection(poly[order_z], facecolors=rgb[order_z], edgecolors="none", antialiased=False)
    )
    ax.set_xlim(poly[:, :, 0].min(), poly[:, :, 0].max())
    ax.set_ylim(poly[:, :, 1].min(), poly[:, :, 1].max())
    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.set_title(
        f"{summary['label']} — {len(order)} grains ({n_shapes} shapes × {copies}, shuffled, "
        "random orientations)",
        fontsize=12,
        color=INK,
        loc="left",
    )
    fig.tight_layout()
    out = folder / "mix_preview.png"
    fig.savefig(out, facecolor="white")
    plt.close(fig)
    return out


def _style(ax):
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    for s in ["left", "bottom"]:
        ax.spines[s].set_color(INK2)
    ax.tick_params(colors=INK2, labelsize=8)
    ax.grid(color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def metrics_chart(folders: list[Path], out: Path) -> Path:
    """Grading curve, Zingg diagram and angularity vs sphericity (up to 6 presets)."""
    plt, _ = _plt()
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.6), dpi=140)
    fig.patch.set_facecolor("white")
    ax1, ax2, ax3 = axes
    for ax in axes:
        _style(ax)

    for color, folder in zip(SERIES, folders, strict=False):
        label = json.loads((folder / "summary.json").read_text())["label"]
        rows = list(csv.DictReader(open(folder / "prototype_metrics.csv")))
        m = {
            k: np.array([float(r[k]) for r in rows])
            for k in ["diameter_nominal_m", "elongation_IL", "flatness_SI", "sphericity", "angularity_deg"]
        }
        d = np.sort(m["diameter_nominal_m"] * 1000)
        ax1.step(
            d, np.arange(1, len(d) + 1) / len(d) * 100, where="post", color=color, linewidth=2, label=label
        )
        for ax, x, y in [
            (ax2, m["elongation_IL"], m["flatness_SI"]),
            (ax3, m["angularity_deg"], m["sphericity"]),
        ]:
            ax.scatter(x, y, s=22, color=color, edgecolors="white", linewidths=0.8, label=label, zorder=3)

    ax1.set_xscale("log")
    ax1.set_xlabel("Nominal diameter (mm, log scale)", color=INK2, fontsize=9)
    ax1.set_ylabel("Cumulative passing (%)", color=INK2, fontsize=9)
    ax1.axvline(2, color=INK2, linewidth=0.8, linestyle=":")
    ax1.text(2, 102, "sand | gravel", ha="center", fontsize=7, color=INK2)
    ax1.set_ylim(0, 108)
    ax1.set_title("Grading curve", fontsize=10, color=INK, loc="left")

    ax2.axvline(2 / 3, color=INK2, linewidth=0.8, linestyle=":")
    ax2.axhline(2 / 3, color=INK2, linewidth=0.8, linestyle=":")
    for x, y, t in [(0.83, 0.97, "sphere"), (0.83, 0.03, "disc"), (0.35, 0.97, "rod"), (0.35, 0.03, "blade")]:
        ax2.text(x, y, t, fontsize=8, color=INK2, ha="center", va="center")
    ax2.set_xlim(0.2, 1.02)
    ax2.set_ylim(0, 1.02)
    ax2.set_xlabel("Elongation I/L", color=INK2, fontsize=9)
    ax2.set_ylabel("Flatness S/I", color=INK2, fontsize=9)
    ax2.set_title("Zingg diagram (measured shapes)", fontsize=10, color=INK, loc="left")

    ax3.set_xlabel("Angularity proxy (95th pct. dihedral angle, °)", color=INK2, fontsize=9)
    ax3.set_ylabel("Wadell sphericity", color=INK2, fontsize=9)
    ax3.set_title("Angularity vs sphericity", fontsize=10, color=INK, loc="left")
    ax1.legend(frameon=False, fontsize=8, loc="lower right")

    fig.suptitle("Metrics measured on the generated shapes", fontsize=12, color=INK, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(out, facecolor="white")
    plt.close(fig)
    return out


def moisture_states(folders: list[Path], out: Path) -> Path:
    """One representative grain per preset, shown in the four moisture states."""
    plt, PolyCollection = _plt()
    fig, axes = plt.subplots(len(folders), 4, figsize=(11, 2.9 * len(folders)), dpi=150, squeeze=False)
    fig.patch.set_facecolor("white")
    for r, folder in enumerate(folders):
        summary, data = _load(folder)
        water = summary.get("moisture", {}).get("median_water_content_pct", {})
        k = len(data["colors"]) // 2  # a fixed grain from the middle of the library
        v, f, color = data[f"v{k}"], data[f"f{k}"], data["colors"][k]
        c = np.linalg.svd(v - v.mean(axis=0), full_matrices=False)[2]
        v = (v @ c.T) @ R_VIEW.T
        lim = np.abs(v[:, :2]).max() * 1.08
        for col, s in enumerate(STATES):
            ax = axes[r, col]
            ax.set_axis_off()
            poly, rgb, depth = shade_mesh(v, f, color, s)
            order = np.argsort(depth)
            ax.add_collection(
                PolyCollection(poly[order], facecolors=rgb[order], edgecolors="none", antialiased=False)
            )
            ax.set_xlim(-lim, lim)
            ax.set_ylim(-lim, lim)
            ax.set_aspect("equal")
            pct = water.get(s)
            ax.set_title(
                LABELS[s] + (f"  ·  water {pct:.1f} %" if pct is not None else ""),
                fontsize=9,
                color=INK2,
                pad=2,
            )
        axes[r, 0].text(
            -0.08,
            0.5,
            summary["label"],
            transform=axes[r, 0].transAxes,
            rotation=90,
            va="center",
            ha="right",
            fontsize=10,
            color=INK,
        )
    fig.tight_layout()
    fig.savefig(out, facecolor="white")
    plt.close(fig)
    return out


def moisture_gallery(folders: list[Path], out: Path, grains: int = 5, tile: float = 0.62) -> Path:
    """Gallery: one row per preset, `grains` different grains shown in each moisture state.

    Each grain is drawn at its own scale (sizes differ by orders of magnitude
    between presets). Presets without moisture (regoliths) show the dry state only.
    """
    from .presets import PRESETS

    plt, PolyCollection = _plt()
    n_rows, n_states = len(folders), len(STATES)
    label_w, gap, head_h, row_gap = 2.1, 0.22, 0.55, 0.06
    width = label_w + n_states * grains * tile + (n_states - 1) * gap + 0.15
    height = head_h + n_rows * (tile + row_gap) + 0.1
    fig = plt.figure(figsize=(width, height), dpi=150)
    fig.patch.set_facecolor("white")

    def box(x_in, y_in, w_in, h_in):
        return [x_in / width, 1 - (y_in + h_in) / height, w_in / width, h_in / height]

    for c, s in enumerate(STATES):
        x0 = label_w + c * (grains * tile + gap)
        fig.text(
            (x0 + grains * tile / 2) / width,
            1 - 0.32 / height,
            LABELS[s],
            ha="center",
            va="center",
            fontsize=11,
            color=INK,
            weight="bold",
        )

    for r, folder in enumerate(folders):
        summary, data = _load(folder)
        preset = PRESETS.get(summary["preset"], {})
        has_moisture = preset.get("moisture", True)
        y0 = head_h + r * (tile + row_gap)
        fig.text(
            0.12 / width,
            1 - (y0 + tile / 2) / height,
            summary["label"],
            ha="left",
            va="center",
            fontsize=9.5,
            color=INK,
        )
        n_shapes = len(data["colors"])
        picks = np.linspace(0, n_shapes - 1, grains).round().astype(int)
        views = []
        for k in picks:
            v = data[f"v{k}"]
            axes_ = np.linalg.svd(v - v.mean(axis=0), full_matrices=False)[2]
            views.append(((v @ axes_.T) @ R_VIEW.T, data[f"f{k}"], data["colors"][k]))
        for c, s in enumerate(STATES):
            x0 = label_w + c * (grains * tile + gap)
            if not has_moisture and s != "dry":
                if c == 1:
                    fig.text(
                        (x0 + 0.1) / width,
                        1 - (y0 + tile / 2) / height,
                        f"no moisture ({preset.get('moisture_note', 'no liquid water')})",
                        ha="left",
                        va="center",
                        fontsize=8.5,
                        color=INK2,
                        style="italic",
                    )
                continue
            for g, (v, f, color) in enumerate(views):
                ax = fig.add_axes(box(x0 + g * tile, y0, tile, tile))
                ax.set_axis_off()
                poly, rgb, depth = shade_mesh(v, f, color, s)
                order = np.argsort(depth)
                ax.add_collection(
                    PolyCollection(poly[order], facecolors=rgb[order], edgecolors="none", antialiased=False)
                )
                lim = np.abs(v[:, :2]).max() * 1.1
                ax.set_xlim(-lim, lim)
                ax.set_ylim(-lim, lim)
                ax.set_aspect("equal")
    fig.savefig(out, facecolor="white")
    plt.close(fig)
    return out
