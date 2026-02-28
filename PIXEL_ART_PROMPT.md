# Pixel Art with pixeldot

When asked to create pixel art, sprites, or dot images, follow these steps.

## Setup (do this ONCE, before first use)

```bash
pip install git+https://github.com/sangyeon-bagelcode/pixeldot.git
# For large image performance (NumPy backend):
# pip install "pixeldot[perf] @ git+https://github.com/sangyeon-bagelcode/pixeldot.git"
```

If the install fails, check `python -c "import pixeldot"`. If already importable, skip.

## Rules

1. **Always** `import pixeldot as px`. NEVER write raw RGBA tuple arrays — pixeldot is 10-17x more token-efficient.
2. **Always** save both the PNG and a 10x preview: `px.save(sprite, "x.png")` + `px.save_preview(sprite, "x_10x.png")`.
3. Pick the right tool for the job (see table below).

## Tool Selection

| Situation | Tool | Why |
|-----------|------|-----|
| Small sprite (≤48x48, ≤62 colors) | `StringCanvas` | 1 char = 1 pixel, ~263 tok for 32x32 |
| Many unique colors (62+) | `MultiCharPalette` | 2-char keys, up to 8836 colors |
| Large map/scene with repeating tiles | `TileMap` | 1 char = 1 tile, ~263 tok for 256x256 |
| Multi-layer compositing | `LayerStack` | 6 blend modes, per-layer opacity |
| Editing existing PNG | `AutoPalette.from_image()` | Auto-assigns char keys to colors |
| Performance-critical (64x64+) | `FastSprite` | NumPy backend, 1000x+ faster |

## API Cheat Sheet

```python
import pixeldot as px

# ── Core: 1 char = 1 pixel ──
p = px.Palette({'.': px.TRANSPARENT, 'K': px.BLACK, 'h': '#C8B4DC', 'b': '#8C64B4', 'd': '#5A3C78'})
sprite = px.StringCanvas(p).render_block('''
    ..KK..
    .KhhK.
    KhbbdK
''')
px.save(sprite, "out.png")
px.save_preview(sprite, "out_10x.png")

# ── Color helpers ──
shades = px.auto_shades(base_color, count=5)         # auto highlight → shadow
ramp = px.color_ramp(c1, c2, steps=8)                # gradient
lighter = px.lighten(color, 0.2)                      # also: darken, saturate, desaturate

# ── Style presets ──
palette = px.get_preset_palette("pico8")              # gameboy, nes, pico8, sweetie16, endesga32
outlined = px.apply_outline(sprite, px.BLACK, px.OutlineStyle.THIN)  # THIN, THICK, SELECTIVE
shadowed = px.apply_shadow(sprite, offset=(1,1), opacity=0.5)

# ── Large maps: 1 char = 1 tile ──
tileset = px.TileSet({'g': grass_sprite, 'w': water_sprite})  # all tiles same size
scene = px.TileMap(tileset, '''
    ggggwwgg
    ggwwwwgg
''').to_sprite()

# ── Layers ──
stack = px.LayerStack(32, 32)
stack.add_layer("bg", bg_sprite)
stack.add_layer("fx", fx_sprite, opacity=0.5, blend_mode=px.BlendMode.SCREEN)
result = stack.flatten()  # BlendMode: NORMAL, MULTIPLY, SCREEN, OVERLAY, ADD, SUBTRACT

# ── Multi-char palette (62+ colors) ──
mp = px.MultiCharPalette({'..': px.TRANSPARENT, 'r1': '#FF0000', 'r2': '#CC0000'}, key_length=2)
sprite = mp.render_block('''r1r1r2r2''')

# ── Transforms (all return new Sprite) ──
sprite.crop(x, y, w, h)  |  sprite.paste(other, x, y)  |  sprite.flip_h()  |  sprite.flip_v()
sprite.replace_color(old, new)  |  sprite.trim()
px.StripSheet([f1, f2, f3]).to_sprite()                # animation strip
px.GridSheet({"a": s1, "b": s2}, columns=4).to_sprite()  # sprite sheet
px.AutoPalette.from_image("input.png")                 # PNG → (palette, string_rows)
```

## Palette Naming Convention

`.`=transparent `K`=black `W`=white, then lowercase by role: `h`=highlight `b`=body `d`=dark `s`=secondary, or by color initial: `r`=red `g`=green `e`=emerald.
