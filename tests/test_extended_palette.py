"""Tests for extended palette — multi-char keys and auto-palette."""

import pytest
import pixeldot as px
from pixeldot.extended_palette import MultiCharPalette, AutoPalette


class TestMultiCharPalette:
    def test_basic_render(self):
        p = MultiCharPalette({
            '..': px.TRANSPARENT,
            'KK': px.BLACK,
            'rr': (255, 0, 0, 255),
        }, key_length=2)
        sprite = p.render(["..KK", "KKrr"])
        assert sprite.size == (2, 2)
        assert sprite.get_pixel(0, 0) == px.TRANSPARENT
        assert sprite.get_pixel(1, 0) == px.BLACK
        assert sprite.get_pixel(0, 1) == px.BLACK
        assert sprite.get_pixel(1, 1) == (255, 0, 0, 255)

    def test_render_block(self):
        p = MultiCharPalette({
            '..': px.TRANSPARENT,
            'KK': px.BLACK,
        }, key_length=2)
        sprite = p.render_block('''
            ..KKKK..
            KK....KK
        ''')
        assert sprite.size == (4, 2)
        assert sprite.get_pixel(0, 0) == px.TRANSPARENT
        assert sprite.get_pixel(1, 0) == px.BLACK

    def test_hex_color_values(self):
        p = MultiCharPalette({
            'r1': '#FF0000',
            'r2': '#CC0000',
        }, key_length=2)
        sprite = p.render(["r1r2"])
        assert sprite.get_pixel(0, 0) == (255, 0, 0, 255)
        assert sprite.get_pixel(1, 0) == (204, 0, 0, 255)

    def test_wrong_key_length_raises(self):
        with pytest.raises(ValueError, match="length"):
            MultiCharPalette({'a': px.BLACK}, key_length=2)

    def test_row_not_divisible_raises(self):
        p = MultiCharPalette({'ab': px.BLACK}, key_length=2)
        with pytest.raises(ValueError, match="not divisible"):
            p.render(["abc"])

    def test_unknown_key_raises(self):
        p = MultiCharPalette({'ab': px.BLACK}, key_length=2)
        with pytest.raises(KeyError):
            p.render(["cd"])

    def test_empty_rows_raises(self):
        p = MultiCharPalette({'ab': px.BLACK}, key_length=2)
        with pytest.raises(ValueError):
            p.render([])

    def test_unequal_row_lengths_raises(self):
        p = MultiCharPalette({'ab': px.BLACK, 'cd': px.WHITE}, key_length=2)
        with pytest.raises(ValueError, match="chars"):
            p.render(["ab", "abcd"])

    def test_to_string(self):
        p = MultiCharPalette({
            '..': px.TRANSPARENT,
            'KK': px.BLACK,
        }, key_length=2)
        sprite = p.render(["..KK", "KK.."])
        rows = p.to_string(sprite)
        assert rows == ["..KK", "KK.."]

    def test_round_trip(self):
        """render -> to_string -> render produces the same sprite."""
        p = MultiCharPalette({
            '..': px.TRANSPARENT,
            'KK': px.BLACK,
            'rr': (255, 0, 0, 255),
        }, key_length=2)
        original_rows = ["..KKrr", "KKrr..", "rr..KK"]
        sprite1 = p.render(original_rows)
        rows = p.to_string(sprite1)
        assert rows == original_rows
        sprite2 = p.render(rows)
        assert sprite1 == sprite2

    def test_to_string_missing_color_raises(self):
        p = MultiCharPalette({'ab': px.BLACK}, key_length=2)
        # Create a sprite with a color not in the palette
        sprite = px.Sprite([[(255, 0, 0, 255)]])
        with pytest.raises(KeyError):
            p.to_string(sprite)

    def test_contains_and_len(self):
        p = MultiCharPalette({'ab': px.BLACK, 'cd': px.WHITE}, key_length=2)
        assert 'ab' in p
        assert 'xx' not in p
        assert len(p) == 2

    def test_key_length_1_works_like_palette(self):
        p = MultiCharPalette({'.': px.TRANSPARENT, 'K': px.BLACK}, key_length=1)
        sprite = p.render([".K", "K."])
        assert sprite.size == (2, 2)
        assert sprite.get_pixel(0, 0) == px.TRANSPARENT
        assert sprite.get_pixel(1, 0) == px.BLACK


class TestAutoPalette:
    def test_from_sprite_single_char(self):
        """Small number of colors -> single-char Palette."""
        p = px.Palette({'.': px.TRANSPARENT, 'K': px.BLACK, 'r': (255, 0, 0, 255)})
        original = px.StringCanvas(p).render(["..KK", "KrrK", "..KK"])
        palette, rows = AutoPalette.from_sprite(original)
        assert isinstance(palette, px.Palette)
        assert len(rows) == 3
        assert len(rows[0]) == 4
        # Reconstruct and verify
        reconstructed = px.StringCanvas(palette).render(rows)
        assert original == reconstructed

    def test_from_sprite_round_trip(self):
        """Sprite -> AutoPalette -> render -> same sprite."""
        colors = [
            (255, 0, 0, 255),
            (0, 255, 0, 255),
            (0, 0, 255, 255),
            px.BLACK,
            px.WHITE,
        ]
        pixels = [[colors[x % len(colors)] for x in range(5)] for _ in range(3)]
        original = px.Sprite(pixels)
        palette, rows = AutoPalette.from_sprite(original)
        if isinstance(palette, px.Palette):
            reconstructed = px.StringCanvas(palette).render(rows)
        else:
            reconstructed = palette.render(rows)
        assert original == reconstructed

    def test_from_sprite_frequency_order(self):
        """Most frequent color gets first key."""
        # Red appears 3 times, black 1 time
        pixels = [
            [(255, 0, 0, 255), (255, 0, 0, 255)],
            [(255, 0, 0, 255), px.BLACK],
        ]
        original = px.Sprite(pixels)
        palette, rows = AutoPalette.from_sprite(original)
        assert isinstance(palette, px.Palette)
        # Most frequent (red) should get 'a' (first key)
        red_key = palette.reverse_lookup((255, 0, 0, 255))
        assert red_key == 'a'

    def test_from_sprite_many_colors_uses_multichar(self):
        """More than 62 unique colors forces 2-char keys."""
        # Create 70 unique colors
        colors = [(i, i * 3 % 256, i * 7 % 256, 255) for i in range(70)]
        pixels = [colors[i:i+10] for i in range(0, 70, 10)]
        original = px.Sprite(pixels)
        palette, rows = AutoPalette.from_sprite(original)
        assert isinstance(palette, MultiCharPalette)
        assert palette.key_length == 2
        # Round-trip
        reconstructed = palette.render(rows)
        assert original == reconstructed
