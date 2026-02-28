"""Style presets: retro palettes, outline, and shadow effects."""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional, Tuple

from .color import BLACK, TRANSPARENT, Color, Palette
from .sprite import Sprite


# ---------------------------------------------------------------------------
# Retro palette constants
# ---------------------------------------------------------------------------

GAMEBOY_PALETTE: Dict[str, Color] = {
    "lightest": (155, 188, 15, 255),
    "light": (139, 172, 15, 255),
    "dark": (48, 98, 48, 255),
    "darkest": (15, 56, 15, 255),
}

NES_PALETTE: Dict[str, Color] = {
    "black": (0, 0, 0, 255),
    "white": (255, 255, 255, 255),
    "red": (188, 0, 0, 255),
    "cyan": (0, 188, 188, 255),
    "purple": (136, 0, 160, 255),
    "green": (0, 168, 0, 255),
    "blue": (0, 0, 188, 255),
    "yellow": (228, 228, 0, 255),
    "orange": (188, 108, 0, 255),
    "brown": (100, 68, 0, 255),
    "light_red": (228, 92, 92, 255),
    "dark_grey": (80, 80, 80, 255),
    "grey": (120, 120, 120, 255),
    "light_green": (100, 228, 100, 255),
    "light_blue": (100, 100, 228, 255),
    "light_grey": (168, 168, 168, 255),
}

PICO8_PALETTE: Dict[str, Color] = {
    "black": (0, 0, 0, 255),
    "dark_blue": (29, 43, 83, 255),
    "dark_purple": (126, 37, 83, 255),
    "dark_green": (0, 135, 81, 255),
    "brown": (171, 82, 54, 255),
    "dark_grey": (95, 87, 79, 255),
    "light_grey": (194, 195, 199, 255),
    "white": (255, 241, 232, 255),
    "red": (255, 0, 77, 255),
    "orange": (255, 163, 0, 255),
    "yellow": (255, 236, 39, 255),
    "green": (0, 228, 54, 255),
    "blue": (41, 173, 255, 255),
    "lavender": (131, 118, 156, 255),
    "pink": (255, 119, 168, 255),
    "peach": (255, 204, 170, 255),
}

SWEETIE16_PALETTE: Dict[str, Color] = {
    "black": (26, 28, 44, 255),
    "purple": (93, 39, 93, 255),
    "red": (177, 62, 83, 255),
    "orange": (239, 125, 87, 255),
    "yellow": (255, 205, 117, 255),
    "light_green": (167, 240, 112, 255),
    "green": (56, 183, 100, 255),
    "dark_green": (37, 113, 121, 255),
    "dark_blue": (41, 54, 111, 255),
    "blue": (59, 93, 201, 255),
    "light_blue": (65, 166, 246, 255),
    "cyan": (115, 239, 247, 255),
    "white": (244, 244, 244, 255),
    "light_grey": (148, 176, 194, 255),
    "grey": (86, 108, 134, 255),
    "dark_grey": (51, 60, 87, 255),
}

ENDESGA32_PALETTE: Dict[str, Color] = {
    "void": (19, 19, 19, 255),
    "ash": (43, 43, 43, 255),
    "blind": (81, 81, 81, 255),
    "iron": (139, 139, 139, 255),
    "light": (198, 198, 198, 255),
    "white": (255, 255, 255, 255),
    "cocoa": (67, 28, 11, 255),
    "woody": (107, 46, 12, 255),
    "sandy": (168, 89, 26, 255),
    "skin": (224, 148, 80, 255),
    "salmon": (237, 195, 137, 255),
    "blood": (133, 18, 18, 255),
    "red": (209, 42, 42, 255),
    "orange": (233, 114, 36, 255),
    "gold": (239, 183, 51, 255),
    "yellow": (245, 232, 97, 255),
    "midnight": (25, 31, 68, 255),
    "dark_blue": (34, 60, 114, 255),
    "blue": (50, 105, 172, 255),
    "sea": (75, 160, 207, 255),
    "sky": (143, 211, 234, 255),
    "swamp": (18, 56, 18, 255),
    "forest": (26, 100, 26, 255),
    "green": (51, 161, 51, 255),
    "lime": (124, 209, 72, 255),
    "moss": (183, 232, 123, 255),
    "grape": (64, 18, 82, 255),
    "plum": (115, 30, 105, 255),
    "mauve": (174, 60, 134, 255),
    "pink": (232, 106, 164, 255),
    "rose": (237, 172, 192, 255),
    "teal": (42, 127, 116, 255),
}

_PRESET_PALETTES: Dict[str, Dict[str, Color]] = {
    "gameboy": GAMEBOY_PALETTE,
    "nes": NES_PALETTE,
    "pico8": PICO8_PALETTE,
    "sweetie16": SWEETIE16_PALETTE,
    "endesga32": ENDESGA32_PALETTE,
}


def list_preset_palettes() -> List[str]:
    """Return names of all available preset palettes."""
    return sorted(_PRESET_PALETTES.keys())


def get_preset_palette(name: str) -> Palette:
    """Look up a preset palette by name and return a Palette.

    Automatically assigns single-character keys based on name initials.
    """
    name_lower = name.lower()
    if name_lower not in _PRESET_PALETTES:
        raise KeyError(
            f"Unknown preset palette {name!r}. "
            f"Available: {', '.join(list_preset_palettes())}"
        )
    colors = _PRESET_PALETTES[name_lower]
    # Assign characters: digits 0-9, then a-z, then A-Z
    chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    mapping: Dict[str, Color | str] = {}
    for i, (_, color) in enumerate(colors.items()):
        if i >= len(chars):
            break
        mapping[chars[i]] = color
    return Palette(mapping)


# ---------------------------------------------------------------------------
# Outline
# ---------------------------------------------------------------------------

class OutlineStyle(Enum):
    """Outline rendering mode."""
    NONE = "none"
    THIN = "thin"
    THICK = "thick"
    SELECTIVE = "selective"


def apply_outline(
    sprite: Sprite,
    color: Color = BLACK,
    style: OutlineStyle = OutlineStyle.THIN,
) -> Sprite:
    """Add an outline around opaque pixels. Returns a new, larger Sprite."""
    if style == OutlineStyle.NONE:
        return sprite

    w, h = sprite.width, sprite.height

    if style == OutlineStyle.THIN:
        offsets = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    elif style == OutlineStyle.THICK:
        offsets = [
            (-1, -1), (0, -1), (1, -1),
            (-1, 0),           (1, 0),
            (-1, 1),  (0, 1),  (1, 1),
        ]
    elif style == OutlineStyle.SELECTIVE:
        # Only outline bottom and right for a shadow-like effect
        offsets = [(1, 0), (0, 1), (1, 1)]
    else:
        raise ValueError(f"Unknown outline style: {style!r}")

    # Expand canvas by 2 in each direction for outline room
    new_w = w + 2
    new_h = h + 2
    pixels: list[list[Color]] = [[TRANSPARENT] * new_w for _ in range(new_h)]

    # Draw outline first
    for y in range(h):
        for x in range(w):
            if sprite.get_pixel(x, y)[3] > 0:
                for dx, dy in offsets:
                    nx, ny = x + 1 + dx, y + 1 + dy
                    if 0 <= nx < new_w and 0 <= ny < new_h:
                        if pixels[ny][nx][3] == 0:
                            pixels[ny][nx] = color

    # Draw original pixels on top (offset by 1,1)
    for y in range(h):
        for x in range(w):
            px = sprite.get_pixel(x, y)
            if px[3] > 0:
                pixels[y + 1][x + 1] = px

    return Sprite(pixels, _skip_copy=True)


# ---------------------------------------------------------------------------
# Shadow
# ---------------------------------------------------------------------------

def apply_shadow(
    sprite: Sprite,
    offset: Tuple[int, int] = (1, 1),
    color: Optional[Color] = None,
    opacity: float = 0.5,
) -> Sprite:
    """Add a drop shadow behind opaque pixels. Returns a new Sprite."""
    shadow_color = color or BLACK
    # Compute alpha for shadow
    shadow_a = max(0, min(255, round(opacity * 255)))
    shadow_rgba: Color = (shadow_color[0], shadow_color[1], shadow_color[2], shadow_a)

    ox, oy = offset
    # Compute new canvas size to fit sprite + shadow
    min_x = min(0, ox)
    min_y = min(0, oy)
    max_x = max(sprite.width, sprite.width + ox)
    max_y = max(sprite.height, sprite.height + oy)
    new_w = max_x - min_x
    new_h = max_y - min_y

    pixels: list[list[Color]] = [[TRANSPARENT] * new_w for _ in range(new_h)]

    # Sprite origin in new canvas
    sx = -min_x
    sy = -min_y

    # Draw shadow
    for y in range(sprite.height):
        for x in range(sprite.width):
            if sprite.get_pixel(x, y)[3] > 0:
                nx = sx + x + ox
                ny = sy + y + oy
                if 0 <= nx < new_w and 0 <= ny < new_h:
                    pixels[ny][nx] = shadow_rgba

    # Draw sprite on top
    for y in range(sprite.height):
        for x in range(sprite.width):
            px = sprite.get_pixel(x, y)
            if px[3] > 0:
                pixels[sy + y][sx + x] = px

    return Sprite(pixels, _skip_copy=True)
