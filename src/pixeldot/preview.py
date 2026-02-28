"""Preview and scaling utilities."""

from __future__ import annotations

from typing import List, Optional, Tuple

from PIL import Image

from .color import Color
from .sprite import Sprite


def scale_nearest(sprite: Sprite, factor: int) -> Sprite:
    """Scale up using nearest-neighbor interpolation."""
    if factor < 1:
        raise ValueError(f"Scale factor must be >= 1, got {factor}")
    if factor == 1:
        return sprite

    w, h = sprite.width * factor, sprite.height * factor
    pixels: list[list[Color]] = []
    for y in range(h):
        row: list[Color] = []
        sy = y // factor
        for x in range(w):
            sx = x // factor
            row.append(sprite.get_pixel(sx, sy))
        pixels.append(row)
    return Sprite(pixels, _skip_copy=True)


def preview_image(
    sprite: Sprite,
    scale: int = 10,
    background: Optional[Color] = None,
) -> Image.Image:
    """Create an upscaled preview PIL Image.

    If background is provided, composites the sprite onto that color.
    """
    scaled = scale_nearest(sprite, scale)
    img = scaled.to_image()

    if background is not None:
        bg = Image.new("RGBA", img.size, background)
        bg.paste(img, (0, 0), img)
        return bg
    return img


def side_by_side(
    sprites: List[Sprite],
    scale: int = 10,
    gap: int = 2,
    background: Optional[Color] = None,
) -> Image.Image:
    """Place multiple sprites side by side for comparison.

    Args:
        sprites: List of sprites to display.
        scale: Scale factor for each sprite.
        gap: Gap between sprites in scaled pixels.
        background: Optional background color.
    """
    if not sprites:
        raise ValueError("No sprites to display")

    scaled = [scale_nearest(s, scale) for s in sprites]
    max_h = max(s.height for s in scaled)
    total_w = sum(s.width for s in scaled) + gap * (len(scaled) - 1)

    bg_color = background or (0, 0, 0, 0)
    result = Image.new("RGBA", (total_w, max_h), bg_color)

    x_offset = 0
    for s in scaled:
        img = s.to_image()
        result.paste(img, (x_offset, 0), img)
        x_offset += s.width + gap

    return result
