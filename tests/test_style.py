"""Tests for style — preset palettes, outline, and shadow effects."""

import pytest
import pixeldot as px


def make_sprite(rows):
    """Helper: create sprite from string rows."""
    p = px.Palette({'.': px.TRANSPARENT, 'K': px.BLACK, 'r': '#FF0000'})
    return px.StringCanvas(p).render(rows)


class TestPresetPalettes:
    def test_gameboy_has_4_colors(self):
        assert len(px.GAMEBOY_PALETTE) == 4

    def test_nes_has_16_colors(self):
        assert len(px.NES_PALETTE) == 16

    def test_pico8_has_16_colors(self):
        assert len(px.PICO8_PALETTE) == 16

    def test_sweetie16_has_16_colors(self):
        assert len(px.SWEETIE16_PALETTE) == 16

    def test_endesga32_has_32_colors(self):
        assert len(px.ENDESGA32_PALETTE) == 32

    def test_all_rgba_tuples(self):
        for name, palette in [
            ("gameboy", px.GAMEBOY_PALETTE),
            ("pico8", px.PICO8_PALETTE),
        ]:
            for key, color in palette.items():
                assert len(color) == 4, f"{name}.{key} is not RGBA"
                assert all(0 <= c <= 255 for c in color), f"{name}.{key} out of range"

    def test_list_presets(self):
        names = px.list_preset_palettes()
        assert "gameboy" in names
        assert "pico8" in names
        assert "nes" in names
        assert "sweetie16" in names
        assert "endesga32" in names

    def test_get_preset_palette(self):
        p = px.get_preset_palette("pico8")
        assert isinstance(p, px.Palette)
        assert len(p) == 16

    def test_get_preset_case_insensitive(self):
        p = px.get_preset_palette("PICO8")
        assert isinstance(p, px.Palette)

    def test_unknown_preset_raises(self):
        with pytest.raises(KeyError, match="Unknown preset"):
            px.get_preset_palette("nonexistent")


class TestOutlineStyle:
    def test_enum_values(self):
        assert px.OutlineStyle.NONE.value == "none"
        assert px.OutlineStyle.THIN.value == "thin"
        assert px.OutlineStyle.THICK.value == "thick"
        assert px.OutlineStyle.SELECTIVE.value == "selective"


class TestApplyOutline:
    def test_none_returns_same(self):
        s = make_sprite(["K"])
        result = px.apply_outline(s, style=px.OutlineStyle.NONE)
        assert result == s

    def test_thin_outline_expands(self):
        s = make_sprite(["K"])
        result = px.apply_outline(s, style=px.OutlineStyle.THIN)
        # 1x1 + 2 border = 3x3
        assert result.width == 3
        assert result.height == 3

    def test_thin_outline_has_outline_pixels(self):
        s = make_sprite(["K"])
        outline_color = (255, 0, 0, 255)
        result = px.apply_outline(s, color=outline_color, style=px.OutlineStyle.THIN)
        # Center should be original pixel
        assert result.get_pixel(1, 1) == px.BLACK
        # Cardinal neighbors should be outline
        assert result.get_pixel(1, 0) == outline_color  # top
        assert result.get_pixel(1, 2) == outline_color  # bottom
        assert result.get_pixel(0, 1) == outline_color  # left
        assert result.get_pixel(2, 1) == outline_color  # right

    def test_thick_outline(self):
        s = make_sprite(["K"])
        result = px.apply_outline(s, style=px.OutlineStyle.THICK)
        assert result.width == 3
        assert result.height == 3
        # All 8 neighbors should be outlined
        for x in range(3):
            for y in range(3):
                if (x, y) != (1, 1):
                    assert result.get_pixel(x, y)[3] > 0

    def test_outline_does_not_fill_isolated_transparent(self):
        s = make_sprite(["K..", "...", "..K"])
        result = px.apply_outline(s, style=px.OutlineStyle.THIN)
        # Far from any opaque pixel, center should stay transparent
        # Original (1,1) maps to (2,2) in expanded. Not adjacent to either pixel.
        assert result.get_pixel(2, 2) == px.TRANSPARENT


class TestApplyShadow:
    def test_shadow_expands_size(self):
        s = make_sprite(["K"])
        result = px.apply_shadow(s, offset=(1, 1))
        assert result.width == 2
        assert result.height == 2

    def test_shadow_default_opacity(self):
        s = make_sprite(["K"])
        result = px.apply_shadow(s, offset=(1, 1))
        # Shadow pixel should be semi-transparent
        shadow = result.get_pixel(1, 1)
        assert shadow[3] == 128  # round(0.5 * 255)

    def test_shadow_custom_color(self):
        s = make_sprite(["K"])
        shadow_color = (255, 0, 0, 255)
        result = px.apply_shadow(s, offset=(1, 1), color=shadow_color, opacity=1.0)
        shadow = result.get_pixel(1, 1)
        assert shadow[:3] == (255, 0, 0)

    def test_original_on_top(self):
        s = make_sprite(["K"])
        result = px.apply_shadow(s, offset=(0, 0))
        # Original should be on top of shadow
        assert result.get_pixel(0, 0) == px.BLACK
