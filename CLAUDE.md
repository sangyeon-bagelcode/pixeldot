# pixeldot

Token-efficient pixel art toolkit. **1 character = 1 pixel.**

When creating pixel art, always `import pixeldot as px` and use `StringCanvas.render_block()` instead of raw RGBA tuples.

Use the `/pixel-art` command to activate the pixel art creation agent.

Quick start:
```python
import pixeldot as px
p = px.Palette({'.': px.TRANSPARENT, 'K': px.BLACK, 'r': '#FF0000'})
sprite = px.StringCanvas(p).render_block('''
    ..KK..
    .KrrK.
    KrrrrK
''')
px.save(sprite, "out.png")
px.save_preview(sprite, "out_10x.png")
```

## Choosing the right tool

| Situation | Tool | Token cost |
|-----------|------|------------|
| Small sprite (≤48x48) | `StringCanvas` | ~263 tok/32x32 |
| Many colors (62+) | `MultiCharPalette` | ~519 tok/32x32 |
| Large map/scene | `TileMap` | ~263 tok/256x256 |
| Complex compositing | `LayerStack` | per-layer cost |
| Performance-critical | `FastSprite` | same (NumPy backend) |
| Existing PNG editing | `AutoPalette.from_image()` | auto |

## Style presets

```python
palette = px.get_preset_palette("pico8")  # gameboy, nes, pico8, sweetie16, endesga32
```

## Color utilities

```python
shades = px.auto_shades(base_color, count=5)     # highlight → shadow
ramp = px.color_ramp(color_a, color_b, steps=8)  # gradient
lighter = px.lighten(color, 0.2)                  # HSL manipulation
```

## Effects

```python
outlined = px.apply_outline(sprite, px.BLACK, px.OutlineStyle.THIN)
shadowed = px.apply_shadow(sprite, offset=(1,1), opacity=0.5)
```
