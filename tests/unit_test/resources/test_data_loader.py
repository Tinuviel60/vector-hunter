import json
import pytest
from pathlib import Path
from unittest.mock import mock_open, patch
from vect_hunt.resources.data_loader import DataLoader


# --------------------
# Setup
# --------------------
@pytest.fixture(autouse=True)
def clear_cache():
    DataLoader.clear_cache()
    yield
    DataLoader.clear_cache()


@pytest.fixture
def sample_data():
    return {"player": {"health": 100}, "enemies": [{"type": "goblin"}]}


# --------------------
# Chargement basique
# --------------------
def test_load_json_basic(sample_data):
    json_content = json.dumps(sample_data)

    with patch("builtins.open", mock_open(read_data=json_content)):
        with patch("vect_hunt.resources.data_loader.DATA_DIR", Path("/fake")):
            result = DataLoader.load_json("test.json")

    assert result == sample_data


def test_load_json_file_not_found():
    with patch("vect_hunt.resources.data_loader.DATA_DIR", Path("/fake")):
        with pytest.raises(FileNotFoundError):
            DataLoader.load_json("nonexistent.json")


def test_load_json_invalid_json():
    with patch("builtins.open", mock_open(read_data="{ invalid")):
        with patch("vect_hunt.resources.data_loader.DATA_DIR", Path("/fake")):
            with pytest.raises(json.JSONDecodeError):
                DataLoader.load_json("invalid.json")


# --------------------
# Cache
# --------------------
def test_cache_works(sample_data):
    json_content = json.dumps(sample_data)
    mock_file = mock_open(read_data=json_content)

    with patch("builtins.open", mock_file):
        with patch("vect_hunt.resources.data_loader.DATA_DIR", Path("/fake")):
            result1 = DataLoader.load_json("test.json")
            result2 = DataLoader.load_json("test.json")

    assert mock_file.call_count == 1
    assert result1 == result2


def test_cache_disabled(sample_data):
    json_content = json.dumps(sample_data)
    mock_file = mock_open(read_data=json_content)

    with patch("builtins.open", mock_file):
        with patch("vect_hunt.resources.data_loader.DATA_DIR", Path("/fake")):
            DataLoader.load_json("test.json", use_cache=False)
            DataLoader.load_json("test.json", use_cache=False)

    assert mock_file.call_count == 2


def test_reload_ignores_cache(sample_data):
    json_content = json.dumps(sample_data)
    mock_file = mock_open(read_data=json_content)

    with patch("builtins.open", mock_file):
        with patch("vect_hunt.resources.data_loader.DATA_DIR", Path("/fake")):
            DataLoader.load_json("test.json")
            DataLoader.reload("test.json")

    assert mock_file.call_count == 2


def test_clear_cache_works(sample_data):
    json_content = json.dumps(sample_data)
    mock_file = mock_open(read_data=json_content)

    with patch("builtins.open", mock_file):
        with patch("vect_hunt.resources.data_loader.DATA_DIR", Path("/fake")):
            DataLoader.load_json("test.json")
            DataLoader.clear_cache()
            DataLoader.load_json("test.json")

    assert mock_file.call_count == 2
