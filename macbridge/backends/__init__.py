"""Backends remotos do macbridge.

Um backend representa um "Mac" onde o build acontece.
"""
from macbridge.backends.base import Backend
from macbridge.backends.mock import MockBackend
from macbridge.backends.ssh import SshBackend

__all__ = ["Backend", "MockBackend", "SshBackend"]


def create_backend(cfg: dict) -> Backend:
    """Fabrica de backend a partir da configuracao."""
    name = (cfg.get("backend") or "mock").lower()
    if name == "mock":
        return MockBackend(cfg)
    if name == "ssh":
        return SshBackend(cfg)
    raise ValueError(f"Backend desconhecido: {name!r} (use 'mock' ou 'ssh')")
