"""Tests for FastSprite — NumPy-backed high-performance sprite."""

import pytest
import pixeldot as px

numpy = pytest.importorskip("numpy")
from pixeldot.fast_sprite import FastSprite


def make_sprite(rows):
    """Helper: create sprite from string rows."""
    p = px.Palette({'.': px.TRANSPARENT, 'K': px.BLACK, 'r': '#FF0000', 'g': '#00FF00'})
    return px.StringCanvas(p).render(rows)


class TestCreation:
    def test_empty(self):
        fs = FastSprite.empty(4, 3)
        assert fs.size == (4, 3)
        assert fs.get_pixel(0, 0) == (0, 0, 0, 0)

    def test_invalid_shape(self):
        with pytest.raises(ValueError, match="shape"):
            FastSprite(numpy.zeros((4, 4), dtype=numpy.uint8))

    def test_from_image(self):
        sprite = make_sprite(["Kr", "rK"])
        img = sprite.to_image()
        fs = FastSprite.from_image(img)
        assert fs.size == (2, 2)
        assert fs.get_pixel(0, 0) == px.BLACK
        assert fs.get_pixel(1, 0) == (255, 0, 0, 255)


class TestConversion:
    def test_from_sprite(self):
        sprite = make_sprite(["Kr", "rK"])
        fs = FastSprite.from_sprite(sprite)
        assert fs.size == (2, 2)
        assert fs.get_pixel(0, 0) == px.BLACK
        assert fs.get_pixel(1, 0) == (255, 0, 0, 255)

    def test_to_sprite(self):
        sprite = make_sprite(["Kr", "rK"])
        fs = FastSprite.from_sprite(sprite)
        back = fs.to_sprite()
        assert back == sprite

    def test_round_trip(self):
        sprite = make_sprite(["KrK", ".g.", "r.r"])
        fs = FastSprite.from_sprite(sprite)
        back = fs.to_sprite()
        assert back == sprite

    def test_image_round_trip(self):
        fs = FastSprite.from_sprite(make_sprite(["Kr", "rK"]))
        img = fs.to_image()
        fs2 = FastSprite.from_image(img)
        assert fs == fs2


class TestTransforms:
    def test_crop(self):
        fs = FastSprite.from_sprite(make_sprite(["KKK", "KrK", "KKK"]))
        cropped = fs.crop(1, 1, 1, 1)
        assert cropped.size == (1, 1)
        assert cropped.get_pixel(0, 0) == (255, 0, 0, 255)

    def test_crop_clamp(self):
        fs = FastSprite.from_sprite(make_sprite(["Kr", "rK"]))
        cropped = fs.crop(0, 0, 10, 10)
        assert cropped.size == (2, 2)

    def test_crop_empty_raises(self):
        fs = FastSprite.from_sprite(make_sprite(["Kr"]))
        with pytest.raises(ValueError, match="empty"):
            fs.crop(5, 5, 1, 1)

    def test_paste_opaque(self):
        bg = FastSprite.empty(3, 3)
        dot = FastSprite.from_sprite(make_sprite(["r"]))
        result = bg.paste(dot, 1, 1)
        assert result.get_pixel(1, 1) == (255, 0, 0, 255)
        assert result.get_pixel(0, 0) == (0, 0, 0, 0)
        # Original unchanged
        assert bg.get_pixel(1, 1) == (0, 0, 0, 0)

    def test_paste_transparent(self):
        bg = FastSprite.from_sprite(make_sprite(["KK"]))
        overlay = FastSprite.from_sprite(make_sprite([".r"]))
        result = bg.paste(overlay, 0, 0)
        assert result.get_pixel(0, 0) == px.BLACK
        assert result.get_pixel(1, 0) == (255, 0, 0, 255)

    def test_paste_out_of_bounds(self):
        bg = FastSprite.empty(2, 2)
        dot = FastSprite.from_sprite(make_sprite(["r"]))
        result = bg.paste(dot, 5, 5)
        assert result.get_pixel(0, 0) == (0, 0, 0, 0)

    def test_flip_h(self):
        fs = FastSprite.from_sprite(make_sprite(["Kr"]))
        flipped = fs.flip_h()
        assert flipped.get_pixel(0, 0) == (255, 0, 0, 255)
        assert flipped.get_pixel(1, 0) == px.BLACK

    def test_flip_v(self):
        fs = FastSprite.from_sprite(make_sprite(["K", "r"]))
        flipped = fs.flip_v()
        assert flipped.get_pixel(0, 0) == (255, 0, 0, 255)
        assert flipped.get_pixel(0, 1) == px.BLACK

    def test_replace_color(self):
        fs = FastSprite.from_sprite(make_sprite(["Kr"]))
        replaced = fs.replace_color(px.BLACK, (255, 0, 0, 255))
        assert replaced.get_pixel(0, 0) == (255, 0, 0, 255)
        assert replaced.get_pixel(1, 0) == (255, 0, 0, 255)

    def test_trim(self):
        fs = FastSprite.from_sprite(make_sprite(["...", ".K.", "..."]))
        trimmed = fs.trim()
        assert trimmed.size == (1, 1)
        assert trimmed.get_pixel(0, 0) == px.BLACK

    def test_trim_fully_transparent(self):
        fs = FastSprite.from_sprite(make_sprite(["...", "..."]))
        trimmed = fs.trim()
        assert trimmed.size == (1, 1)


class TestBounds:
    def test_opaque_bounds(self):
        fs = FastSprite.from_sprite(make_sprite(["...", ".Kr", "..."]))
        bounds = fs.opaque_bounds()
        assert bounds == (1, 1, 2, 1)

    def test_opaque_bounds_none(self):
        fs = FastSprite.from_sprite(make_sprite(["...", "..."]))
        assert fs.opaque_bounds() is None


class TestEquality:
    def test_equal(self):
        a = FastSprite.from_sprite(make_sprite(["Kr"]))
        b = FastSprite.from_sprite(make_sprite(["Kr"]))
        assert a == b

    def test_not_equal(self):
        a = FastSprite.from_sprite(make_sprite(["Kr"]))
        b = FastSprite.from_sprite(make_sprite(["rK"]))
        assert a != b

    def test_not_equal_to_other_types(self):
        fs = FastSprite.from_sprite(make_sprite(["Kr"]))
        assert fs != "not a sprite"


class TestGetPixel:
    def test_out_of_bounds(self):
        fs = FastSprite.empty(2, 2)
        with pytest.raises(IndexError):
            fs.get_pixel(5, 0)

    def test_repr(self):
        fs = FastSprite.empty(3, 4)
        assert repr(fs) == "FastSprite(3x4)"
