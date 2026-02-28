"""Immutable pixel data container."""

from __future__ import annotations

from typing import Optional, Tuple

from PIL import Image

from .color import TRANSPARENT, Color


class Sprite:
    """Immutable pixel data. All transforms return a new Sprite."""

    __slots__ = ("_pixels", "_width", "_height")

    def __init__(self, pixels: list[list[Color]], *, _skip_copy: bool = False) -> None:
        if not pixels or not pixels[0]:
            raise ValueError("Sprite must have at least 1x1 pixels")
        h = len(pixels)
        w = len(pixels[0])
        for i, row in enumerate(pixels):
            if len(row) != w:
                raise ValueError(
                    f"Row {i} has {len(row)} pixels, expected {w}"
                )
        if _skip_copy:
            self._pixels = pixels
        else:
            self._pixels = [row[:] for row in pixels]
        self._width = w
        self._height = h

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def size(self) -> Tuple[int, int]:
        return (self._width, self._height)

    def get_pixel(self, x: int, y: int) -> Color:
        """Get pixel color at (x, y). Origin is top-left."""
        if not (0 <= x < self._width and 0 <= y < self._height):
            raise IndexError(f"({x}, {y}) out of bounds for {self._width}x{self._height}")
        return self._pixels[y][x]

    def to_image(self) -> Image.Image:
        """Convert to PIL Image (RGBA)."""
        img = Image.new("RGBA", (self._width, self._height))
        for y in range(self._height):
            for x in range(self._width):
                img.putpixel((x, y), self._pixels[y][x])
        return img

    @classmethod
    def from_image(cls, img: Image.Image) -> Sprite:
        """Create Sprite from PIL Image."""
        img = img.convert("RGBA")
        w, h = img.size
        pixels = []
        for y in range(h):
            row = []
            for x in range(w):
                row.append(img.getpixel((x, y)))
            pixels.append(row)
        return cls(pixels, _skip_copy=True)

    @classmethod
    def empty(cls, w: int, h: int) -> Sprite:
        """Create a transparent sprite of the given size."""
        pixels = [[TRANSPARENT] * w for _ in range(h)]
        return cls(pixels, _skip_copy=True)

    def crop(self, x: int, y: int, w: int, h: int) -> Sprite:
        """Extract a sub-region. Clamps to bounds."""
        x = max(0, x)
        y = max(0, y)
        w = min(w, self._width - x)
        h = min(h, self._height - y)
        if w <= 0 or h <= 0:
            raise ValueError("Crop region is empty")
        pixels = [self._pixels[row][x : x + w] for row in range(y, y + h)]
        return Sprite(pixels, _skip_copy=True)

    def paste(self, other: Sprite, x: int, y: int) -> Sprite:
        """Paste another sprite with alpha compositing. Returns new Sprite."""
        pixels = [row[:] for row in self._pixels]
        for sy in range(other._height):
            ty = y + sy
            if ty < 0 or ty >= self._height:
                continue
            for sx in range(other._width):
                tx = x + sx
                if tx < 0 or tx >= self._width:
                    continue
                src = other._pixels[sy][sx]
                if src[3] == 0:
                    continue
                if src[3] == 255:
                    pixels[ty][tx] = src
                else:
                    dst = pixels[ty][tx]
                    sa = src[3] / 255.0
                    da = dst[3] / 255.0
                    out_a = sa + da * (1 - sa)
                    if out_a == 0:
                        pixels[ty][tx] = TRANSPARENT
                    else:
                        pixels[ty][tx] = (
                            int((src[0] * sa + dst[0] * da * (1 - sa)) / out_a),
                            int((src[1] * sa + dst[1] * da * (1 - sa)) / out_a),
                            int((src[2] * sa + dst[2] * da * (1 - sa)) / out_a),
                            int(out_a * 255),
                        )
        return Sprite(pixels, _skip_copy=True)

    def flip_h(self) -> Sprite:
        """Flip horizontally."""
        pixels = [row[::-1] for row in self._pixels]
        return Sprite(pixels, _skip_copy=True)

    def flip_v(self) -> Sprite:
        """Flip vertically."""
        pixels = [row[:] for row in reversed(self._pixels)]
        return Sprite(pixels, _skip_copy=True)

    def replace_color(self, old: Color, new: Color) -> Sprite:
        """Replace all occurrences of one color with another."""
        pixels = []
        for row in self._pixels:
            pixels.append([new if c == old else c for c in row])
        return Sprite(pixels, _skip_copy=True)

    def opaque_bounds(self) -> Optional[Tuple[int, int, int, int]]:
        """Find bounding box of non-transparent pixels. Returns (x, y, w, h) or None."""
        min_x, min_y = self._width, self._height
        max_x, max_y = -1, -1
        for y in range(self._height):
            for x in range(self._width):
                if self._pixels[y][x][3] > 0:
                    min_x = min(min_x, x)
                    min_y = min(min_y, y)
                    max_x = max(max_x, x)
                    max_y = max(max_y, y)
        if max_x == -1:
            return None
        return (min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)

    def trim(self) -> Sprite:
        """Remove transparent border. Returns a cropped Sprite."""
        bounds = self.opaque_bounds()
        if bounds is None:
            return Sprite.empty(1, 1)
        return self.crop(*bounds)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Sprite):
            return NotImplemented
        return (
            self._width == other._width
            and self._height == other._height
            and self._pixels == other._pixels
        )

    def __repr__(self) -> str:
        return f"Sprite({self._width}x{self._height})"
