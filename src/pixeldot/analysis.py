"""Sprite analysis: palette extraction, bounds detection, hashing."""

from __future__ import annotations

import hashlib
from collections import Counter
from dataclasses import dataclass
from typing import List, Optional, Tuple

from .color import Color, color_to_hex
from .sprite import Sprite


@dataclass
class ColorInfo:
    """Information about a color's usage in a sprite."""
    color: Color
    hex: str
    count: int
    percentage: float


def extract_palette(sprite: Sprite, top_n: int = 12) -> List[ColorInfo]:
    """Extract the most used colors from a sprite.

    Transparent pixels are excluded from results.
    """
    counter: Counter[Color] = Counter()
    total_opaque = 0

    for y in range(sprite.height):
        for x in range(sprite.width):
            c = sprite.get_pixel(x, y)
            if c[3] > 0:
                counter[c] += 1
                total_opaque += 1

    if total_opaque == 0:
        return []

    result: List[ColorInfo] = []
    for color, count in counter.most_common(top_n):
        result.append(
            ColorInfo(
                color=color,
                hex=color_to_hex(color),
                count=count,
                percentage=round(count / total_opaque * 100, 1),
            )
        )
    return result


def color_count(sprite: Sprite) -> int:
    """Count unique non-transparent colors in a sprite."""
    colors: set[Color] = set()
    for y in range(sprite.height):
        for x in range(sprite.width):
            c = sprite.get_pixel(x, y)
            if c[3] > 0:
                colors.add(c)
    return len(colors)


def opaque_bounds(sprite: Sprite) -> Optional[Tuple[int, int, int, int]]:
    """Find bounding box of non-transparent pixels. Returns (x, y, w, h) or None."""
    return sprite.opaque_bounds()


def pixel_hash(sprite: Sprite) -> str:
    """Compute SHA-256 hash of pixel data for uniqueness checking."""
    h = hashlib.sha256()
    for y in range(sprite.height):
        for x in range(sprite.width):
            c = sprite.get_pixel(x, y)
            h.update(bytes(c))
    return h.hexdigest()
