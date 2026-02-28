"""Tests for color_utils — HSL conversion, manipulation, ramps, dithering."""

import pytest
import pixeldot as px


class TestHSLConversion:
    def test_red(self):
        h, s, l = px.rgb_to_hsl((255, 0, 0, 255))
        assert h == pytest.approx(0.0, abs=1)
        assert s == pytest.approx(1.0, abs=0.01)
        assert l == pytest.approx(0.5, abs=0.01)

    def test_green(self):
        h, s, l = px.rgb_to_hsl((0, 255, 0, 255))
        assert h == pytest.approx(120.0, abs=1)
        assert s == pytest.approx(1.0, abs=0.01)
        assert l == pytest.approx(0.5, abs=0.01)

    def test_blue(self):
        h, s, l = px.rgb_to_hsl((0, 0, 255, 255))
        assert h == pytest.approx(240.0, abs=1)
        assert s == pytest.approx(1.0, abs=0.01)
        assert l == pytest.approx(0.5, abs=0.01)

    def test_white(self):
        h, s, l = px.rgb_to_hsl(px.WHITE)
        assert s == pytest.approx(0.0, abs=0.01)
        assert l == pytest.approx(1.0, abs=0.01)

    def test_black(self):
        h, s, l = px.rgb_to_hsl(px.BLACK)
        assert s == pytest.approx(0.0, abs=0.01)
        assert l == pytest.approx(0.0, abs=0.01)

    def test_round_trip(self):
        original = (200, 100, 50, 255)
        h, s, l = px.rgb_to_hsl(original)
        restored = px.hsl_to_rgb(h, s, l, 255)
        for i in range(3):
            assert restored[i] == pytest.approx(original[i], abs=2)

    def test_grey(self):
        h, s, l = px.rgb_to_hsl((128, 128, 128, 255))
        assert s == pytest.approx(0.0, abs=0.01)
        assert l == pytest.approx(0.502, abs=0.01)

    def test_preserves_alpha(self):
        result = px.hsl_to_rgb(0, 1.0, 0.5, 128)
        assert result[3] == 128


class TestLightenDarken:
    def test_lighten(self):
        original = (100, 50, 50, 255)
        lighter = px.lighten(original, 0.2)
        _, _, l_orig = px.rgb_to_hsl(original)
        _, _, l_new = px.rgb_to_hsl(lighter)
        assert l_new > l_orig

    def test_darken(self):
        original = (100, 50, 50, 255)
        darker = px.darken(original, 0.2)
        _, _, l_orig = px.rgb_to_hsl(original)
        _, _, l_new = px.rgb_to_hsl(darker)
        assert l_new < l_orig

    def test_lighten_preserves_alpha(self):
        result = px.lighten((100, 50, 50, 128), 0.1)
        assert result[3] == 128

    def test_darken_preserves_alpha(self):
        result = px.darken((100, 50, 50, 128), 0.1)
        assert result[3] == 128


class TestSaturateDesaturate:
    def test_saturate(self):
        original = (150, 100, 100, 255)
        result = px.saturate(original, 0.2)
        _, s_orig, _ = px.rgb_to_hsl(original)
        _, s_new, _ = px.rgb_to_hsl(result)
        assert s_new > s_orig

    def test_desaturate(self):
        original = (150, 100, 100, 255)
        result = px.desaturate(original, 0.2)
        _, s_orig, _ = px.rgb_to_hsl(original)
        _, s_new, _ = px.rgb_to_hsl(result)
        assert s_new < s_orig


class TestColorLerp:
    def test_t0(self):
        c1 = (0, 0, 0, 255)
        c2 = (255, 255, 255, 255)
        assert px.color_lerp(c1, c2, 0.0) == c1

    def test_t1(self):
        c1 = (0, 0, 0, 255)
        c2 = (255, 255, 255, 255)
        assert px.color_lerp(c1, c2, 1.0) == c2

    def test_midpoint(self):
        c1 = (0, 0, 0, 255)
        c2 = (200, 100, 50, 255)
        mid = px.color_lerp(c1, c2, 0.5)
        assert mid == (100, 50, 25, 255)

    def test_clamps_t(self):
        c1 = (0, 0, 0, 255)
        c2 = (255, 255, 255, 255)
        assert px.color_lerp(c1, c2, -1.0) == c1
        assert px.color_lerp(c1, c2, 2.0) == c2


class TestColorRamp:
    def test_basic_ramp(self):
        ramp = px.color_ramp(px.BLACK, px.WHITE, 3)
        assert len(ramp) == 3
        assert ramp[0] == px.BLACK
        assert ramp[-1] == px.WHITE

    def test_ramp_too_few_steps(self):
        with pytest.raises(ValueError):
            px.color_ramp(px.BLACK, px.WHITE, 1)


class TestAutoShades:
    def test_count(self):
        shades = px.auto_shades((200, 50, 50, 255), count=5)
        assert len(shades) == 5

    def test_highlight_to_shadow(self):
        shades = px.auto_shades((200, 50, 50, 255), count=5)
        # First should be lighter, last should be darker
        _, _, l_first = px.rgb_to_hsl(shades[0])
        _, _, l_last = px.rgb_to_hsl(shades[-1])
        assert l_first > l_last

    def test_too_few(self):
        with pytest.raises(ValueError):
            px.auto_shades(px.BLACK, count=1)


class TestDitherPattern:
    def test_checker(self):
        pattern = px.dither_pattern(px.BLACK, px.WHITE, "checker")
        assert pattern == [[True, False], [False, True]]

    def test_horizontal(self):
        pattern = px.dither_pattern(px.BLACK, px.WHITE, "horizontal")
        assert pattern == [[True, True], [False, False]]

    def test_vertical(self):
        pattern = px.dither_pattern(px.BLACK, px.WHITE, "vertical")
        assert pattern == [[True, False], [True, False]]

    def test_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown dither"):
            px.dither_pattern(px.BLACK, px.WHITE, "spiral")


class TestColorDistance:
    def test_same_color(self):
        assert px.color_distance(px.BLACK, px.BLACK) == 0.0

    def test_different_colors(self):
        d = px.color_distance(px.BLACK, px.WHITE)
        assert d > 0

    def test_symmetry(self):
        c1 = (100, 50, 200, 255)
        c2 = (50, 100, 100, 255)
        assert px.color_distance(c1, c2) == px.color_distance(c2, c1)
