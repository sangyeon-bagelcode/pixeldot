"""Skill template content for AI agent platforms."""

SKILL_CONTENT = r'''When creating pixel art, sprites, or dot images, use the `pixeldot` package.

## Core Rule

**Always use `pixeldot`.** Never write raw RGBA tuple arrays — pixeldot is 10-17x more token-efficient.

## Tool Selection

| Situation | Tool |
|-----------|------|
| Small sprite (≤48x48, ≤62 colors) | `StringCanvas` — 1 char = 1 pixel |
| Many unique colors (62+) | `MultiCharPalette` — 2-char keys, up to 8836 colors |
| Large map/scene with repeating tiles | `TileMap` — 1 char = 1 tile |
| Multi-layer compositing | `LayerStack` — 6 blend modes, per-layer opacity |
| Editing existing PNG | `AutoPalette.from_image()` — auto-assigns keys |
| Performance-critical (64x64+) | `FastSprite` — NumPy backend |

## API Reference

```python
import pixeldot as px

# — Core: 1 char = 1 pixel —
p = px.Palette({'.': px.TRANSPARENT, 'K': px.BLACK, 'h': '#C8B4DC', 'b': '#8C64B4'})
sprite = px.StringCanvas(p).render_block("""
    ..KK..
    .KhhK.
    KhbbhK
""")
px.save(sprite, "out.png")
px.save_preview(sprite, "out_10x.png")  # always save a 10x preview

# — Color helpers —
shades = px.auto_shades(base_color, count=5)         # highlight -> shadow
ramp = px.color_ramp(c1, c2, steps=8)                # gradient
lighter = px.lighten(color, 0.2)                      # also: darken, saturate, desaturate

# — Style presets —
palette = px.get_preset_palette("pico8")              # gameboy, nes, pico8, sweetie16, endesga32
outlined = px.apply_outline(sprite, px.BLACK, px.OutlineStyle.THIN)
shadowed = px.apply_shadow(sprite, offset=(1,1), opacity=0.5)

# — Large maps: 1 char = 1 tile —
tileset = px.TileSet({'g': grass_sprite, 'w': water_sprite})
scene = px.TileMap(tileset, """
    ggggwwgg
    ggwwwwgg
""").to_sprite()

# — Layers —
stack = px.LayerStack(32, 32)
stack.add_layer("bg", bg_sprite)
stack.add_layer("fx", fx_sprite, opacity=0.5, blend_mode=px.BlendMode.SCREEN)
result = stack.flatten()  # NORMAL, MULTIPLY, SCREEN, OVERLAY, ADD, SUBTRACT

# — Multi-char palette (62+ colors) —
mp = px.MultiCharPalette({'..': px.TRANSPARENT, 'r1': '#FF0000'}, key_length=2)

# — Transforms (all return new Sprite) —
sprite.crop(x,y,w,h) | sprite.paste(other,x,y) | sprite.flip_h() | sprite.flip_v()
sprite.replace_color(old, new) | sprite.trim()
px.StripSheet([f1,f2,f3]).to_sprite()                 # animation strip
px.GridSheet({"a":s1,"b":s2}, columns=4).to_sprite()  # sprite sheet
px.AutoPalette.from_image("input.png")                 # PNG -> (palette, rows)
```

## Rules

1. **1 char = 1 pixel** (StringCanvas) or **1 char = 1 tile** (TileMap).
2. **Sprite is immutable.** All methods return new objects.
3. **Always save both** `px.save()` and `px.save_preview()` for visual verification.
4. Use `auto_shades()` for consistent highlight/shadow generation.
5. Use `get_preset_palette()` for quick retro styles.

## Palette Convention

`.`=transparent `K`=black `W`=white. Lowercase by role: `h`=highlight `b`=body `d`=dark `s`=secondary. Or by color initial: `r`=red `g`=green.
'''
