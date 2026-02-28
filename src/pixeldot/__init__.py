"""pixeldot — Token-efficient pixel art toolkit for AI agents.

Represent 32x32 sprites in ~300 tokens instead of ~5000.

Usage::

    import pixeldot as px

    p = px.Palette({
        '.': px.TRANSPARENT,
        'K': px.BLACK,
        'r': '#FF0000',
    })
    sprite = px.StringCanvas(p).render_block('''
        ..KK..
        .KrrK.
        KrrrrK
    ''')
    px.save(sprite, "gem.png")
    px.save_preview(sprite, "gem_10x.png")
"""

from ._version import __version__

# color.py
from .color import (
    Color,
    Palette,
    TRANSPARENT,
    BLACK,
    WHITE,
    rgba,
    hex_to_color,
    color_to_hex,
)

# sprite.py
from .sprite import Sprite

# canvas.py
from .canvas import StringCanvas

# sheet.py
from .sheet import StripSheet, GridSheet

# region.py
from .region import Region, RegionLayout

# preview.py
from .preview import scale_nearest, preview_image, side_by_side

# analysis.py
from .analysis import ColorInfo, extract_palette, color_count, opaque_bounds, pixel_hash

# color_utils.py
from .color_utils import (
    rgb_to_hsl,
    hsl_to_rgb,
    lighten,
    darken,
    saturate,
    desaturate,
    color_lerp,
    color_ramp,
    auto_shades,
    dither_pattern,
    color_distance,
)

# style.py
from .style import (
    GAMEBOY_PALETTE,
    NES_PALETTE,
    PICO8_PALETTE,
    SWEETIE16_PALETTE,
    ENDESGA32_PALETTE,
    get_preset_palette,
    list_preset_palettes,
    OutlineStyle,
    apply_outline,
    apply_shadow,
)

# tiles.py
from .tiles import TileSet, TileMap

# layers.py
from .layers import BlendMode, Layer, LayerStack

# extended_palette.py
from .extended_palette import MultiCharPalette, AutoPalette

# io.py
from .io import load, save, save_preview

# fast_sprite.py (optional — requires numpy)
try:
    from .fast_sprite import FastSprite
except ImportError:
    pass

__all__ = [
    "__version__",
    # color
    "Color", "Palette", "TRANSPARENT", "BLACK", "WHITE",
    "rgba", "hex_to_color", "color_to_hex",
    # sprite
    "Sprite",
    # canvas
    "StringCanvas",
    # sheet
    "StripSheet", "GridSheet",
    # region
    "Region", "RegionLayout",
    # tiles
    "TileSet", "TileMap",
    # preview
    "scale_nearest", "preview_image", "side_by_side",
    # analysis
    "ColorInfo", "extract_palette", "color_count", "opaque_bounds", "pixel_hash",
    # color_utils
    "rgb_to_hsl", "hsl_to_rgb", "lighten", "darken", "saturate", "desaturate",
    "color_lerp", "color_ramp", "auto_shades", "dither_pattern", "color_distance",
    # style
    "GAMEBOY_PALETTE", "NES_PALETTE", "PICO8_PALETTE", "SWEETIE16_PALETTE",
    "ENDESGA32_PALETTE", "get_preset_palette", "list_preset_palettes",
    "OutlineStyle", "apply_outline", "apply_shadow",
    # layers
    "BlendMode", "Layer", "LayerStack",
    # extended_palette
    "MultiCharPalette", "AutoPalette",
    # io
    "load", "save", "save_preview",
    # fast (optional)
    "FastSprite",
]
