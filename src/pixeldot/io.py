"""PNG load/save utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Union

from PIL import Image

from .sprite import Sprite
from .preview import scale_nearest


def load(path: Union[str, Path]) -> Sprite:
    """Load a PNG file as a Sprite."""
    img = Image.open(path).convert("RGBA")
    return Sprite.from_image(img)


def save(sprite: Sprite, path: Union[str, Path]) -> None:
    """Save a Sprite as a PNG file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    img = sprite.to_image()
    img.save(str(path))


def save_preview(sprite: Sprite, path: Union[str, Path], scale: int = 10) -> None:
    """Save an upscaled preview of a Sprite."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    scaled = scale_nearest(sprite, scale)
    img = scaled.to_image()
    img.save(str(path))
