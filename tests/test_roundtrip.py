"""End-to-end roundtrip tests: string → Sprite → PNG → load → analyze → string."""

import tempfile
from pathlib import Path

import pytest
import pixeldot as px


@pytest.fixture
def palette():
    return px.Palette({
        '.': px.TRANSPARENT,
        'K': px.BLACK,
        'W': px.WHITE,
        'r': '#FF0000',
        'g': '#00FF00',
        'b': '#0000FF',
    })


@pytest.fixture
def sample_rows():
    return [
        "..KK..",
        ".KrrK.",
        "KrrrrK",
        "KggggK",
        ".KbbK.",
        "..KK..",
    ]


class TestFullRoundtrip:
    def test_string_to_png_to_string(self, palette, sample_rows):
        """Complete roundtrip: string → Sprite → PNG → load → string."""
        canvas = px.StringCanvas(palette)
        sprite = canvas.render(sample_rows)

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.png"
            px.save(sprite, path)

            loaded = px.load(path)
            assert sprite == loaded

            result_rows = px.StringCanvas.to_string(loaded, palette)
            assert result_rows == sample_rows

    def test_save_and_load_preview(self, palette, sample_rows):
        """Verify preview save works."""
        canvas = px.StringCanvas(palette)
        sprite = canvas.render(sample_rows)

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "preview.png"
            px.save_preview(sprite, path, scale=4)

            loaded = px.load(path)
            assert loaded.width == sprite.width * 4
            assert loaded.height == sprite.height * 4


class TestAnalysisRoundtrip:
    def test_palette_extraction(self, palette, sample_rows):
        canvas = px.StringCanvas(palette)
        sprite = canvas.render(sample_rows)

        colors = px.extract_palette(sprite, top_n=10)
        assert len(colors) > 0

        # Black should be the most used (border)
        assert colors[0].color == px.BLACK

        # Verify all expected colors are present
        found_hex = {c.hex for c in colors}
        assert "#000000" in found_hex
        assert "#FF0000" in found_hex

    def test_color_count(self, palette, sample_rows):
        canvas = px.StringCanvas(palette)
        sprite = canvas.render(sample_rows)
        assert px.color_count(sprite) == 4  # K, r, g, b

    def test_pixel_hash_consistency(self, palette, sample_rows):
        canvas = px.StringCanvas(palette)
        s1 = canvas.render(sample_rows)
        s2 = canvas.render(sample_rows)
        assert px.pixel_hash(s1) == px.pixel_hash(s2)

    def test_pixel_hash_differs(self, palette, sample_rows):
        canvas = px.StringCanvas(palette)
        s1 = canvas.render(sample_rows)
        s2 = canvas.render(["KK", "rr"])
        assert px.pixel_hash(s1) != px.pixel_hash(s2)


class TestSheetRoundtrip:
    def test_strip_pack_unpack(self, palette):
        canvas = px.StringCanvas(palette)
        f1 = canvas.render(["Kr", "rK"])
        f2 = canvas.render(["rK", "Kr"])

        strip = px.StripSheet([f1, f2])
        packed = strip.to_sprite()
        assert packed.size == (4, 2)

        unpacked = px.StripSheet.from_sprite(packed, frame_width=2)
        assert unpacked.frame_count == 2
        assert unpacked.frames[0] == f1
        assert unpacked.frames[1] == f2

    def test_grid_pack(self, palette):
        canvas = px.StringCanvas(palette)
        sprites = {
            "a": canvas.render(["KK", "KK"]),
            "b": canvas.render(["rr", "rr"]),
            "c": canvas.render(["gg", "gg"]),
        }
        grid = px.GridSheet(sprites, columns=2)
        packed = grid.to_sprite()
        assert packed.width == 4  # 2 columns * 2px
        assert packed.height == 4  # 2 rows * 2px

        meta = grid.get_metadata()
        assert len(meta) == 3
        assert meta[0]["name"] == "a"
        assert meta[0]["x"] == 0


class TestRegionRoundtrip:
    def test_compose_decompose(self, palette):
        canvas = px.StringCanvas(palette)
        layout = px.RegionLayout(
            canvas_size=(4, 4),
            regions=[
                px.Region("top", 0, 0, 4, 2),
                px.Region("bottom", 0, 2, 4, 2),
            ],
        )
        top = canvas.render(["KKKK", "rrrr"])
        bottom = canvas.render(["gggg", "bbbb"])

        composed = layout.compose({"top": top, "bottom": bottom})
        assert composed.size == (4, 4)
        assert composed.get_pixel(0, 0) == px.BLACK
        assert composed.get_pixel(0, 2) == (0, 255, 0, 255)

        parts = layout.decompose(composed)
        assert parts["top"] == top
        assert parts["bottom"] == bottom
