"""Tests for layer system — blend modes, compositing, and layer management."""

import pytest
import pixeldot as px
from pixeldot.layers import BlendMode, Layer, LayerStack, _blend_pixel


def make_sprite(rows):
    """Helper: create sprite from string rows."""
    p = px.Palette({'.': px.TRANSPARENT, 'K': px.BLACK, 'r': '#FF0000', 'g': '#00FF00', 'b': '#0000FF', 'W': px.WHITE})
    return px.StringCanvas(p).render(rows)


def solid_sprite(color, w=2, h=2):
    """Helper: create a solid-color sprite."""
    pixels = [[color] * w for _ in range(h)]
    return px.Sprite(pixels)


class TestLayerManagement:
    def test_add_and_get_layer(self):
        stack = LayerStack(2, 2)
        s = make_sprite(["rr", "rr"])
        stack.add_layer("bg", s)
        layer = stack.get_layer("bg")
        assert layer.name == "bg"
        assert layer.opacity == 1.0
        assert layer.visible is True
        assert layer.blend_mode == BlendMode.NORMAL

    def test_add_duplicate_name_raises(self):
        stack = LayerStack(2, 2)
        s = make_sprite(["rr", "rr"])
        stack.add_layer("bg", s)
        with pytest.raises(ValueError, match="already exists"):
            stack.add_layer("bg", s)

    def test_add_wrong_size_raises(self):
        stack = LayerStack(2, 2)
        s = make_sprite(["rrr", "rrr"])
        with pytest.raises(ValueError, match="doesn't match"):
            stack.add_layer("bg", s)

    def test_add_at_position(self):
        stack = LayerStack(2, 2)
        s = make_sprite(["rr", "rr"])
        stack.add_layer("top", s)
        stack.add_layer("bottom", s, position=0)
        assert stack.layer_names == ["bottom", "top"]

    def test_remove_layer(self):
        stack = LayerStack(2, 2)
        s = make_sprite(["rr", "rr"])
        stack.add_layer("bg", s)
        removed = stack.remove_layer("bg")
        assert removed.name == "bg"
        assert stack.layer_names == []

    def test_remove_nonexistent_raises(self):
        stack = LayerStack(2, 2)
        with pytest.raises(KeyError):
            stack.remove_layer("nope")

    def test_get_nonexistent_raises(self):
        stack = LayerStack(2, 2)
        with pytest.raises(KeyError):
            stack.get_layer("nope")

    def test_reorder(self):
        stack = LayerStack(2, 2)
        s = make_sprite(["rr", "rr"])
        stack.add_layer("a", s)
        stack.add_layer("b", s)
        stack.add_layer("c", s)
        stack.reorder(["c", "a", "b"])
        assert stack.layer_names == ["c", "a", "b"]

    def test_reorder_missing_name_raises(self):
        stack = LayerStack(2, 2)
        s = make_sprite(["rr", "rr"])
        stack.add_layer("a", s)
        with pytest.raises(ValueError):
            stack.reorder(["b"])

    def test_layer_names_order(self):
        stack = LayerStack(2, 2)
        s = make_sprite(["rr", "rr"])
        stack.add_layer("bottom", s)
        stack.add_layer("middle", s)
        stack.add_layer("top", s)
        assert stack.layer_names == ["bottom", "middle", "top"]

    def test_set_visibility(self):
        stack = LayerStack(2, 2)
        s = make_sprite(["rr", "rr"])
        stack.add_layer("bg", s)
        stack.set_visibility("bg", False)
        assert stack.get_layer("bg").visible is False

    def test_set_opacity(self):
        stack = LayerStack(2, 2)
        s = make_sprite(["rr", "rr"])
        stack.add_layer("bg", s)
        stack.set_opacity("bg", 0.5)
        assert stack.get_layer("bg").opacity == 0.5

    def test_set_blend_mode(self):
        stack = LayerStack(2, 2)
        s = make_sprite(["rr", "rr"])
        stack.add_layer("bg", s)
        stack.set_blend_mode("bg", BlendMode.MULTIPLY)
        assert stack.get_layer("bg").blend_mode == BlendMode.MULTIPLY


class TestFlatten:
    def test_flatten_single_layer(self):
        stack = LayerStack(2, 2)
        s = make_sprite(["rr", "rr"])
        stack.add_layer("bg", s)
        result = stack.flatten()
        assert result.get_pixel(0, 0) == (255, 0, 0, 255)

    def test_flatten_empty_stack(self):
        stack = LayerStack(2, 2)
        result = stack.flatten()
        assert result.get_pixel(0, 0) == px.TRANSPARENT

    def test_flatten_hidden_layer_ignored(self):
        stack = LayerStack(2, 2)
        red = make_sprite(["rr", "rr"])
        green = make_sprite(["gg", "gg"])
        stack.add_layer("bg", red)
        stack.add_layer("fg", green)
        stack.set_visibility("fg", False)
        result = stack.flatten()
        assert result.get_pixel(0, 0) == (255, 0, 0, 255)

    def test_flatten_normal_opaque_on_opaque(self):
        """Top opaque layer completely covers bottom."""
        stack = LayerStack(2, 2)
        red = make_sprite(["rr", "rr"])
        green = make_sprite(["gg", "gg"])
        stack.add_layer("bg", red)
        stack.add_layer("fg", green)
        result = stack.flatten()
        assert result.get_pixel(0, 0) == (0, 255, 0, 255)

    def test_flatten_with_transparency(self):
        """Top layer has transparent pixels, bottom shows through."""
        stack = LayerStack(2, 2)
        red = make_sprite(["rr", "rr"])
        partial = make_sprite([".g", "g."])
        stack.add_layer("bg", red)
        stack.add_layer("fg", partial)
        result = stack.flatten()
        assert result.get_pixel(0, 0) == (255, 0, 0, 255)  # transparent on top
        assert result.get_pixel(1, 0) == (0, 255, 0, 255)   # green on top

    def test_flatten_with_opacity(self):
        """Layer opacity < 1.0 blends with layer below."""
        stack = LayerStack(1, 1)
        white = solid_sprite(px.WHITE, 1, 1)
        black = solid_sprite(px.BLACK, 1, 1)
        stack.add_layer("bg", white)
        stack.add_layer("fg", black, opacity=0.5)
        result = stack.flatten()
        r, g, b, a = result.get_pixel(0, 0)
        # Black at 50% over white should be ~(127, 127, 127)
        assert a == 255
        assert 126 <= r <= 128
        assert 126 <= g <= 128
        assert 126 <= b <= 128


class TestBlendModes:
    def test_normal_blend(self):
        """Normal blend is standard alpha compositing."""
        result = _blend_pixel((255, 0, 0, 255), (0, 255, 0, 255), BlendMode.NORMAL, 1.0)
        assert result == (255, 0, 0, 255)

    def test_multiply_blend(self):
        """MULTIPLY: white * color = color; black * anything = black."""
        # White * Red = Red
        result = _blend_pixel(px.WHITE, (255, 0, 0, 255), BlendMode.MULTIPLY, 1.0)
        assert result[0] == 255
        assert result[1] == 0
        assert result[2] == 0

        # Black * anything = Black
        result = _blend_pixel(px.BLACK, (255, 128, 64, 255), BlendMode.MULTIPLY, 1.0)
        assert result[0] == 0
        assert result[1] == 0
        assert result[2] == 0

    def test_screen_blend(self):
        """SCREEN: black screen color = color; white screen anything = white."""
        # Black screen Red = Red
        result = _blend_pixel(px.BLACK, (255, 0, 0, 255), BlendMode.SCREEN, 1.0)
        assert result[0] == 255
        assert result[1] == 0
        assert result[2] == 0

        # White screen anything = White
        result = _blend_pixel(px.WHITE, (128, 128, 128, 255), BlendMode.SCREEN, 1.0)
        assert result[0] == 255
        assert result[1] == 255
        assert result[2] == 255

    def test_overlay_blend(self):
        """OVERLAY: depends on dst value."""
        # 50% gray on 50% gray
        mid = (128, 128, 128, 255)
        result = _blend_pixel(mid, mid, BlendMode.OVERLAY, 1.0)
        # Overlay of 0.5 on 0.5: since dst=0.5 >= 0.5: 1 - 2*(1-0.5)*(1-0.5) = 0.5
        assert 126 <= result[0] <= 130

    def test_add_blend(self):
        """ADD: clamped addition."""
        result = _blend_pixel(
            (200, 100, 50, 255), (100, 200, 250, 255), BlendMode.ADD, 1.0
        )
        assert result[0] == 255  # clamped
        assert result[1] == 255  # clamped (300/255 -> 1.0 -> 255)
        assert result[2] == 255  # clamped

    def test_add_blend_no_clamp(self):
        """ADD without overflow."""
        result = _blend_pixel(
            (10, 20, 30, 255), (40, 50, 60, 255), BlendMode.ADD, 1.0
        )
        r, g, b, a = result
        assert 49 <= r <= 51  # ~50
        assert 69 <= g <= 71  # ~70
        assert 89 <= b <= 91  # ~90

    def test_subtract_blend(self):
        """SUBTRACT: clamped subtraction."""
        result = _blend_pixel(
            (100, 200, 255, 255), (200, 100, 50, 255), BlendMode.SUBTRACT, 1.0
        )
        r, g, b, a = result
        # dst - src: (200-100, 100-200, 50-255) = (100, 0, 0)
        assert 99 <= r <= 101
        assert g == 0
        assert b == 0

    def test_blend_with_zero_opacity(self):
        """Zero opacity means no change."""
        dst = (100, 100, 100, 255)
        result = _blend_pixel((255, 0, 0, 255), dst, BlendMode.NORMAL, 0.0)
        assert result == dst

    def test_blend_with_transparent_src(self):
        """Transparent source pixel is no-op."""
        dst = (100, 100, 100, 255)
        result = _blend_pixel(px.TRANSPARENT, dst, BlendMode.MULTIPLY, 1.0)
        assert result == dst

    def test_blend_modes_in_flatten(self):
        """Integration: blend modes work through LayerStack.flatten()."""
        stack = LayerStack(1, 1)
        white = solid_sprite(px.WHITE, 1, 1)
        red = solid_sprite((255, 0, 0, 255), 1, 1)
        stack.add_layer("bg", white)
        stack.add_layer("fg", red, blend_mode=BlendMode.MULTIPLY)
        result = stack.flatten()
        pixel = result.get_pixel(0, 0)
        # Multiply: white * red = red
        assert pixel[0] == 255
        assert pixel[1] == 0
        assert pixel[2] == 0
