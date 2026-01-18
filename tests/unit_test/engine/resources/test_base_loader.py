import pytest
from pathlib import Path

from vect_hunt.engine.resources.loaders.data_loader import DataLoader


@pytest.mark.parametrize(
    "relative_path, setup, max_bytes, expect_ok",
    [
        pytest.param("test.json", "file_ok", 1024, True, id="valid_path"),
        pytest.param("/etc/passwd", None, 1024, False, id="reject_absolute"),
        pytest.param("../secret.json", None, 1024, False, id="reject_dotdot"),
        pytest.param(
            "test.txt",
            "file_txt",
            1024,
            False,
            id="reject_extension",
        ),
        pytest.param("reject_size", "big.json", "file_big", 1, False, id="reject_size"),
        pytest.param(
            "link.json",
            "file_symlink",
            1024,
            False,
            id="reject_symlink",
        ),
    ],
)
def test_resolve_path_security(
    relative_path: str,
    setup: str | None,
    max_bytes: int,
    expect_ok: bool,
    tmp_path: Path,
) -> None:
    if setup == "file_ok":
        (tmp_path / "test.json").write_text("{}", encoding="utf-8")
    elif setup == "file_txt":
        (tmp_path / "test.txt").write_text("x", encoding="utf-8")
    elif setup == "file_big":
        (tmp_path / "big.json").write_text("ab", encoding="utf-8")
    elif setup == "file_symlink":
        target = tmp_path / "target.json"
        target.write_text("{}", encoding="utf-8")
        link = tmp_path / "link.json"
        try:
            link.symlink_to(target)
        except OSError:
            pytest.skip("Symlinks not supported on this platform.")

    if expect_ok:
        resolved = DataLoader._resolve_path(
            tmp_path,
            relative_path,
            allowed_extensions={".json"},
            max_bytes=max_bytes,
        )
        assert resolved == (tmp_path / relative_path).resolve()
        return

    with pytest.raises(ValueError):
        DataLoader._resolve_path(
            tmp_path,
            relative_path,
            allowed_extensions={".json"},
            max_bytes=max_bytes,
        )