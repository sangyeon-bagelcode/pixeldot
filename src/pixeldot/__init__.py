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

# io.py
from .io import load, save, save_preview

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
    # preview
    "scale_nearest", "preview_image", "side_by_side",
    # analysis
    "ColorInfo", "extract_palette", "color_count", "opaque_bounds", "pixel_hash",
    # io
    "load", "save", "save_preview",
]
