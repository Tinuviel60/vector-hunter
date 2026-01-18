import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from vect_hunt.engine.resources.loaders.font__loader import FontLoader


# --------------------
# Setup
# --------------------
@pytest.fixture(autouse=True)
def clear_cache():
    FontLoader._cache.clear()
    yield
    FontLoader._cache.clear()


@pytest.fixture
def mock_pygame():
    with patch("vect_hunt.engine.resources.loaders.font__loader.pygame") as mock_pg:
        mock_pg.font.Font.return_value = MagicMock()
        yield mock_pg


# --------------------
# Chargement basique
# --------------------
def test_load_basic(mock_pygame):
    with patch.object(
        FontLoader, "_resolve_path", return_value=Path("/fake/arial.ttf")
    ):
        font = FontLoader.load("arial.ttf", 24)

    mock_pygame.font.Font.assert_called_once_with(Path("/fake/arial.ttf"), 24)
    assert font is not None


def test_load_file_not_found():
    with patch.object(FontLoader, "_resolve_path", side_effect=FileNotFoundError()):
        with pytest.raises(FileNotFoundError):
            FontLoader.load("nonexistent.ttf", 24)


# --------------------
# Cache
# --------------------
def test_cache_works(mock_pygame):
    with patch.object(
        FontLoader, "_resolve_path", return_value=Path("/fake/arial.ttf")
    ):
        font1 = FontLoader.load("arial.ttf", 24)
        font2 = FontLoader.load("arial.ttf", 24)

    assert mock_pygame.font.Font.call_count == 1
    assert font1 is font2


def test_different_sizes_separate_cache(mock_pygame):
    mock_pygame.font.Font.side_effect = [MagicMock(name="24"), MagicMock(name="48")]

    with patch.object(
        FontLoader, "_resolve_path", return_value=Path("/fake/arial.ttf")
    ):
        font_24 = FontLoader.load("arial.ttf", 24)
        font_48 = FontLoader.load("arial.ttf", 48)

    assert mock_pygame.font.Font.call_count == 2
    assert font_24 is not font_48


def test_different_files_separate_cache(mock_pygame):
    mock_pygame.font.Font.side_effect = [
        MagicMock(name="arial"),
        MagicMock(name="times"),
    ]

    with patch.object(FontLoader, "_resolve_path") as resolve_path:
        resolve_path.side_effect = [
            Path("/fake/arial.ttf"),
            Path("/fake/times.ttf"),
        ]
        font1 = FontLoader.load("arial.ttf", 24)
        font2 = FontLoader.load("times.ttf", 24)

    assert mock_pygame.font.Font.call_count == 2
    assert font1 is not font2
