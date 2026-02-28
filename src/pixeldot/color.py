"""Color types and Palette for single-character pixel mapping."""

from __future__ import annotations

from typing import Dict, Optional, Tuple

Color = Tuple[int, int, int, int]  # RGBA

TRANSPARENT: Color = (0, 0, 0, 0)
BLACK: Color = (0, 0, 0, 255)
WHITE: Color = (255, 255, 255, 255)


def rgba(r: int, g: int, b: int, a: int = 255) -> Color:
    """Create an RGBA color tuple."""
    return (r, g, b, a)


def hex_to_color(hex_str: str) -> Color:
    """Convert hex string to RGBA color.

    Supports: "#RGB", "#RGBA", "#RRGGBB", "#RRGGBBAA" (with or without #).
    """
    h = hex_str.lstrip("#")
    if len(h) == 3:
        r, g, b = (int(c * 2, 16) for c in h)
        return (r, g, b, 255)
    if len(h) == 4:
        r, g, b, a = (int(c * 2, 16) for c in h)
        return (r, g, b, a)
    if len(h) == 6:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)
    if len(h) == 8:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(h[6:8], 16))
    raise ValueError(f"Invalid hex color: {hex_str!r}")


def color_to_hex(color: Color) -> str:
    """Convert RGBA color to hex string (e.g. '#FF8800' or '#FF880080')."""
    r, g, b, a = color
    if a == 255:
        return f"#{r:02X}{g:02X}{b:02X}"
    return f"#{r:02X}{g:02X}{b:02X}{a:02X}"


class Palette:
    """Single-character to RGBA color mapping.

    Keys must be exactly 1 character. Values can be Color tuples or hex strings.
    The '.' character conventionally maps to TRANSPARENT.
    """

    def __init__(self, mapping: Dict[str, Color | str]) -> None:
        self._map: Dict[str, Color] = {}
        for key, value in mapping.items():
            if len(key) != 1:
                raise ValueError(
                    f"Palette key must be exactly 1 character, got {key!r} (len={len(key)})"
                )
            if isinstance(value, str):
                self._map[key] = hex_to_color(value)
            else:
                self._map[key] = value

    def __getitem__(self, key: str) -> Color:
        try:
            return self._map[key]
        except KeyError:
            raise KeyError(f"Character {key!r} not found in palette")

    def __contains__(self, key: str) -> bool:
        return key in self._map

    def __len__(self) -> int:
        return len(self._map)

    def __iter__(self):
        return iter(self._map)

    def keys(self):
        return self._map.keys()

    def items(self):
        return self._map.items()

    def with_updates(self, **overrides: Color | str) -> Palette:
        """Return a new Palette with the given overrides applied."""
        new_map: Dict[str, Color | str] = dict(self._map)
        new_map.update(overrides)
        return Palette(new_map)

    def reverse_lookup(self, color: Color) -> Optional[str]:
        """Find the character key for a given color. Returns None if not found."""
        for key, val in self._map.items():
            if val == color:
                return key
        return None
