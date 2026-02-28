"""Tests for Sprite — immutable pixel container."""

import pytest
import pixeldot as px


def make_sprite(rows):
    """Helper: create sprite from string rows."""
    p = px.Palette({'.': px.TRANSPARENT, 'K': px.BLACK, 'r': '#FF0000', 'g': '#00FF00'})
    return px.StringCanvas(p).render(rows)


class TestCreation:
    def test_empty(self):
        s = px.Sprite.empty(4, 3)
        assert s.size == (4, 3)
        assert s.get_pixel(0, 0) == px.TRANSPARENT

    def test_invalid_empty(self):
        with pytest.raises(ValueError):
            px.Sprite([])

    def test_jagged_rows(self):
        with pytest.raises(ValueError, match="Row 1"):
            px.Sprite([
                [(0, 0, 0, 255), (0, 0, 0, 255)],
                [(0, 0, 0, 255)],
            ])


class TestTransforms:
    def test_crop(self):
        s = make_sprite(["KKK", "KrK", "KKK"])
        cropped = s.crop(1, 1, 1, 1)
        assert cropped.size == (1, 1)
        assert cropped.get_pixel(0, 0) == (255, 0, 0, 255)

    def test_paste(self):
        bg = px.Sprite.empty(3, 3)
        dot = make_sprite(["r"])
        result = bg.paste(dot, 1, 1)
        assert result.get_pixel(1, 1) == (255, 0, 0, 255)
        assert result.get_pixel(0, 0) == px.TRANSPARENT
        # Original unchanged (immutable)
        assert bg.get_pixel(1, 1) == px.TRANSPARENT

    def test_flip_h(self):
        s = make_sprite(["Kr"])
        flipped = s.flip_h()
        assert flipped.get_pixel(0, 0) == (255, 0, 0, 255)
        assert flipped.get_pixel(1, 0) == px.BLACK

    def test_flip_v(self):
        s = make_sprite(["K", "r"])
        flipped = s.flip_v()
        assert flipped.get_pixel(0, 0) == (255, 0, 0, 255)
        assert flipped.get_pixel(0, 1) == px.BLACK

    def test_replace_color(self):
        s = make_sprite(["Kr"])
        replaced = s.replace_color(px.BLACK, (255, 0, 0, 255))
        assert replaced.get_pixel(0, 0) == (255, 0, 0, 255)
        assert replaced.get_pixel(1, 0) == (255, 0, 0, 255)

    def test_trim(self):
        s = make_sprite(["...", ".K.", "..."])
        trimmed = s.trim()
        assert trimmed.size == (1, 1)
        assert trimmed.get_pixel(0, 0) == px.BLACK

    def test_trim_fully_transparent(self):
        s = make_sprite(["...", "...", "..."])
        trimmed = s.trim()
        assert trimmed.size == (1, 1)


class TestBounds:
    def test_opaque_bounds(self):
        s = make_sprite(["...", ".Kr", "..."])
        bounds = s.opaque_bounds()
        assert bounds == (1, 1, 2, 1)

    def test_opaque_bounds_none(self):
        s = make_sprite(["...", "..."])
        assert s.opaque_bounds() is None


class TestEquality:
    def test_equal(self):
        a = make_sprite(["Kr"])
        b = make_sprite(["Kr"])
        assert a == b

    def test_not_equal(self):
        a = make_sprite(["Kr"])
        b = make_sprite(["rK"])
        assert a != b


class TestImageConversion:
    def test_to_from_image(self):
        original = make_sprite(["Kr", "rK"])
        img = original.to_image()
        restored = px.Sprite.from_image(img)
        assert original == restored
