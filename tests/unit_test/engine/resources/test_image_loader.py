import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from vect_hunt.engine.resources.loaders.image_loader import ImageLoader


# --------------------
# Setup
# --------------------
@pytest.fixture(autouse=True)
def clear_cache():
    ImageLoader._cache.clear()
    yield
    ImageLoader._cache.clear()


@pytest.fixture
def mock_pygame():
    with patch("vect_hunt.engine.resources.loaders.image_loader.pygame") as mock_pg:
        mock_surface = MagicMock()
        mock_surface.convert_alpha.return_value = mock_surface
        mock_surface.get_size.return_value = (64, 64)
        mock_pg.image.load.return_value = mock_surface
        yield mock_pg


# --------------------
# Chargement basique
# --------------------
def test_load_basic(mock_pygame):
    with patch.object(
        ImageLoader, "_resolve_path", return_value=Path("/fake/player.png")
    ):
        surface = ImageLoader.load("player.png")

    mock_pygame.image.load.assert_called_once_with(Path("/fake/player.png"))
    assert surface is not None


def test_load_file_not_found():
    with patch.object(ImageLoader, "_resolve_path", side_effect=FileNotFoundError()):
        with pytest.raises(FileNotFoundError):
            ImageLoader.load("nonexistent.png")


# --------------------
# Cache
# --------------------
def test_cache_works(mock_pygame):
    with patch.object(
        ImageLoader, "_resolve_path", return_value=Path("/fake/player.png")
    ):
        surf1 = ImageLoader.load("player.png")
        surf2 = ImageLoader.load("player.png")

    assert mock_pygame.image.load.call_count == 1
    assert surf1 is surf2


def test_different_images_separate_cache(mock_pygame):
    def create_surface(name):
        mock = MagicMock(name=name)
        mock.convert_alpha.return_value = mock
        mock.get_size.return_value = (64, 64)
        return mock

    mock_pygame.image.load.side_effect = [create_surface("p1"), create_surface("p2")]

    with patch.object(ImageLoader, "_resolve_path") as resolve_path:
        resolve_path.side_effect = [
            Path("/fake/player.png"),
            Path("/fake/enemy.png"),
        ]
        surf1 = ImageLoader.load("player.png")
        surf2 = ImageLoader.load("enemy.png")

    assert mock_pygame.image.load.call_count == 2
    assert surf1 is not surf2


# --------------------
# convert_alpha
# --------------------
def test_convert_alpha_called():
    with patch.object(
        ImageLoader, "_resolve_path", return_value=Path("/fake/test.png")
    ):
        with patch("vect_hunt.engine.resources.loaders.image_loader.pygame") as mock_pg:
            original = MagicMock()
            converted = MagicMock()
            converted.get_size.return_value = (64, 64)
            original.convert_alpha.return_value = converted
            mock_pg.image.load.return_value = original

            result = ImageLoader.load("test.png")

    original.convert_alpha.assert_called_once()
    assert result is converted
