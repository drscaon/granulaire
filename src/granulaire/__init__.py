"""Granulaire: realistic granular assets generator for physical AI, exporting to OpenUSD."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("granulaire")
except PackageNotFoundError:  # running from a source tree without installation
    __version__ = "0.0.0+unknown"

from .generator import Scene, Variations, generate_scene, write_outputs  # noqa: E402
from .presets import CATEGORIES, PRESETS  # noqa: E402

__all__ = [
    "CATEGORIES",
    "PRESETS",
    "Scene",
    "Variations",
    "__version__",
    "generate_scene",
    "write_outputs",
]
