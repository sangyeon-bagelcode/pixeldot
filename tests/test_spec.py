"""Tests for the batch spec system."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
import yaml

from pixeldot.spec import Spec, SpecError, load_spec, render_spec
from pixeldot.color import BLACK, TRANSPARENT, WHITE, Palette
from pixeldot.sprite import Sprite


def _write_spec(tmp_path: Path, data: dict) -> Path:
    """Write a YAML spec to a temp file and return its path."""
    spec_file = tmp_path / "spec.yaml"
    spec_file.write_text(yaml.dump(data, default_flow_style=False))
    return spec_file


# ---------------------------------------------------------------------------
# Basic palette + block rendering
# ---------------------------------------------------------------------------


class TestBasicBlock:
    def test_simple_sprite(self, tmp_path: Path):
        data = {
            "palette": {".": "transparent", "K": "#000000"},
            "sprites": {
                "dot": {
                    "block": ".K.\nK.K\n.K.",
                    "save": "out/dot.png",
                }
            },
        }
        spec_file = _write_spec(tmp_path, data)
        results = render_spec(spec_file, dry_run=True)
        assert "dot" in results
        sprite = results["dot"]
        assert sprite.size == (3, 3)
        # center pixel should be transparent
        assert sprite.get_pixel(1, 1) == TRANSPARENT
        # top-center should be black
        assert sprite.get_pixel(1, 0) == BLACK

    def test_reserved_colors(self, tmp_path: Path):
        data = {
            "palette": {".": "transparent", "K": "black", "W": "white"},
            "sprites": {
                "test": {"block": "KW\n.K"}
            },
        }
        spec_file = _write_spec(tmp_path, data)
        results = render_spec(spec_file, dry_run=True)
        sprite = results["test"]
        assert sprite.get_pixel(0, 0) == BLACK
        assert sprite.get_pixel(1, 0) == WHITE
        assert sprite.get_pixel(0, 1) == TRANSPARENT

    def test_hex_colors(self, tmp_path: Path):
        data = {
            "palette": {"r": "#FF0000", "g": "#00FF00"},
            "sprites": {
                "rg": {"block": "rg"}
            },
        }
        spec_file = _write_spec(tmp_path, data)
        results = render_spec(spec_file, dry_run=True)
        sprite = results["rg"]
        assert sprite.get_pixel(0, 0) == (255, 0, 0, 255)
        assert sprite.get_pixel(1, 0) == (0, 255, 0, 255)

    def test_save_creates_files(self, tmp_path: Path):
        data = {
            "palette": {".": "transparent", "K": "black"},
            "sprites": {
                "dot": {
                    "block": "K",
                    "save": "out/dot.png",
                    "preview": "out/dot_10x.png",
                }
            },
        }
        spec_file = _write_spec(tmp_path, data)
        results = render_spec(spec_file)
        assert (tmp_path / "out" / "dot.png").exists()
        assert (tmp_path / "out" / "dot_10x.png").exists()


# ---------------------------------------------------------------------------
# Sprite references: strip, grid
# ---------------------------------------------------------------------------


class TestSpriteReferences:
    def test_strip(self, tmp_path: Path):
        data = {
            "palette": {".": "transparent", "K": "black"},
            "sprites": {
                "f1": {"block": "KK\nKK"},
                "f2": {"block": "..\n.."},
                "strip": {
                    "type": "strip",
                    "frames": ["f1", "f2"],
                    "save": "strip.png",
                },
            },
        }
        spec_file = _write_spec(tmp_path, data)
        results = render_spec(spec_file, dry_run=True)
        strip_sprite = results["strip"]
        # 2 frames of 2x2 → 4x2
        assert strip_sprite.size == (4, 2)

    def test_grid(self, tmp_path: Path):
        data = {
            "palette": {".": "transparent", "K": "black"},
            "sprites": {
                "a": {"block": "KK\nKK"},
                "b": {"block": "..\n.."},
                "sheet": {
                    "type": "grid",
                    "sprites": {"a": "a", "b": "b"},
                    "columns": 2,
                },
            },
        }
        spec_file = _write_spec(tmp_path, data)
        results = render_spec(spec_file, dry_run=True)
        sheet_sprite = results["sheet"]
        # 2 sprites in 2 columns, each 2x2 → 4x2
        assert sheet_sprite.size == (4, 2)

    def test_grid_with_padding(self, tmp_path: Path):
        data = {
            "palette": {".": "transparent", "K": "black"},
            "sprites": {
                "a": {"block": "KK\nKK"},
                "b": {"block": "..\n.."},
                "sheet": {
                    "type": "grid",
                    "sprites": {"a": "a", "b": "b"},
                    "columns": 2,
                    "padding": 1,
                },
            },
        }
        spec_file = _write_spec(tmp_path, data)
        results = render_spec(spec_file, dry_run=True)
        sheet_sprite = results["sheet"]
        # 2 sprites in 2 columns, each 2x2, padding 1 → 5x2
        assert sheet_sprite.size == (5, 2)


# ---------------------------------------------------------------------------
# TileMap spec
# ---------------------------------------------------------------------------


class TestTileMapSpec:
    def test_tilemap(self, tmp_path: Path):
        data = {
            "palette": {"g": "#00FF00", "w": "#0000FF"},
            "sprites": {
                "grass": {"block": "gg\ngg"},
                "water": {"block": "ww\nww"},
                "map": {
                    "type": "tilemap",
                    "tileset": {"g": "grass", "w": "water"},
                    "grid": "ggww\nwwgg",
                },
            },
        }
        spec_file = _write_spec(tmp_path, data)
        results = render_spec(spec_file, dry_run=True)
        map_sprite = results["map"]
        # 4x2 tiles of 2x2 each → 8x4
        assert map_sprite.size == (8, 4)


# ---------------------------------------------------------------------------
# Preset palette
# ---------------------------------------------------------------------------


class TestPresetPalette:
    def test_preset_palette(self, tmp_path: Path):
        # pico8 preset auto-assigns single-char keys
        data = {
            "preset": "pico8",
            "sprites": {
                "dot": {"block": "01\n10"}
            },
        }
        spec_file = _write_spec(tmp_path, data)
        results = render_spec(spec_file, dry_run=True)
        assert results["dot"].size == (2, 2)


# ---------------------------------------------------------------------------
# Effects
# ---------------------------------------------------------------------------


class TestEffects:
    def test_outline(self, tmp_path: Path):
        data = {
            "palette": {".": "transparent", "K": "black"},
            "sprites": {
                "dot": {
                    "block": "K",
                    "outline": True,
                }
            },
        }
        spec_file = _write_spec(tmp_path, data)
        results = render_spec(spec_file, dry_run=True)
        # 1x1 with thin outline → 3x3
        assert results["dot"].size == (3, 3)

    def test_shadow(self, tmp_path: Path):
        data = {
            "palette": {".": "transparent", "K": "black"},
            "sprites": {
                "dot": {
                    "block": "K",
                    "shadow": True,
                }
            },
        }
        spec_file = _write_spec(tmp_path, data)
        results = render_spec(spec_file, dry_run=True)
        # 1x1 with shadow offset (1,1) → 2x2
        assert results["dot"].size == (2, 2)

    def test_outline_config(self, tmp_path: Path):
        data = {
            "palette": {".": "transparent", "K": "black"},
            "sprites": {
                "dot": {
                    "block": "K",
                    "outline": {"color": "#FF0000", "style": "thick"},
                }
            },
        }
        spec_file = _write_spec(tmp_path, data)
        results = render_spec(spec_file, dry_run=True)
        assert results["dot"].size == (3, 3)


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------


class TestErrors:
    def test_missing_palette(self, tmp_path: Path):
        data = {"sprites": {"dot": {"block": "K"}}}
        spec_file = _write_spec(tmp_path, data)
        with pytest.raises(SpecError, match="palette"):
            load_spec(spec_file)

    def test_missing_sprites(self, tmp_path: Path):
        data = {"palette": {".": "transparent"}}
        spec_file = _write_spec(tmp_path, data)
        with pytest.raises(SpecError, match="sprites"):
            load_spec(spec_file)

    def test_undefined_reference(self, tmp_path: Path):
        data = {
            "palette": {".": "transparent"},
            "sprites": {
                "strip": {
                    "type": "strip",
                    "frames": ["nonexistent"],
                }
            },
        }
        spec_file = _write_spec(tmp_path, data)
        spec = load_spec(spec_file)
        with pytest.raises(SpecError, match="not defined"):
            spec.render()

    def test_unknown_type(self, tmp_path: Path):
        data = {
            "palette": {".": "transparent"},
            "sprites": {
                "bad": {"type": "unknown_type", "block": "."}
            },
        }
        spec_file = _write_spec(tmp_path, data)
        spec = load_spec(spec_file)
        with pytest.raises(SpecError, match="Unknown sprite type"):
            spec.render()

    def test_missing_block_field(self, tmp_path: Path):
        data = {
            "palette": {".": "transparent"},
            "sprites": {
                "bad": {}
            },
        }
        spec_file = _write_spec(tmp_path, data)
        spec = load_spec(spec_file)
        with pytest.raises(SpecError, match="block"):
            spec.render()

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_spec("/nonexistent/spec.yaml")

    def test_invalid_palette_key(self, tmp_path: Path):
        data = {
            "palette": {"ab": "#000000"},
            "sprites": {"dot": {"block": "a"}},
        }
        spec_file = _write_spec(tmp_path, data)
        with pytest.raises(SpecError, match="1 character"):
            load_spec(spec_file)


# ---------------------------------------------------------------------------
# Dry-run and --only
# ---------------------------------------------------------------------------


class TestOptions:
    def test_dry_run_no_files(self, tmp_path: Path):
        data = {
            "palette": {".": "transparent", "K": "black"},
            "sprites": {
                "dot": {"block": "K", "save": "out/dot.png"}
            },
        }
        spec_file = _write_spec(tmp_path, data)
        results = render_spec(spec_file, dry_run=True)
        assert "dot" in results
        assert not (tmp_path / "out" / "dot.png").exists()

    def test_only_filter(self, tmp_path: Path):
        data = {
            "palette": {".": "transparent", "K": "black"},
            "sprites": {
                "a": {"block": "K"},
                "b": {"block": "."},
            },
        }
        spec_file = _write_spec(tmp_path, data)
        results = render_spec(spec_file, dry_run=True, only={"a"})
        assert "a" in results
        assert "b" not in results

    def test_only_with_dependency(self, tmp_path: Path):
        """--only on a strip should still render its frame dependencies."""
        data = {
            "palette": {".": "transparent", "K": "black"},
            "sprites": {
                "f1": {"block": "K"},
                "strip": {
                    "type": "strip",
                    "frames": ["f1"],
                },
            },
        }
        spec_file = _write_spec(tmp_path, data)
        results = render_spec(spec_file, dry_run=True, only={"strip"})
        assert "strip" in results
        # f1 is rendered as a dependency but included in results
        # because _ensure_rendered adds it
        assert results["strip"].size == (1, 1)


# ---------------------------------------------------------------------------
# Layers type
# ---------------------------------------------------------------------------


class TestLayers:
    def test_layers_simple(self, tmp_path: Path):
        data = {
            "palette": {".": "transparent", "K": "black", "r": "#FF0000"},
            "sprites": {
                "bg": {"block": "KK\nKK"},
                "fg": {"block": "r.\n.r"},
                "comp": {
                    "type": "layers",
                    "layers": [
                        {"sprite": "bg", "name": "background"},
                        {"sprite": "fg", "name": "foreground", "opacity": 1.0},
                    ],
                },
            },
        }
        spec_file = _write_spec(tmp_path, data)
        results = render_spec(spec_file, dry_run=True)
        comp = results["comp"]
        assert comp.size == (2, 2)
        # top-left should be red (fg on top of bg)
        assert comp.get_pixel(0, 0) == (255, 0, 0, 255)
        # top-right should be black (bg showing through transparent fg)
        assert comp.get_pixel(1, 0) == BLACK

    def test_layers_string_ref(self, tmp_path: Path):
        data = {
            "palette": {"K": "black"},
            "sprites": {
                "bg": {"block": "KK\nKK"},
                "comp": {
                    "type": "layers",
                    "layers": ["bg"],
                },
            },
        }
        spec_file = _write_spec(tmp_path, data)
        results = render_spec(spec_file, dry_run=True)
        assert results["comp"].size == (2, 2)
