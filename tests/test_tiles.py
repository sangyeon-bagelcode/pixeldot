"""Tests for TileSet and TileMap."""

import pytest
import pixeldot as px


def make_tile(rows):
    """Helper: create a small tile from string rows."""
    p = px.Palette({'.': px.TRANSPARENT, 'K': px.BLACK, 'r': '#FF0000', 'g': '#00FF00'})
    return px.StringCanvas(p).render(rows)


@pytest.fixture
def grass_tile():
    return make_tile(["gg", "gg"])


@pytest.fixture
def water_tile():
    return make_tile(["..", ".."])


@pytest.fixture
def rock_tile():
    return make_tile(["KK", "KK"])


@pytest.fixture
def tileset(grass_tile, water_tile, rock_tile):
    return px.TileSet({
        'g': grass_tile,
        'w': water_tile,
        'r': rock_tile,
    })


class TestTileSet:
    def test_creation(self, tileset):
        assert tileset.tile_size == (2, 2)
        assert len(tileset) == 3

    def test_auto_tile_size(self, grass_tile, water_tile):
        ts = px.TileSet({'g': grass_tile, 'w': water_tile})
        assert ts.tile_size == (2, 2)

    def test_explicit_tile_size(self, grass_tile):
        ts = px.TileSet({'g': grass_tile}, tile_size=(2, 2))
        assert ts.tile_size == (2, 2)

    def test_mismatched_size_raises(self):
        small = make_tile(["K"])
        big = make_tile(["KK", "KK"])
        with pytest.raises(ValueError, match="size"):
            px.TileSet({'s': small, 'b': big})

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="at least one"):
            px.TileSet({})

    def test_multi_char_key_raises(self, grass_tile):
        with pytest.raises(ValueError, match="1 character"):
            px.TileSet({'gg': grass_tile})

    def test_getitem(self, tileset, grass_tile):
        assert tileset['g'] == grass_tile

    def test_getitem_missing_raises(self, tileset):
        with pytest.raises(KeyError, match="not found"):
            tileset['x']

    def test_contains(self, tileset):
        assert 'g' in tileset
        assert 'x' not in tileset

    def test_keys(self, tileset):
        assert sorted(tileset.keys()) == ['g', 'r', 'w']

    def test_repr(self, tileset):
        assert "3 tiles" in repr(tileset)
        assert "2x2" in repr(tileset)


class TestTileMap:
    def test_simple_grid(self, tileset):
        tm = px.TileMap(tileset, ['gg', 'rr'])
        assert tm.grid_size == (2, 2)
        assert tm.pixel_size == (4, 4)

    def test_block_string_grid(self, tileset):
        tm = px.TileMap(tileset, '''
            ggg
            grg
            ggg
        ''')
        assert tm.grid_size == (3, 3)
        assert tm.pixel_size == (6, 6)

    def test_to_sprite(self, tileset):
        tm = px.TileMap(tileset, ['gw', 'rg'])
        sprite = tm.to_sprite()
        assert sprite.size == (4, 4)
        # top-left tile is grass (green)
        assert sprite.get_pixel(0, 0) == (0, 255, 0, 255)
        assert sprite.get_pixel(1, 1) == (0, 255, 0, 255)
        # top-right tile is water (transparent)
        assert sprite.get_pixel(2, 0) == px.TRANSPARENT
        # bottom-left tile is rock (black)
        assert sprite.get_pixel(0, 2) == px.BLACK

    def test_single_tile(self, tileset):
        tm = px.TileMap(tileset, ['g'])
        sprite = tm.to_sprite()
        assert sprite.size == (2, 2)
        assert sprite.get_pixel(0, 0) == (0, 255, 0, 255)

    def test_unknown_tile_raises(self, tileset):
        with pytest.raises(KeyError, match="not in TileSet"):
            px.TileMap(tileset, ['gx'])

    def test_inconsistent_row_length_raises(self, tileset):
        with pytest.raises(ValueError, match="chars"):
            px.TileMap(tileset, ['gg', 'g'])

    def test_empty_grid_raises(self, tileset):
        with pytest.raises(ValueError, match="empty"):
            px.TileMap(tileset, '')

    def test_repr(self, tileset):
        tm = px.TileMap(tileset, ['gg', 'rr'])
        r = repr(tm)
        assert "2x2 tiles" in r
        assert "4x4px" in r

    def test_large_map(self, tileset):
        """Test that a larger map renders correctly."""
        grid = ['grgw'] * 4
        tm = px.TileMap(tileset, grid)
        assert tm.grid_size == (4, 4)
        assert tm.pixel_size == (8, 8)
        sprite = tm.to_sprite()
        assert sprite.size == (8, 8)
