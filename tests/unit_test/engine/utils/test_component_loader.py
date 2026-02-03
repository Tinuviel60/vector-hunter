import os

from vect_hunt.engine.utils import component_loader


def test_find_py_files_recursively(monkeypatch, tmp_path):
    root = tmp_path / "components"
    root.mkdir()
    (root / "a.py").write_text("x = 1", encoding="utf-8")
    (root / "__init__.py").write_text("", encoding="utf-8")

    results = component_loader._find_py_files_recursively(str(root))

    assert any(path.endswith("a.py") for _, path in results)


def test_load_all_components_imports_modules(monkeypatch, tmp_path):
    loaded = []

    def fake_import(name, path):
        loaded.append((name, path))
        return object()

    monkeypatch.setattr(component_loader, "_import_module_from_path", fake_import)
    monkeypatch.setattr(component_loader.os.path, "isdir", lambda p: True)
    monkeypatch.setattr(
        component_loader,
        "_find_py_files_recursively",
        lambda p: [("mod_a", os.path.join(p, "a.py"))],
    )

    component_loader.load_all_components([str(tmp_path)])

    assert loaded == [("mod_a", os.path.join(str(tmp_path), "a.py"))]
