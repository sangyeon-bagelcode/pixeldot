"""Layer system with blend modes for compositing multiple sprites."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from .color import TRANSPARENT, Color
from .sprite import Sprite


class BlendMode(Enum):
    NORMAL = "normal"
    MULTIPLY = "multiply"
    SCREEN = "screen"
    OVERLAY = "overlay"
    ADD = "add"
    SUBTRACT = "subtract"


@dataclass
class Layer:
    name: str
    sprite: Sprite
    opacity: float = 1.0
    visible: bool = True
    blend_mode: BlendMode = BlendMode.NORMAL


def _blend_pixel(src: Color, dst: Color, mode: BlendMode, opacity: float) -> Color:
    """Blend a single source pixel onto a destination pixel."""
    sa = (src[3] / 255.0) * opacity
    if sa == 0.0:
        return dst

    da = dst[3] / 255.0

    if mode == BlendMode.NORMAL:
        out_a = sa + da * (1 - sa)
        if out_a == 0:
            return TRANSPARENT
        return (
            int((src[0] * sa + dst[0] * da * (1 - sa)) / out_a),
            int((src[1] * sa + dst[1] * da * (1 - sa)) / out_a),
            int((src[2] * sa + dst[2] * da * (1 - sa)) / out_a),
            int(out_a * 255),
        )

    # For non-normal blend modes, compute blended RGB in 0.0-1.0 range
    sr, sg, sb = src[0] / 255.0, src[1] / 255.0, src[2] / 255.0
    dr, dg, db = dst[0] / 255.0, dst[1] / 255.0, dst[2] / 255.0

    if mode == BlendMode.MULTIPLY:
        br, bg, bb = sr * dr, sg * dg, sb * db
    elif mode == BlendMode.SCREEN:
        br = 1 - (1 - sr) * (1 - dr)
        bg = 1 - (1 - sg) * (1 - dg)
        bb = 1 - (1 - sb) * (1 - db)
    elif mode == BlendMode.OVERLAY:
        br = 2 * sr * dr if dr < 0.5 else 1 - 2 * (1 - sr) * (1 - dr)
        bg = 2 * sg * dg if dg < 0.5 else 1 - 2 * (1 - sg) * (1 - dg)
        bb = 2 * sb * db if db < 0.5 else 1 - 2 * (1 - sb) * (1 - db)
    elif mode == BlendMode.ADD:
        br = min(sr + dr, 1.0)
        bg = min(sg + dg, 1.0)
        bb = min(sb + db, 1.0)
    elif mode == BlendMode.SUBTRACT:
        br = max(dr - sr, 0.0)
        bg = max(dg - sg, 0.0)
        bb = max(db - sb, 0.0)
    else:
        raise ValueError(f"Unknown blend mode: {mode}")

    # Composite blended color with source alpha onto destination
    out_a = sa + da * (1 - sa)
    if out_a == 0:
        return TRANSPARENT
    # The blended result replaces the src color in the standard alpha composite formula
    return (
        int((br * sa + dr * da * (1 - sa)) / out_a * 255),
        int((bg * sa + dg * da * (1 - sa)) / out_a * 255),
        int((bb * sa + db * da * (1 - sa)) / out_a * 255),
        int(out_a * 255),
    )


class LayerStack:
    """Manages an ordered collection of layers for compositing."""

    def __init__(self, width: int, height: int) -> None:
        self._width = width
        self._height = height
        self._layers: List[Layer] = []

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    def add_layer(
        self,
        name: str,
        sprite: Sprite,
        opacity: float = 1.0,
        blend_mode: BlendMode = BlendMode.NORMAL,
        position: Optional[int] = None,
    ) -> None:
        """Add a layer. position=None means top. Raises ValueError if name exists."""
        for layer in self._layers:
            if layer.name == name:
                raise ValueError(f"Layer {name!r} already exists")
        if sprite.width != self._width or sprite.height != self._height:
            raise ValueError(
                f"Sprite size {sprite.size} doesn't match stack size "
                f"({self._width}, {self._height})"
            )
        layer = Layer(name=name, sprite=sprite, opacity=opacity, blend_mode=blend_mode)
        if position is None:
            self._layers.append(layer)
        else:
            self._layers.insert(position, layer)

    def remove_layer(self, name: str) -> Layer:
        """Remove and return a layer by name."""
        for i, layer in enumerate(self._layers):
            if layer.name == name:
                return self._layers.pop(i)
        raise KeyError(f"Layer {name!r} not found")

    def get_layer(self, name: str) -> Layer:
        """Get a layer by name."""
        for layer in self._layers:
            if layer.name == name:
                return layer
        raise KeyError(f"Layer {name!r} not found")

    def reorder(self, names: List[str]) -> None:
        """Set layer order (bottom to top). Must include all layer names."""
        if set(names) != {layer.name for layer in self._layers}:
            raise ValueError("names must contain exactly all layer names")
        by_name = {layer.name: layer for layer in self._layers}
        self._layers = [by_name[n] for n in names]

    def set_visibility(self, name: str, visible: bool) -> None:
        self.get_layer(name).visible = visible

    def set_opacity(self, name: str, opacity: float) -> None:
        self.get_layer(name).opacity = opacity

    def set_blend_mode(self, name: str, mode: BlendMode) -> None:
        self.get_layer(name).blend_mode = mode

    @property
    def layer_names(self) -> List[str]:
        """Layer names from bottom to top."""
        return [layer.name for layer in self._layers]

    def flatten(self) -> Sprite:
        """Composite all visible layers into a single Sprite."""
        pixels: list[list[Color]] = [
            [TRANSPARENT] * self._width for _ in range(self._height)
        ]

        for layer in self._layers:
            if not layer.visible:
                continue
            for y in range(self._height):
                for x in range(self._width):
                    src = layer.sprite.get_pixel(x, y)
                    if src[3] == 0:
                        continue
                    pixels[y][x] = _blend_pixel(
                        src, pixels[y][x], layer.blend_mode, layer.opacity
                    )

        return Sprite(pixels, _skip_copy=True)
