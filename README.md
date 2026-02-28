# pixeldot

**Token-efficient pixel art toolkit for AI agents.**

AI agents waste thousands of tokens writing RGBA tuple arrays for pixel art. pixeldot fixes this with a **1-character-per-pixel string format** that's 10-15x more compact.

```
# Before: ~5000 tokens for a 32x32 sprite
pixels = [[(0,0,0,0), (0,0,0,0), (0,0,0,255), (200,180,220,255), ...], ...]  # 32 rows × 32 cols

# After: ~300 tokens for the same sprite
sprite = px.StringCanvas(palette).render_block('''
    ..KhbK..
    .KhhbbK.
    KhhhhbbK
''')
```

---

## Install

```bash
pip install pixeldot
```

Or from source:

```bash
git clone https://github.com/WonsangYeon/pixeldot.git
cd pixeldot
pip install -e .
```

## Quick Start

```python
import pixeldot as px

# Define palette: 1 character = 1 color
palette = px.Palette({
    '.': px.TRANSPARENT,
    'K': px.BLACK,
    'h': '#C8B4DC',       # highlight
    'b': '#8C64B4',       # body
    'd': '#5A3C78',       # dark/shadow
})

# Draw with strings — each character is one pixel
canvas = px.StringCanvas(palette)
sprite = canvas.render_block('''
    ....KK....
    ...KhbK...
    ..KhhbbK..
    .KhhhbbbK.
    KhhhhbbbbK
    KddddbbbbK
    .KdddbbbK.
    ..KdddbK..
    ...KKKK...
''')

# Save
px.save(sprite, "shield.png")
px.save_preview(sprite, "shield_10x.png")  # 10x upscale for viewing
```

---

## Agent Integration (Claude Code)

pixeldot includes built-in [Claude Code](https://docs.anthropic.com/en/docs/claude-code) support. After setup, your agent automatically knows how to use pixeldot when you ask it to create pixel art.

### Setup (one-time, per project)

**Step 1.** Install pixeldot in your project:

```bash
pip install pixeldot
```

**Step 2.** Find where pixeldot is installed:

```bash
python -c "import pixeldot, pathlib; print(pathlib.Path(pixeldot.__file__).parent.parent.parent)"
```

**Step 3.** Copy the skill file into your project:

```bash
# From the pixeldot repo (or installed location)
mkdir -p .claude/commands
cp <pixeldot-path>/.claude/commands/pixel-art.md .claude/commands/pixel-art.md
```

Or create `.claude/commands/pixel-art.md` manually with this content:

<details>
<summary>Click to expand pixel-art.md</summary>

```markdown
You are a pixel art creation agent using the `pixeldot` Python package.

## Core Rule

**Always use `pixeldot` for pixel art.** Never write raw RGBA tuple arrays.

## Quick Reference

import pixeldot as px
palette = px.Palette({'.': px.TRANSPARENT, 'K': px.BLACK, 'r': '#FF0000'})
sprite = px.StringCanvas(palette).render_block('''..KK..\n.KrrK.\nKrrrrK''')
px.save(sprite, "out.png")
px.save_preview(sprite, "out_10x.png")

## Palette Convention

- `.` = transparent, `K` = black/outline, `W` = white
- Lowercase for roles: `h`=highlight, `b`=body, `d`=dark, `s`=secondary

## Key APIs

- `px.StringCanvas(palette).render_block('''...''')` — string to sprite
- `px.save(sprite, path)` / `px.save_preview(sprite, path, scale=10)`
- `px.load(path)` — load existing PNG
- `sprite.replace_color(old, new)` — recolor
- `sprite.crop/paste/flip_h/flip_v/trim` — transforms (all return new sprite)
- `px.StripSheet([f1, f2, f3])` — animation strip
- `px.GridSheet({"a": s1, "b": s2}, columns=4)` — sprite collection
- `px.extract_palette(sprite)` — analyze colors in existing sprite
```

</details>

**Step 4.** (Optional) Add to your project's `CLAUDE.md`:

```markdown
## Pixel Art

Use `pixeldot` for all pixel art creation. Run `/pixel-art` for the full guide.
```

### How it works

Once set up:

1. Ask your agent: *"Make a 16x16 sword sprite"*
2. The agent uses `/pixel-art` skill automatically
3. It creates the sprite using pixeldot's string format (~300 tokens instead of ~5000)
4. Saves both the PNG and a 10x preview for visual verification

### Without Claude Code

pixeldot works with any AI agent. Add the content of `CLAUDE.md` or `.claude/commands/pixel-art.md` to your agent's system prompt or context.

---

## Features

### StringCanvas — Core Token Saver

```python
palette = px.Palette({'.': px.TRANSPARENT, 'K': px.BLACK, 'r': '#FF0000'})
canvas = px.StringCanvas(palette)

# render from list of strings
sprite = canvas.render(["KrK", ".K.", "KrK"])

# render from triple-quoted block (auto-dedent)
sprite = canvas.render_block('''
    KrK
    .K.
    KrK
''')

# reverse: sprite back to strings (for editing existing PNGs)
rows = px.StringCanvas.to_string(sprite, palette)
```

### Sprite — Immutable Pixel Container

```python
sprite = px.Sprite.empty(32, 32)           # transparent canvas
sprite = px.load("input.png")              # from file
sprite = px.Sprite.from_image(pil_image)   # from PIL

# All transforms return new sprites (original unchanged)
cropped = sprite.crop(x, y, w, h)
combined = base.paste(overlay, x, y)       # alpha compositing
flipped = sprite.flip_h()                  # or flip_v()
recolored = sprite.replace_color(old_color, new_color)
trimmed = sprite.trim()                    # remove transparent border
bounds = sprite.opaque_bounds()            # → (x, y, w, h) or None
```

### Animation Strips

```python
frames = [canvas.render_block(f) for f in [idle, walk1, walk2]]
strip = px.StripSheet(frames)
px.save(strip.to_sprite(), "walk_strip.png")

# Load strip back
strip = px.StripSheet.from_sprite(px.load("walk_strip.png"), frame_width=32)
```

### Collection Grids

```python
grid = px.GridSheet(
    {"sword": sword, "axe": axe, "bow": bow},
    columns=3,
    padding=1,
)
px.save(grid.to_sprite(), "weapons.png")
meta = grid.get_metadata()  # [{"name": "sword", "x": 0, "y": 0, "w": 32, "h": 32}, ...]
```

### Multi-Part Layout

```python
layout = px.RegionLayout(
    canvas_size=(32, 32),
    regions=[
        px.Region("blade", 8, 0, 16, 24),
        px.Region("hilt", 12, 22, 8, 10),
    ],
)
weapon = layout.compose({"blade": blade_sprite, "hilt": hilt_sprite})
parts = layout.decompose(weapon)  # split back into named parts
```

### Analysis

```python
colors = px.extract_palette(sprite, top_n=12)
# [ColorInfo(color=(0,0,0,255), hex='#000000', count=120, percentage=45.2), ...]

count = px.color_count(sprite)        # unique non-transparent colors
bounds = px.opaque_bounds(sprite)     # (x, y, w, h) or None
hash_val = px.pixel_hash(sprite)      # SHA-256 for dedup
```

### Preview

```python
px.save_preview(sprite, "big.png", scale=10)                    # 10x nearest-neighbor
img = px.preview_image(sprite, scale=10, background=px.WHITE)   # PIL Image with bg
img = px.side_by_side([v1, v2, v3], scale=10, gap=2)            # comparison view
```

---

## API Reference

### Color & Palette

| API | Description |
|-----|-------------|
| `px.TRANSPARENT` | `(0, 0, 0, 0)` |
| `px.BLACK` | `(0, 0, 0, 255)` |
| `px.WHITE` | `(255, 255, 255, 255)` |
| `px.rgba(r, g, b, a=255)` | Create RGBA tuple |
| `px.hex_to_color("#FF8800")` | Hex string to Color |
| `px.color_to_hex(color)` | Color to hex string |
| `px.Palette({"K": px.BLACK, ...})` | Character-to-color mapping |
| `palette.with_updates(x="#00FF00")` | New palette with overrides |

### Rendering

| API | Description |
|-----|-------------|
| `px.StringCanvas(palette)` | Create renderer |
| `canvas.render(["KK", "rr"])` | Render row list |
| `canvas.render_block('''...''')` | Render triple-quoted block |
| `StringCanvas.to_string(sprite, palette)` | Sprite to string rows |

### Sprite

| API | Description |
|-----|-------------|
| `Sprite.empty(w, h)` | Transparent sprite |
| `Sprite.from_image(pil_img)` | From PIL Image |
| `sprite.to_image()` | To PIL Image |
| `sprite.size` | `(width, height)` |
| `sprite.get_pixel(x, y)` | Get color at position |
| `sprite.crop(x, y, w, h)` | Extract region |
| `sprite.paste(other, x, y)` | Alpha composite |
| `sprite.flip_h()` / `flip_v()` | Mirror |
| `sprite.replace_color(old, new)` | Swap color |
| `sprite.trim()` | Remove transparent border |
| `sprite.opaque_bounds()` | Non-transparent bbox |

### I/O

| API | Description |
|-----|-------------|
| `px.load(path)` | Load PNG as Sprite |
| `px.save(sprite, path)` | Save as PNG |
| `px.save_preview(sprite, path, scale=10)` | Save upscaled PNG |

### Analysis

| API | Description |
|-----|-------------|
| `px.extract_palette(sprite, top_n=12)` | Top colors used |
| `px.color_count(sprite)` | Unique color count |
| `px.opaque_bounds(sprite)` | Non-transparent bbox |
| `px.pixel_hash(sprite)` | SHA-256 hash |

### Sheets & Layout

| API | Description |
|-----|-------------|
| `px.StripSheet(frames)` | Animation strip |
| `px.GridSheet(sprites, columns)` | Collection grid |
| `px.RegionLayout(size, regions)` | Multi-part layout |
| `px.Region(name, x, y, w, h)` | Named region |

### Preview

| API | Description |
|-----|-------------|
| `px.scale_nearest(sprite, factor)` | Nearest-neighbor scale |
| `px.preview_image(sprite, scale, bg)` | Preview as PIL Image |
| `px.side_by_side(sprites, scale, gap)` | Comparison image |

---

## Requirements

- Python >= 3.10
- Pillow >= 9.0

## License

MIT
