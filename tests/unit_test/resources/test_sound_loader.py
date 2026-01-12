import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from vect_hunt.resources.sound_loader import SoundLoader


# --------------------
# Setup
# --------------------
@pytest.fixture(autouse=True)
def clear_cache():
    SoundLoader._cache.clear()
    yield
    SoundLoader._cache.clear()


@pytest.fixture
def mock_pygame():
    with patch("vect_hunt.resources.sound_loader.pygame") as mock_pg:
        mock_pg.mixer.Sound.return_value = MagicMock()
        yield mock_pg


# --------------------
# Chargement basique
# --------------------
def test_load_basic(mock_pygame):
    with patch("vect_hunt.resources.sound_loader.SOUNDS_DIR", Path("/fake")):
        sound = SoundLoader.load("jump.wav")
    
    mock_pygame.mixer.Sound.assert_called_once_with(Path("/fake/jump.wav"))
    assert sound is not None


def test_load_file_not_found():
    with patch("vect_hunt.resources.sound_loader.SOUNDS_DIR", Path("/fake")):
        with patch("vect_hunt.resources.sound_loader.pygame") as mock_pg:
            mock_pg.mixer.Sound.side_effect = FileNotFoundError()
            
            with pytest.raises(FileNotFoundError):
                SoundLoader.load("nonexistent.wav")


# --------------------
# Cache
# --------------------
def test_cache_works(mock_pygame):
    with patch("vect_hunt.resources.sound_loader.SOUNDS_DIR", Path("/fake")):
        sound1 = SoundLoader.load("jump.wav")
        sound2 = SoundLoader.load("jump.wav")
    
    assert mock_pygame.mixer.Sound.call_count == 1
    assert sound1 is sound2


def test_different_sounds_separate_cache(mock_pygame):
    mock_pygame.mixer.Sound.side_effect = [MagicMock(name="s1"), MagicMock(name="s2")]
    
    with patch("vect_hunt.resources.sound_loader.SOUNDS_DIR", Path("/fake")):
        sound1 = SoundLoader.load("jump.wav")
        sound2 = SoundLoader.load("shoot.wav")
    
    assert mock_pygame.mixer.Sound.call_count == 2
    assert sound1 is not sound2
