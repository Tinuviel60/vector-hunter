import pytest
from vect_hunt.engine.core import RenderOps


# -------------------
# hex_to_rgb / rgb_to_hex
# -------------------
@pytest.mark.parametrize(
    "hex_color, expected",
    [
        ("#FF0000", (255, 0, 0)),
        ("00FF00", (0, 255, 0)),
        ("0000FF", (0, 0, 255)),
        ("123456", (18, 52, 86)),
    ],
)
def test_hex_to_rgb_valid(hex_color, expected):
    assert RenderOps.hex_to_rgb(hex_color) == expected


@pytest.mark.parametrize("invalid_hex", ["#FFF", "GGHHII", "12345", "ZZZZZZ"])
def test_hex_to_rgb_invalid_raises(invalid_hex):
    with pytest.raises(ValueError):
        RenderOps.hex_to_rgb(invalid_hex)


def test_rgb_to_hex():
    assert RenderOps.rgb_to_hex((255, 128, 0)) == "#FF8000"


# -------------------
# hex_to_rgba / rgba_to_hex
# -------------------
def test_hex_to_rgba_rgb_default_alpha():
    assert RenderOps.hex_to_rgba("#FF8000") == (255, 128, 0, 255)


def test_hex_to_rgba_with_alpha():
    assert RenderOps.hex_to_rgba("#FF800080") == (255, 128, 0, 128)


def test_rgba_to_hex():
    assert RenderOps.rgba_to_hex((255, 128, 0, 128)) == "#FF800080"


# -------------------
# lerp_color / blend_colors
# -------------------
def test_lerp_color():
    assert RenderOps.lerp_color((0, 0, 0), (255, 255, 255), 0.5) == (128, 128, 128)


def test_blend_colors_alpha():
    assert RenderOps.blend_colors((200, 0, 0), (0, 0, 200), "alpha", 0.5) == (
        100,
        0,
        100,
    )


def test_blend_colors_add():
    assert RenderOps.blend_colors((250, 10, 10), (10, 250, 10), "add") == (
        255,
        255,
        20,
    )


# -------------------
# adjust_brightness / adjust_contrast / tint / with_alpha
# -------------------
def test_adjust_brightness():
    assert RenderOps.adjust_brightness((100, 100, 100), 1.5) == (150, 150, 150)


def test_adjust_contrast():
    assert RenderOps.adjust_contrast((128, 128, 128), 1.2) == (128, 128, 128)


def test_tint():
    assert RenderOps.tint((200, 200, 200), (255, 0, 0), 0.5) == (228, 100, 100)


def test_with_alpha():
    assert RenderOps.with_alpha((255, 0, 0), 128) == (255, 0, 0, 128)
    assert RenderOps.with_alpha((255, 0, 0, 64), 128) == (255, 0, 0, 128)
