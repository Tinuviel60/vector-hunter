import json
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest
from vect_hunt.engine.resources.loaders.data_loader import DataLoader


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
        with patch.object(
            DataLoader, "_resolve_path", return_value=Path("/fake/test.json")
        ):
            result = DataLoader.load_json("test.json")

    assert result == sample_data


def test_load_json_file_not_found():
    with patch.object(DataLoader, "_resolve_path", side_effect=FileNotFoundError):
        with pytest.raises(FileNotFoundError):
            DataLoader.load_json("nonexistent.json")


def test_load_json_invalid_json():
    with patch("builtins.open", mock_open(read_data="{ invalid")):
        with patch.object(
            DataLoader, "_resolve_path", return_value=Path("/fake/invalid.json")
        ):
            with pytest.raises(json.JSONDecodeError):
                DataLoader.load_json("invalid.json")


# --------------------
# Cache
# --------------------
def test_cache_works(sample_data):
    json_content = json.dumps(sample_data)
    mock_file = mock_open(read_data=json_content)

    with patch("builtins.open", mock_file):
        with patch.object(
            DataLoader, "_resolve_path", return_value=Path("/fake/test.json")
        ):
            result1 = DataLoader.load_json("test.json")
            result2 = DataLoader.load_json("test.json")

    assert mock_file.call_count == 1
    assert result1 == result2


def test_clear_cache_works(sample_data):
    json_content = json.dumps(sample_data)
    mock_file = mock_open(read_data=json_content)

    with patch("builtins.open", mock_file):
        with patch.object(
            DataLoader, "_resolve_path", return_value=Path("/fake/test.json")
        ):
            DataLoader.load_json("test.json")
            DataLoader.clear_cache()
            DataLoader.load_json("test.json")

    assert mock_file.call_count == 2
