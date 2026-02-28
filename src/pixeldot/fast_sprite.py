"""FastSprite: NumPy-backed high-performance sprite."""

from __future__ import annotations

from typing import Optional, Tuple

try:
    import numpy as np
except ImportError:
    raise ImportError(
        "FastSprite requires NumPy. Install it with: "
        "pip install pixeldot[perf]"
    )

from PIL import Image

from .color import TRANSPARENT, Color
from .sprite import Sprite


class FastSprite:
    """High-performance sprite using NumPy arrays.

    Same API as Sprite but backed by a NumPy ndarray of shape (H, W, 4)
    with dtype uint8. Significantly faster for large images (64x64+).
    """

    __slots__ = ("_data",)

    def __init__(self, data: np.ndarray) -> None:
        if data.ndim != 3 or data.shape[2] != 4:
            raise ValueError(
                f"Expected shape (H, W, 4), got {data.shape}"
            )
        if data.dtype != np.uint8:
            data = data.astype(np.uint8)
        self._data = data

    @property
    def width(self) -> int:
        return self._data.shape[1]

    @property
    def height(self) -> int:
        return self._data.shape[0]

    @property
    def size(self) -> Tuple[int, int]:
        return (self._data.shape[1], self._data.shape[0])

    def get_pixel(self, x: int, y: int) -> Color:
        """Get pixel color at (x, y). Origin is top-left."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise IndexError(
                f"({x}, {y}) out of bounds for {self.width}x{self.height}"
            )
        r, g, b, a = self._data[y, x]
        return (int(r), int(g), int(b), int(a))

    def to_image(self) -> Image.Image:
        """Convert to PIL Image (RGBA)."""
        return Image.fromarray(self._data, "RGBA")

    @classmethod
    def from_image(cls, img: Image.Image) -> FastSprite:
        """Create FastSprite from PIL Image."""
        img = img.convert("RGBA")
        data = np.array(img, dtype=np.uint8)
        return cls(data)

    @classmethod
    def empty(cls, w: int, h: int) -> FastSprite:
        """Create a transparent sprite of the given size."""
        data = np.zeros((h, w, 4), dtype=np.uint8)
        return cls(data)

    def crop(self, x: int, y: int, w: int, h: int) -> FastSprite:
        """Extract a sub-region. Clamps to bounds."""
        x = max(0, x)
        y = max(0, y)
        w = min(w, self.width - x)
        h = min(h, self.height - y)
        if w <= 0 or h <= 0:
            raise ValueError("Crop region is empty")
        return FastSprite(self._data[y : y + h, x : x + w].copy())

    def paste(self, other: FastSprite, x: int, y: int) -> FastSprite:
        """Paste another sprite with alpha compositing. Returns new FastSprite."""
        result = self._data.copy()

        # Compute overlap region
        sx_start = max(0, -x)
        sy_start = max(0, -y)
        sx_end = min(other.width, self.width - x)
        sy_end = min(other.height, self.height - y)

        if sx_start >= sx_end or sy_start >= sy_end:
            return FastSprite(result)

        tx_start = x + sx_start
        ty_start = y + sy_start
        tx_end = x + sx_end
        ty_end = y + sy_end

        src = other._data[sy_start:sy_end, sx_start:sx_end].astype(np.float32)
        dst = result[ty_start:ty_end, tx_start:tx_end].astype(np.float32)

        sa = src[:, :, 3:4] / 255.0
        da = dst[:, :, 3:4] / 255.0

        out_a = sa + da * (1.0 - sa)

        # Avoid division by zero
        safe_out_a = np.where(out_a > 0, out_a, 1.0)

        out_rgb = (src[:, :, :3] * sa + dst[:, :, :3] * da * (1.0 - sa)) / safe_out_a
        out_alpha = out_a * 255.0

        combined = np.concatenate([out_rgb, out_alpha], axis=2)
        result[ty_start:ty_end, tx_start:tx_end] = combined.astype(np.uint8)

        return FastSprite(result)

    def flip_h(self) -> FastSprite:
        """Flip horizontally."""
        return FastSprite(self._data[:, ::-1].copy())

    def flip_v(self) -> FastSprite:
        """Flip vertically."""
        return FastSprite(self._data[::-1].copy())

    def replace_color(self, old: Color, new: Color) -> FastSprite:
        """Replace all occurrences of one color with another."""
        old_arr = np.array(old, dtype=np.uint8)
        new_arr = np.array(new, dtype=np.uint8)
        data = self._data.copy()
        mask = np.all(data == old_arr, axis=2)
        data[mask] = new_arr
        return FastSprite(data)

    def opaque_bounds(self) -> Optional[Tuple[int, int, int, int]]:
        """Find bounding box of non-transparent pixels. Returns (x, y, w, h) or None."""
        alpha = self._data[:, :, 3]
        rows = np.any(alpha > 0, axis=1)
        cols = np.any(alpha > 0, axis=0)
        if not rows.any():
            return None
        min_y = int(np.argmax(rows))
        max_y = int(len(rows) - 1 - np.argmax(rows[::-1]))
        min_x = int(np.argmax(cols))
        max_x = int(len(cols) - 1 - np.argmax(cols[::-1]))
        return (min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)

    def trim(self) -> FastSprite:
        """Remove transparent border. Returns a cropped FastSprite."""
        bounds = self.opaque_bounds()
        if bounds is None:
            return FastSprite.empty(1, 1)
        return self.crop(*bounds)

    def to_sprite(self) -> Sprite:
        """Convert to regular Sprite."""
        pixels: list[list[Color]] = []
        for y in range(self.height):
            row: list[Color] = []
            for x in range(self.width):
                r, g, b, a = self._data[y, x]
                row.append((int(r), int(g), int(b), int(a)))
            pixels.append(row)
        return Sprite(pixels, _skip_copy=True)

    @classmethod
    def from_sprite(cls, sprite: Sprite) -> FastSprite:
        """Convert from regular Sprite."""
        data = np.zeros((sprite.height, sprite.width, 4), dtype=np.uint8)
        for y in range(sprite.height):
            for x in range(sprite.width):
                data[y, x] = sprite.get_pixel(x, y)
        return cls(data)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FastSprite):
            return NotImplemented
        return np.array_equal(self._data, other._data)

    def __repr__(self) -> str:
        return f"FastSprite({self.width}x{self.height})"
