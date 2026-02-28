"""StringCanvas: the core string-to-Sprite renderer."""

from __future__ import annotations

import textwrap
from typing import List, Optional

from .color import Color, Palette
from .sprite import Sprite


class StringCanvas:
    """Renders single-character-per-pixel string art into Sprites.

    Each character in the input maps to one pixel via the Palette.
    This is the key to 10-15x token savings over tuple arrays.

    Example::

        p = Palette({'.': TRANSPARENT, 'K': BLACK, 'r': '#FF0000'})
        canvas = StringCanvas(p)
        sprite = canvas.render_block('''
            ..KK..
            .KrrK.
            KrrrrK
            .KrrK.
            ..KK..
        ''')
    """

    def __init__(self, palette: Palette) -> None:
        self._palette = palette

    @property
    def palette(self) -> Palette:
        return self._palette

    def render(self, rows: List[str]) -> Sprite:
        """Render a list of strings into a Sprite.

        Each character maps to one pixel. All rows must have the same length.
        """
        if not rows:
            raise ValueError("Empty rows")

        # Filter out empty rows
        rows = [r for r in rows if r]
        if not rows:
            raise ValueError("All rows are empty")

        width = len(rows[0])
        for i, row in enumerate(rows):
            if len(row) != width:
                raise ValueError(
                    f"Row {i} has {len(row)} chars, expected {width} "
                    f"(row: {row!r})"
                )

        pixels: list[list[Color]] = []
        for y, row in enumerate(rows):
            pixel_row: list[Color] = []
            for x, ch in enumerate(row):
                if ch not in self._palette:
                    raise KeyError(
                        f"Character {ch!r} at ({x}, {y}) not in palette"
                    )
                pixel_row.append(self._palette[ch])
            pixels.append(pixel_row)

        return Sprite(pixels, _skip_copy=True)

    def render_block(self, block: str) -> Sprite:
        """Render a triple-quoted block string.

        Automatically handles dedent and strips leading/trailing blank lines.
        """
        text = textwrap.dedent(block)
        lines = text.split("\n")
        # Strip leading and trailing empty lines
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        if not lines:
            raise ValueError("Block is empty after stripping")
        return self.render(lines)

    @staticmethod
    def to_string(sprite: Sprite, palette: Palette) -> List[str]:
        """Reverse render: convert a Sprite back to string rows.

        Useful for editing existing PNGs in string format.
        Raises KeyError if a pixel color has no palette entry.
        """
        rows: List[str] = []
        for y in range(sprite.height):
            chars: list[str] = []
            for x in range(sprite.width):
                color = sprite.get_pixel(x, y)
                ch = palette.reverse_lookup(color)
                if ch is None:
                    raise KeyError(
                        f"Color {color} at ({x}, {y}) has no palette entry"
                    )
                chars.append(ch)
            rows.append("".join(chars))
        return rows
