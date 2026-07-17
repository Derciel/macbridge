"""Sincronizacao do projeto local -> Mac remoto.

Usa o backend para copiar diretorios (rsync quando disponivel no Mac,
scp/tar como fallback). Ignora .git, node_modules, build artifacts.

Opcionalmente mantem um *cache de dependencias*: os diretorios pesados
(Pods, .build, Carthage, vendor) so sao reenviados quando os manifestos
de dependencia mudam (Podfile.lock, Package.resolved, etc). Isso evita
transferir centenas de MB a cada build.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from macbridge.backends.base import CACHE_MARKER

IGNORE = [
    ".git", "node_modules", ".build", "build", "DerivedData",
    ".macbridge", "__pycache__", ".DS_Store", "Pods",
]

# Diretorios de dependencias que sao candidatos a cache (nao sao enviados
# de novo se o fingerprint dos manifestos nao mudar).
DEP_CACHE_DIRS = ["Pods", ".build", "Carthage", "vendor"]

# Manifestos/lockfiles que definem o conteudo das dependencias. Se qualquer
# um mudar, o cache e invalidado e os diretorios sao reenviados.
DEP_MANIFESTS = [
    "Podfile", "Podfile.lock",
    "Package.swift", "Package.resolved",
    "Cartfile", "Cartfile.resolved",
    "Gemfile.lock",
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


def deps_fingerprint(root: Path) -> str:
    """Calcula um hash curto dos manifestos de dependencia do projeto.

    Retorna '' se o projeto nao tiver nenhum manifesto de dependencia
    (logo, nao ha cache de deps para manter).
    """
    h = hashlib.sha1()
    found = False
    for name in DEP_MANIFESTS:
        p = root / name
        if p.is_file():
            found = True
            h.update(name.encode())
            h.update(p.read_bytes())
    return h.hexdigest()[:16] if found else ""


def sync(backend, local_root: str, remote_path: str) -> None:
    """Copia o projeto local para o Mac remoto (recursivo).

    Se o projeto tiver dependencias com manifestos reconhecidos e o hash
    destes ja estiver gravado no Mac (cache hit), os diretorios de cache
    (Pods/.build/etc) sao excluidos do envio. Caso contrario, envia tudo
    e atualiza o cache remoto.
    """
    root = Path(local_root)
    if not root.exists():
        raise FileNotFoundError(f"Pasta do projeto nao existe: {root}")

    files = project_files(root)
    print(f"[sync] {len(files)} arquivo(s) serao enviados para {remote_path}")

    fingerprint = deps_fingerprint(root)
    exclude = []
    if fingerprint:
        cached = backend.cache_get(remote_path)
        if cached == fingerprint:
            exclude = DEP_CACHE_DIRS
            print(f"[sync] cache de deps HIT ({fingerprint}) -> "
                  f"pulando {', '.join(exclude)}")
        else:
            print(f"[sync] cache de deps MISS -> enviando deps e "
                  f"atualizando cache ({fingerprint})")

    backend.copy(str(root), remote_path, exclude=exclude)

    if fingerprint:
        backend.cache_put(remote_path, fingerprint)
