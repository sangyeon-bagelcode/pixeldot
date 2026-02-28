"""TileMap system: large scenes from character grids of tile references."""

from __future__ import annotations

import textwrap
from typing import Dict, List, Optional, Tuple, Union

from .sprite import Sprite


class TileSet:
    """Named collection of tile sprites. All tiles must be the same size.

    Keys must be exactly 1 character, mapping to Sprite tiles.

    Example::

        tileset = TileSet({
            'g': grass_tile,   # 8x8 Sprite
            'w': water_tile,   # 8x8 Sprite
            't': tree_tile,    # 8x8 Sprite
        })
    """

    def __init__(
        self,
        tiles: Dict[str, Sprite],
        tile_size: Optional[Tuple[int, int]] = None,
    ) -> None:
        if not tiles:
            raise ValueError("TileSet must have at least one tile")

        for key in tiles:
            if len(key) != 1:
                raise ValueError(
                    f"Tile key must be exactly 1 character, got {key!r}"
                )

        if tile_size is not None:
            tw, th = tile_size
        else:
            first = next(iter(tiles.values()))
            tw, th = first.size

        for key, sprite in tiles.items():
            if sprite.size != (tw, th):
                raise ValueError(
                    f"Tile {key!r} has size {sprite.size}, "
                    f"expected ({tw}, {th})"
                )

        self._tiles = dict(tiles)
        self._tile_size = (tw, th)

    @property
    def tile_size(self) -> Tuple[int, int]:
        """(width, height) of each tile in pixels."""
        return self._tile_size

    def __getitem__(self, key: str) -> Sprite:
        try:
            return self._tiles[key]
        except KeyError:
            raise KeyError(f"Tile {key!r} not found in TileSet")

    def __contains__(self, key: str) -> bool:
        return key in self._tiles

    def __len__(self) -> int:
        return len(self._tiles)

    def keys(self) -> list[str]:
        return list(self._tiles.keys())

    def __repr__(self) -> str:
        tw, th = self._tile_size
        return f"TileSet({len(self._tiles)} tiles, {tw}x{th})"


class TileMap:
    """Large scene from a character grid of tile references.

    Uses the same "1 char = 1 tile" philosophy as StringCanvas uses
    "1 char = 1 pixel". A 32x32 grid with 8x8 tiles creates a 256x256
    pixel image, expressed in ~1024 characters.

    Example::

        tilemap = TileMap(tileset, '''
            ggggtttggg
            ggwwwwwggg
            ggwwwwwggg
            ggggggggtg
        ''')
        scene = tilemap.to_sprite()
    """

    def __init__(self, tileset: TileSet, grid: Union[str, List[str]]) -> None:
        self._tileset = tileset

        if isinstance(grid, str):
            rows = self._parse_block(grid)
        else:
            rows = [r for r in grid if r]

        if not rows:
            raise ValueError("TileMap grid is empty")

        width = len(rows[0])
        for i, row in enumerate(rows):
            if len(row) != width:
                raise ValueError(
                    f"Grid row {i} has {len(row)} chars, expected {width} "
                    f"(row: {row!r})"
                )
            for j, ch in enumerate(row):
                if ch not in tileset:
                    raise KeyError(
                        f"Character {ch!r} at grid ({j}, {i}) not in TileSet"
                    )

        self._rows = rows
        self._cols = width
        self._nrows = len(rows)

    @staticmethod
    def _parse_block(block: str) -> List[str]:
        """Parse a triple-quoted block string, matching StringCanvas.render_block."""
        text = textwrap.dedent(block)
        lines = text.split("\n")
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        return lines

    @property
    def grid_size(self) -> Tuple[int, int]:
        """(cols, rows) in tiles."""
        return (self._cols, self._nrows)

    @property
    def pixel_size(self) -> Tuple[int, int]:
        """(width, height) in pixels."""
        tw, th = self._tileset.tile_size
        return (self._cols * tw, self._nrows * th)

    def to_sprite(self) -> Sprite:
        """Render the full map by composing tiles into a single Sprite."""
        tw, th = self._tileset.tile_size
        pw, ph = self.pixel_size
        result = Sprite.empty(pw, ph)
        for gy, row in enumerate(self._rows):
            for gx, ch in enumerate(row):
                tile = self._tileset[ch]
                result = result.paste(tile, gx * tw, gy * th)
        return result

    def __repr__(self) -> str:
        cols, rows = self.grid_size
        pw, ph = self.pixel_size
        return f"TileMap({cols}x{rows} tiles, {pw}x{ph}px)"
