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
