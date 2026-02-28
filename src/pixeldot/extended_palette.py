"""Extended palette support: multi-character keys and auto-palette generation."""

from __future__ import annotations

import string
import textwrap
from collections import Counter
from typing import Dict, List, Optional, Tuple, Union

from .color import Color, Palette, hex_to_color
from .sprite import Sprite


class MultiCharPalette:
    """Palette with fixed-length multi-character keys."""

    def __init__(self, mapping: Dict[str, Union[Color, str]], key_length: int = 2) -> None:
        self._key_length = key_length
        self._map: Dict[str, Color] = {}
        for key, value in mapping.items():
            if len(key) != key_length:
                raise ValueError(
                    f"Key {key!r} has length {len(key)}, expected {key_length}"
                )
            if isinstance(value, str):
                self._map[key] = hex_to_color(value)
            else:
                self._map[key] = value

    @property
    def key_length(self) -> int:
        return self._key_length

    def __getitem__(self, key: str) -> Color:
        try:
            return self._map[key]
        except KeyError:
            raise KeyError(f"Key {key!r} not found in palette")

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

    def reverse_lookup(self, color: Color) -> Optional[str]:
        """Find the key for a given color. Returns None if not found."""
        for key, val in self._map.items():
            if val == color:
                return key
        return None

    def render(self, rows: List[str]) -> Sprite:
        """Render rows where every key_length chars map to one pixel."""
        if not rows:
            raise ValueError("Empty rows")
        rows = [r for r in rows if r]
        if not rows:
            raise ValueError("All rows are empty")

        kl = self._key_length
        width = len(rows[0])
        if width % kl != 0:
            raise ValueError(
                f"Row length {width} is not divisible by key_length {kl}"
            )
        pixel_width = width // kl

        for i, row in enumerate(rows):
            if len(row) != width:
                raise ValueError(
                    f"Row {i} has {len(row)} chars, expected {width}"
                )

        pixels: list[list[Color]] = []
        for y, row in enumerate(rows):
            pixel_row: list[Color] = []
            for i in range(0, width, kl):
                key = row[i : i + kl]
                if key not in self._map:
                    raise KeyError(
                        f"Key {key!r} at pixel ({i // kl}, {y}) not in palette"
                    )
                pixel_row.append(self._map[key])
            pixels.append(pixel_row)

        return Sprite(pixels, _skip_copy=True)

    def render_block(self, block: str) -> Sprite:
        """Like StringCanvas.render_block but with multi-char keys."""
        text = textwrap.dedent(block)
        lines = text.split("\n")
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        if not lines:
            raise ValueError("Block is empty after stripping")
        return self.render(lines)

    def to_string(self, sprite: Sprite) -> List[str]:
        """Reverse render: convert Sprite back to string rows."""
        rows: List[str] = []
        for y in range(sprite.height):
            keys: list[str] = []
            for x in range(sprite.width):
                color = sprite.get_pixel(x, y)
                key = self.reverse_lookup(color)
                if key is None:
                    raise KeyError(
                        f"Color {color} at ({x}, {y}) has no palette entry"
                    )
                keys.append(key)
            rows.append("".join(keys))
        return rows


# Characters available for auto-assignment (a-z, A-Z, 0-9)
_SINGLE_CHARS = list(string.ascii_lowercase + string.ascii_uppercase + string.digits)


class AutoPalette:
    """Automatically assign character keys to colors from an existing sprite."""

    @classmethod
    def from_sprite(
        cls, sprite: Sprite, max_single_char: int = 62
    ) -> Tuple[Union[Palette, MultiCharPalette], List[str]]:
        """Analyze sprite and return (palette, string_rows).

        Most frequent colors get single-char keys (a-z, A-Z, 0-9).
        If there are more unique colors than max_single_char, returns
        a MultiCharPalette with 2-char keys.
        """
        # Count color frequencies
        counter: Counter[Color] = Counter()
        for y in range(sprite.height):
            for x in range(sprite.width):
                counter[sprite.get_pixel(x, y)] += 1

        colors_by_freq = [c for c, _ in counter.most_common()]

        if len(colors_by_freq) <= min(max_single_char, len(_SINGLE_CHARS)):
            # Use single-char palette
            mapping: Dict[str, Color] = {}
            color_to_key: Dict[Color, str] = {}
            for i, color in enumerate(colors_by_freq):
                key = _SINGLE_CHARS[i]
                mapping[key] = color
                color_to_key[color] = key
            palette = Palette(mapping)
            rows: List[str] = []
            for y in range(sprite.height):
                chars: list[str] = []
                for x in range(sprite.width):
                    chars.append(color_to_key[sprite.get_pixel(x, y)])
                rows.append("".join(chars))
            return palette, rows
        else:
            # Use 2-char palette
            two_chars = _SINGLE_CHARS
            keys_2: list[str] = []
            for a in two_chars:
                for b in two_chars:
                    keys_2.append(a + b)
                    if len(keys_2) >= len(colors_by_freq):
                        break
                if len(keys_2) >= len(colors_by_freq):
                    break

            mapping_2: Dict[str, Color] = {}
            color_to_key_2: Dict[Color, str] = {}
            for i, color in enumerate(colors_by_freq):
                key = keys_2[i]
                mapping_2[key] = color
                color_to_key_2[color] = key
            mcp = MultiCharPalette(mapping_2, key_length=2)
            rows_2: List[str] = []
            for y in range(sprite.height):
                keys: list[str] = []
                for x in range(sprite.width):
                    keys.append(color_to_key_2[sprite.get_pixel(x, y)])
                rows_2.append("".join(keys))
            return mcp, rows_2

    @classmethod
    def from_image(cls, path: str) -> Tuple[Union[Palette, MultiCharPalette], List[str]]:
        """Load image and convert to palette + strings."""
        from .io import load

        sprite = load(path)
        return cls.from_sprite(sprite)
