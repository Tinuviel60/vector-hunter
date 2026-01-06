#!/usr/bin/env python3
"""
Script de renommage du template.

Renomme :
- le nom du projet (repo / docs)
- le nom du module Python

Placeholders :
- vector-hunter
- vect_hunt
"""

from pathlib import Path
import re
import sys

OLD_PROJECT = "vector-hunter"
OLD_MODULE = "vect_hunt"

EXCLUDED_DIRS = {
    "venv",
    ".git",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
}


def is_valid_module_name(name: str) -> bool:
    """
    Vérifie que le nom est un identifiant Python valide.
    """
    return re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", name) is not None


def is_valid_project_name(name: str) -> bool:
    """
    Vérifie un nom de projet lisible (kebab-case recommandé).
    """
    return re.match(r"^[a-zA-Z0-9][a-zA-Z0-9\-]*$", name) is not None


def should_skip(path: Path) -> bool:
    """
    Indique si un chemin doit être ignoré.
    """
    return any(part in EXCLUDED_DIRS for part in path.parts)


def replace_in_file(path: Path, project_name: str, module_name: str) -> None:
    """
    Remplace les placeholders dans un fichier texte.
    """
    try:
        content = path.read_text(encoding="utf-8")
    except Exception:
        return

    updated = (
        content.replace(OLD_PROJECT, project_name)
               .replace(OLD_MODULE, module_name)
    )

    if updated != content:
        path.write_text(updated, encoding="utf-8")


def main() -> None:
    print("=== Project template initialization ===\n")

    project_name = input("Nom du projet (repo, kebab-case recommandé) : ").strip()
    module_name = input("Nom du module Python (snake_case) : ").strip()

    if not is_valid_project_name(project_name):
        print(f"Nom de projet invalide : {project_name}")
        sys.exit(1)

    if not is_valid_module_name(module_name):
        print(f"Nom de module invalide : {module_name}")
        sys.exit(1)

    root = Path.cwd()

    # 1. Remplacement dans les fichiers
    for path in root.rglob("*"):
        if path.is_file() and not should_skip(path):
            replace_in_file(path, project_name, module_name)

    # 2. Renommage du dossier source
    src_dir = root / "sources" / OLD_MODULE
    if src_dir.exists():
        src_dir.rename(root / "sources" / module_name)

    print("\n✔ Projet initialisé avec succès")
    print(f"  - Projet      : {project_name}")
    print(f"  - Module      : {module_name}")
    print("\nProchaines étapes recommandées :")
    print("- supprimer et recréer le venv")
    print("- pip install -e .")
    print("- vérifier python -m", module_name)


if __name__ == "__main__":
    main()
