"""Tests for StringCanvas — the core renderer."""

import pytest
import pixeldot as px


@pytest.fixture
def basic_palette():
    return px.Palette({
        '.': px.TRANSPARENT,
        'K': px.BLACK,
        'W': px.WHITE,
        'r': '#FF0000',
    })


@pytest.fixture
def canvas(basic_palette):
    return px.StringCanvas(basic_palette)


class TestRender:
    def test_simple_render(self, canvas):
        sprite = canvas.render([
            "KKK",
            "KrK",
            "KKK",
        ])
        assert sprite.size == (3, 3)
        assert sprite.get_pixel(0, 0) == px.BLACK
        assert sprite.get_pixel(1, 1) == (255, 0, 0, 255)

    def test_transparent_pixels(self, canvas):
        sprite = canvas.render([".K.", "K.K", ".K."])
        assert sprite.get_pixel(0, 0) == px.TRANSPARENT
        assert sprite.get_pixel(1, 0) == px.BLACK

    def test_single_pixel(self, canvas):
        sprite = canvas.render(["r"])
        assert sprite.size == (1, 1)
        assert sprite.get_pixel(0, 0) == (255, 0, 0, 255)

    def test_inconsistent_row_length_raises(self, canvas):
        with pytest.raises(ValueError, match="chars"):
            canvas.render(["KK", "KKK"])

    def test_unknown_character_raises(self, canvas):
        with pytest.raises(KeyError, match="not in palette"):
            canvas.render(["KxK"])

    def test_empty_rows_raises(self, canvas):
        with pytest.raises(ValueError):
            canvas.render([])


class TestRenderBlock:
    def test_dedent(self, canvas):
        sprite = canvas.render_block("""
            KK
            rr
        """)
        assert sprite.size == (2, 2)
        assert sprite.get_pixel(0, 0) == px.BLACK
        assert sprite.get_pixel(0, 1) == (255, 0, 0, 255)

    def test_no_leading_trailing_blanks(self, canvas):
        sprite = canvas.render_block("""
            .K.
        """)
        assert sprite.size == (3, 1)

    def test_empty_block_raises(self, canvas):
        with pytest.raises(ValueError):
            canvas.render_block("   \n   \n   ")


class TestToString:
    def test_round_trip(self, canvas, basic_palette):
        original = ["KrK", ".W.", "K.K"]
        sprite = canvas.render(original)
        result = px.StringCanvas.to_string(sprite, basic_palette)
        assert result == original

    def test_unknown_color_raises(self, basic_palette):
        sprite = px.Sprite([[(128, 128, 128, 255)]])
        with pytest.raises(KeyError):
            px.StringCanvas.to_string(sprite, basic_palette)
