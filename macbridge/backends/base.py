"""Contrato de um backend remoto (Mac)."""
from __future__ import annotations

from typing import Tuple

# Marcador (arquivo) gravado no Mac remoto para registrar o fingerprint
# das dependencias ja enviadas. Permite pular o re-envio de Pods/.build/etc.
CACHE_MARKER = ".macbridge_deps.cache"


class Backend:
    """Representa um Mac onde o build iOS acontece.

    Subclasses concretas implementam a comunicacao real (SSH) ou
    simulada (Mock).
    """

    def __init__(self, cfg: dict) -> None:
        self.cfg = cfg

    def connect(self) -> None:
        """Verifica conectividade. Levanta excecao se nao consegurar."""
        raise NotImplementedError

    def run(self, cmd: str) -> Tuple[int, str, str]:
        """Executa um comando remoto.

        Retorna (exit_code, stdout, stderr).
        """
        raise NotImplementedError

    def copy(self, local: str, remote: str, exclude: list = None) -> None:
        """Copia arquivo/diretorio local -> remoto (recursivo).

        `exclude` e uma lista de nomes de diretorios de primeiro nivel que
        devem ser ignorados (usado para pular o cache de dependencias).
        """
        raise NotImplementedError

    def pull(self, remote: str, local: str) -> None:
        """Copia arquivo remoto -> local (baixa artefato pro Windows)."""
        raise NotImplementedError

    def cache_get(self, remote_path: str) -> str:
        """Le o fingerprint de dependencias gravado no Mac ('' se ausente)."""
        raise NotImplementedError

    def cache_put(self, remote_path: str, fingerprint: str) -> None:
        """Grava o fingerprint de dependencias no Mac remoto."""
        raise NotImplementedError

    def status(self) -> dict:
        """Informacoes do Mac remoto: xcode, swift, arch, disk."""
        raise NotImplementedError
