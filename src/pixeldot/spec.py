"""Batch spec system: render multiple sprites from a single YAML file.

Usage::

    from pixeldot.spec import render_spec, load_spec

    # One-shot: parse, render, save
    results = render_spec("spec.yaml")

    # Step-by-step
    spec = load_spec("spec.yaml")
    results = spec.render()
    spec.save_all(results)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

import yaml

from .canvas import StringCanvas
from .color import BLACK, TRANSPARENT, WHITE, Color, Palette, hex_to_color
from .io import save, save_preview
from .layers import BlendMode, LayerStack
from .sheet import GridSheet, StripSheet
from .sprite import Sprite
from .style import OutlineStyle, apply_outline, apply_shadow, get_preset_palette
from .tiles import TileMap, TileSet


class SpecError(Exception):
    """Error in spec file parsing or rendering."""


# Reserved color names
_RESERVED_COLORS: Dict[str, Color] = {
    "transparent": TRANSPARENT,
    "black": BLACK,
    "white": WHITE,
}


def _resolve_color(value: Any) -> Union[Color, str]:
    """Resolve a color value from YAML."""
    if isinstance(value, str):
        lower = value.lower()
        if lower in _RESERVED_COLORS:
            return _RESERVED_COLORS[lower]
        return value  # hex string — Palette constructor handles conversion
    raise SpecError(f"Invalid color value: {value!r}")


def _build_palette(palette_data: Dict[str, Any]) -> Palette:
    """Build a Palette from spec palette section."""
    mapping: Dict[str, Union[Color, str]] = {}
    for key, value in palette_data.items():
        if len(key) != 1:
            raise SpecError(f"Palette key must be 1 character, got {key!r}")
        mapping[key] = _resolve_color(value)
    return Palette(mapping)


class Spec:
    """Parsed batch spec. Call render() to produce sprites, save_all() to write files."""

    def __init__(
        self,
        palette: Palette,
        sprite_defs: Dict[str, Dict[str, Any]],
        base_dir: Path,
    ) -> None:
        self.palette = palette
        self.sprite_defs = sprite_defs
        self.base_dir = base_dir

    def render(self, only: Optional[Set[str]] = None) -> Dict[str, Sprite]:
        """Render all (or selected) sprites. Returns name -> Sprite mapping."""
        results: Dict[str, Sprite] = {}
        for name in self.sprite_defs:
            if only and name not in only:
                continue
            self._ensure_rendered(name, results)
        return results

    def _ensure_rendered(self, name: str, results: Dict[str, Sprite]) -> Sprite:
        """Render a sprite if not already rendered, resolving dependencies."""
        if name in results:
            return results[name]

        if name not in self.sprite_defs:
            raise SpecError(f"Sprite {name!r} not defined in spec")

        defn = self.sprite_defs[name]
        sprite_type = defn.get("type", "block")

        if sprite_type == "block":
            sprite = self._render_block(defn)
        elif sprite_type == "strip":
            sprite = self._render_strip(name, defn, results)
        elif sprite_type == "grid":
            sprite = self._render_grid(name, defn, results)
        elif sprite_type == "tilemap":
            sprite = self._render_tilemap(name, defn, results)
        elif sprite_type == "layers":
            sprite = self._render_layers(name, defn, results)
        else:
            raise SpecError(f"Unknown sprite type {sprite_type!r} in {name!r}")

        sprite = self._apply_effects(sprite, defn)
        results[name] = sprite
        return sprite

    def _render_block(self, defn: Dict[str, Any]) -> Sprite:
        block = defn.get("block")
        if not block:
            raise SpecError("Block sprite missing 'block' field")
        return StringCanvas(self.palette).render_block(block)

    def _render_strip(
        self, name: str, defn: Dict[str, Any], results: Dict[str, Sprite]
    ) -> Sprite:
        frame_names = defn.get("frames")
        if not frame_names:
            raise SpecError(f"Strip {name!r} missing 'frames' field")
        frames = [self._ensure_rendered(fn, results) for fn in frame_names]
        return StripSheet(frames).to_sprite()

    def _render_grid(
        self, name: str, defn: Dict[str, Any], results: Dict[str, Sprite]
    ) -> Sprite:
        sprite_refs = defn.get("sprites")
        if not sprite_refs:
            raise SpecError(f"Grid {name!r} missing 'sprites' field")
        columns = defn.get("columns", 4)
        padding = defn.get("padding", 0)
        sprites: Dict[str, Sprite] = {}
        for sname, ref in sprite_refs.items():
            sprites[sname] = self._ensure_rendered(ref, results)
        return GridSheet(sprites, columns=columns, padding=padding).to_sprite()

    def _render_tilemap(
        self, name: str, defn: Dict[str, Any], results: Dict[str, Sprite]
    ) -> Sprite:
        tileset_refs = defn.get("tileset")
        grid = defn.get("grid")
        if not tileset_refs:
            raise SpecError(f"TileMap {name!r} missing 'tileset' field")
        if not grid:
            raise SpecError(f"TileMap {name!r} missing 'grid' field")
        tiles: Dict[str, Sprite] = {}
        for key, ref in tileset_refs.items():
            tiles[key] = self._ensure_rendered(ref, results)
        tileset = TileSet(tiles)
        return TileMap(tileset, grid).to_sprite()

    def _render_layers(
        self, name: str, defn: Dict[str, Any], results: Dict[str, Sprite]
    ) -> Sprite:
        layer_defs = defn.get("layers")
        if not layer_defs:
            raise SpecError(f"Layers {name!r} missing 'layers' field")

        width = defn.get("width")
        height = defn.get("height")

        # Resolve first layer to determine size if not specified
        first_entry = layer_defs[0]
        first_ref = first_entry["sprite"] if isinstance(first_entry, dict) else first_entry
        first_sprite = self._ensure_rendered(first_ref, results)
        if width is None:
            width = first_sprite.width
        if height is None:
            height = first_sprite.height

        stack = LayerStack(width, height)
        for layer_def in layer_defs:
            if isinstance(layer_def, str):
                sprite = self._ensure_rendered(layer_def, results)
                stack.add_layer(layer_def, sprite)
            else:
                ref = layer_def["sprite"]
                sprite = self._ensure_rendered(ref, results)
                lname = layer_def.get("name", ref)
                opacity = layer_def.get("opacity", 1.0)
                blend_str = layer_def.get("blend_mode", "normal")
                blend_mode = BlendMode(blend_str)
                stack.add_layer(lname, sprite, opacity=opacity, blend_mode=blend_mode)

        return stack.flatten()

    def _apply_effects(self, sprite: Sprite, defn: Dict[str, Any]) -> Sprite:
        if "outline" in defn:
            outline_cfg = defn["outline"]
            if isinstance(outline_cfg, bool) and outline_cfg:
                sprite = apply_outline(sprite, BLACK, OutlineStyle.THIN)
            elif isinstance(outline_cfg, dict):
                color = BLACK
                if "color" in outline_cfg:
                    c = outline_cfg["color"]
                    if isinstance(c, str):
                        color = _RESERVED_COLORS.get(c.lower(), hex_to_color(c))
                    else:
                        color = c
                style_str = outline_cfg.get("style", "thin").upper()
                style = OutlineStyle[style_str]
                sprite = apply_outline(sprite, color, style)

        if "shadow" in defn:
            shadow_cfg = defn["shadow"]
            if isinstance(shadow_cfg, bool) and shadow_cfg:
                sprite = apply_shadow(sprite, offset=(1, 1), opacity=0.5)
            elif isinstance(shadow_cfg, dict):
                offset_list = shadow_cfg.get("offset", [1, 1])
                offset = (offset_list[0], offset_list[1])
                opacity = shadow_cfg.get("opacity", 0.5)
                sprite = apply_shadow(sprite, offset=offset, opacity=opacity)

        return sprite

    def save_all(self, results: Dict[str, Sprite]) -> List[str]:
        """Save all sprites with 'save' or 'preview' paths. Returns saved file paths."""
        saved: List[str] = []
        for name, sprite in results.items():
            defn = self.sprite_defs.get(name, {})
            if "save" in defn:
                path = self.base_dir / defn["save"]
                save(sprite, path)
                saved.append(str(path))
            if "preview" in defn:
                path = self.base_dir / defn["preview"]
                save_preview(sprite, path)
                saved.append(str(path))
        return saved


def load_spec(path: Union[str, Path]) -> Spec:
    """Load and parse a YAML spec file."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Spec file not found: {path}")

    with open(path) as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise SpecError("Spec file must be a YAML mapping")

    # Palette
    palette_data = data.get("palette")
    preset = data.get("preset")

    if palette_data:
        palette = _build_palette(palette_data)
    elif preset:
        palette = get_preset_palette(preset)
    else:
        raise SpecError("Spec must have a 'palette' or 'preset' section")

    # Sprites
    sprite_defs = data.get("sprites")
    if not sprite_defs:
        raise SpecError("Spec must have a 'sprites' section")

    return Spec(palette=palette, sprite_defs=sprite_defs, base_dir=path.parent)


def render_spec(
    path: Union[str, Path],
    *,
    only: Optional[Set[str]] = None,
    dry_run: bool = False,
) -> Dict[str, Sprite]:
    """Load, render, and optionally save all sprites from a YAML spec file."""
    spec = load_spec(path)
    results = spec.render(only=only)
    if not dry_run:
        spec.save_all(results)
    return results
