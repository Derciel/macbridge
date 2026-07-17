"""Sincronizacao do projeto local -> Mac remoto.

Usa o backend para copiar diretorios (rsync quando disponivel no Mac,
scp -r como fallback). Ignora .git, node_modules, build artifacts.
"""
from __future__ import annotations

import fnmatch
from pathlib import Path

IGNORE = [
    ".git", "node_modules", ".build", "build", "DerivedData",
    ".macbridge", "__pycache__", ".DS_Store", "Pods",
]


def _should_ignore(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    for part in rel.parts:
        if part in IGNORE:
            return True
    return False


def project_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for p in root.rglob("*"):
        if p.is_file() and not _should_ignore(p, root):
            files.append(p)
    return files


def sync(backend, local_root: str, remote_path: str) -> None:
    """Copia o projeto local para o Mac remoto (recursivo)."""
    root = Path(local_root)
    if not root.exists():
        raise FileNotFoundError(f"Pasta do projeto nao existe: {root}")

    files = project_files(root)
    print(f"[sync] {len(files)} arquivo(s) serao enviados para {remote_path}")

    # O backend.MockBackend/ SshBackend implementam copy(); passamos a pasta
    # raiz e deixamos o backend decidir recursao (scp -r / mock).
    backend.copy(str(root), remote_path)
