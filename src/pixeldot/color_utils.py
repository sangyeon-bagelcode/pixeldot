"""Color utilities: HSL conversion, manipulation, ramps, dithering."""

from __future__ import annotations

import math
from typing import List, Tuple

from .color import Color


def rgb_to_hsl(color: Color) -> Tuple[float, float, float]:
    """Convert RGBA color to HSL. Returns (h, s, l) with h in [0,360), s,l in [0,1]."""
    r, g, b, _a = color
    rf, gf, bf = r / 255.0, g / 255.0, b / 255.0

    cmax = max(rf, gf, bf)
    cmin = min(rf, gf, bf)
    delta = cmax - cmin

    # Lightness
    l = (cmax + cmin) / 2.0

    if delta == 0:
        return (0.0, 0.0, l)

    # Saturation
    s = delta / (1.0 - abs(2.0 * l - 1.0))

    # Hue
    if cmax == rf:
        h = 60.0 * (((gf - bf) / delta) % 6)
    elif cmax == gf:
        h = 60.0 * (((bf - rf) / delta) + 2)
    else:
        h = 60.0 * (((rf - gf) / delta) + 4)

    return (h % 360.0, min(s, 1.0), l)


def hsl_to_rgb(h: float, s: float, l: float, a: int = 255) -> Color:
    """Convert HSL to RGBA color. h in [0,360), s,l in [0,1], a in [0,255]."""
    h = h % 360.0
    s = max(0.0, min(1.0, s))
    l = max(0.0, min(1.0, l))

    c = (1.0 - abs(2.0 * l - 1.0)) * s
    x = c * (1.0 - abs((h / 60.0) % 2 - 1.0))
    m = l - c / 2.0

    if h < 60:
        rf, gf, bf = c, x, 0.0
    elif h < 120:
        rf, gf, bf = x, c, 0.0
    elif h < 180:
        rf, gf, bf = 0.0, c, x
    elif h < 240:
        rf, gf, bf = 0.0, x, c
    elif h < 300:
        rf, gf, bf = x, 0.0, c
    else:
        rf, gf, bf = c, 0.0, x

    return (
        _clamp(round((rf + m) * 255)),
        _clamp(round((gf + m) * 255)),
        _clamp(round((bf + m) * 255)),
        a,
    )


def lighten(color: Color, amount: float = 0.2) -> Color:
    """Increase lightness by amount (0-1). Preserves alpha."""
    h, s, l = rgb_to_hsl(color)
    return hsl_to_rgb(h, s, min(1.0, l + amount), color[3])


def darken(color: Color, amount: float = 0.2) -> Color:
    """Decrease lightness by amount (0-1). Preserves alpha."""
    h, s, l = rgb_to_hsl(color)
    return hsl_to_rgb(h, s, max(0.0, l - amount), color[3])


def saturate(color: Color, amount: float = 0.2) -> Color:
    """Increase saturation by amount (0-1). Preserves alpha."""
    h, s, l = rgb_to_hsl(color)
    return hsl_to_rgb(h, min(1.0, s + amount), l, color[3])


def desaturate(color: Color, amount: float = 0.2) -> Color:
    """Decrease saturation by amount (0-1). Preserves alpha."""
    h, s, l = rgb_to_hsl(color)
    return hsl_to_rgb(h, max(0.0, s - amount), l, color[3])


def color_lerp(c1: Color, c2: Color, t: float) -> Color:
    """Linear interpolation between two colors. t=0 returns c1, t=1 returns c2."""
    t = max(0.0, min(1.0, t))
    return (
        _clamp(round(c1[0] + (c2[0] - c1[0]) * t)),
        _clamp(round(c1[1] + (c2[1] - c1[1]) * t)),
        _clamp(round(c1[2] + (c2[2] - c1[2]) * t)),
        _clamp(round(c1[3] + (c2[3] - c1[3]) * t)),
    )


def color_ramp(start: Color, end: Color, steps: int) -> List[Color]:
    """Generate a gradient of colors from start to end (inclusive)."""
    if steps < 2:
        raise ValueError("color_ramp requires at least 2 steps")
    return [color_lerp(start, end, i / (steps - 1)) for i in range(steps)]


def auto_shades(base_color: Color, count: int = 5) -> List[Color]:
    """Generate highlight-to-shadow shades from a base color."""
    if count < 2:
        raise ValueError("auto_shades requires at least 2 colors")
    h, s, l = rgb_to_hsl(base_color)
    # Range from highlight (high lightness) to shadow (low lightness)
    l_high = min(1.0, l + 0.3)
    l_low = max(0.0, l - 0.3)
    return [
        hsl_to_rgb(h, s, l_high + (l_low - l_high) * i / (count - 1), base_color[3])
        for i in range(count)
    ]


def dither_pattern(c1: Color, c2: Color, pattern: str = "checker") -> List[List[bool]]:
    """Return a 2D boolean pattern for dithering between two colors.

    True = c1, False = c2. Supported patterns: 'checker', 'horizontal', 'vertical'.
    """
    if pattern == "checker":
        return [
            [True, False],
            [False, True],
        ]
    if pattern == "horizontal":
        return [
            [True, True],
            [False, False],
        ]
    if pattern == "vertical":
        return [
            [True, False],
            [True, False],
        ]
    raise ValueError(f"Unknown dither pattern: {pattern!r}")


def color_distance(c1: Color, c2: Color) -> float:
    """Euclidean distance between two colors in RGBA space."""
    return math.sqrt(
        (c1[0] - c2[0]) ** 2
        + (c1[1] - c2[1]) ** 2
        + (c1[2] - c2[2]) ** 2
        + (c1[3] - c2[3]) ** 2
    )


def _clamp(v: int) -> int:
    """Clamp integer to [0, 255]."""
    return max(0, min(255, v))
