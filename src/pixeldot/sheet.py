"""Sprite sheet packing: strip (animation) and grid (collection)."""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from .sprite import Sprite


class StripSheet:
    """Horizontal strip of animation frames.

    All frames must have the same dimensions.
    """

    def __init__(self, frames: List[Sprite]) -> None:
        if not frames:
            raise ValueError("StripSheet requires at least 1 frame")
        w, h = frames[0].size
        for i, f in enumerate(frames):
            if f.size != (w, h):
                raise ValueError(
                    f"Frame {i} size {f.size} doesn't match first frame {(w, h)}"
                )
        self._frames = list(frames)

    @property
    def frames(self) -> List[Sprite]:
        return list(self._frames)

    @property
    def frame_count(self) -> int:
        return len(self._frames)

    @property
    def frame_size(self) -> Tuple[int, int]:
        return self._frames[0].size

    def to_sprite(self) -> Sprite:
        """Pack all frames into a horizontal strip."""
        fw, fh = self.frame_size
        result = Sprite.empty(fw * len(self._frames), fh)
        for i, frame in enumerate(self._frames):
            result = result.paste(frame, i * fw, 0)
        return result

    @classmethod
    def from_sprite(cls, sprite: Sprite, frame_width: int) -> StripSheet:
        """Split a horizontal strip into frames."""
        if sprite.width % frame_width != 0:
            raise ValueError(
                f"Sprite width {sprite.width} not divisible by frame_width {frame_width}"
            )
        count = sprite.width // frame_width
        frames = [sprite.crop(i * frame_width, 0, frame_width, sprite.height) for i in range(count)]
        return cls(frames)


class GridSheet:
    """Grid-based sprite collection packing."""

    def __init__(
        self,
        sprites: Dict[str, Sprite],
        columns: int,
        cell_size: Optional[Tuple[int, int]] = None,
        padding: int = 0,
    ) -> None:
        if not sprites:
            raise ValueError("GridSheet requires at least 1 sprite")
        if columns < 1:
            raise ValueError(f"columns must be >= 1, got {columns}")

        self._sprites = dict(sprites)
        self._columns = columns
        self._padding = padding
        self._names = list(sprites.keys())

        if cell_size:
            self._cell_w, self._cell_h = cell_size
        else:
            self._cell_w = max(s.width for s in sprites.values())
            self._cell_h = max(s.height for s in sprites.values())

    @property
    def cell_size(self) -> Tuple[int, int]:
        return (self._cell_w, self._cell_h)

    def to_sprite(self) -> Sprite:
        """Pack all sprites into a grid."""
        rows = (len(self._names) + self._columns - 1) // self._columns
        total_w = self._columns * (self._cell_w + self._padding) - self._padding
        total_h = rows * (self._cell_h + self._padding) - self._padding
        total_w = max(1, total_w)
        total_h = max(1, total_h)

        result = Sprite.empty(total_w, total_h)
        for idx, name in enumerate(self._names):
            col = idx % self._columns
            row = idx // self._columns
            x = col * (self._cell_w + self._padding)
            y = row * (self._cell_h + self._padding)
            result = result.paste(self._sprites[name], x, y)
        return result

    def get_metadata(self) -> List[Dict]:
        """Get position metadata for each sprite in the grid.

        Returns a list of dicts with: name, x, y, w, h.
        """
        meta: List[Dict] = []
        for idx, name in enumerate(self._names):
            col = idx % self._columns
            row = idx // self._columns
            x = col * (self._cell_w + self._padding)
            y = row * (self._cell_h + self._padding)
            s = self._sprites[name]
            meta.append({
                "name": name,
                "x": x,
                "y": y,
                "w": s.width,
                "h": s.height,
            })
        return meta
