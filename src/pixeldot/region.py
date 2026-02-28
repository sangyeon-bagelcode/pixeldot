"""Region-based multi-part sprite layout."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from .sprite import Sprite


@dataclass(frozen=True)
class Region:
    """A named rectangular region within a canvas."""
    name: str
    x: int
    y: int
    width: int
    height: int


class RegionLayout:
    """Define named regions within a canvas and compose/decompose sprites.

    Useful for multi-part sprites (e.g. weapon = blade + hilt + guard).
    """

    def __init__(
        self,
        canvas_size: Tuple[int, int],
        regions: List[Region],
    ) -> None:
        self._width, self._height = canvas_size
        self._regions = {r.name: r for r in regions}

        # Validate regions fit within canvas
        for r in regions:
            if r.x < 0 or r.y < 0:
                raise ValueError(f"Region {r.name!r} has negative offset")
            if r.x + r.width > self._width or r.y + r.height > self._height:
                raise ValueError(
                    f"Region {r.name!r} exceeds canvas bounds "
                    f"({r.x + r.width}x{r.y + r.height} > {self._width}x{self._height})"
                )

    @property
    def canvas_size(self) -> Tuple[int, int]:
        return (self._width, self._height)

    @property
    def regions(self) -> Dict[str, Region]:
        return dict(self._regions)

    def compose(self, parts: Dict[str, Sprite]) -> Sprite:
        """Compose named sprite parts into a single canvas.

        Parts not in the layout are ignored. Missing parts leave that region transparent.
        """
        result = Sprite.empty(self._width, self._height)
        for name, sprite in parts.items():
            if name not in self._regions:
                continue
            r = self._regions[name]
            # Crop sprite if it's larger than the region
            src = sprite
            if src.width > r.width or src.height > r.height:
                src = src.crop(0, 0, r.width, r.height)
            result = result.paste(src, r.x, r.y)
        return result

    def decompose(self, sprite: Sprite) -> Dict[str, Sprite]:
        """Extract named regions from a sprite."""
        parts: Dict[str, Sprite] = {}
        for name, r in self._regions.items():
            parts[name] = sprite.crop(r.x, r.y, r.width, r.height)
        return parts
