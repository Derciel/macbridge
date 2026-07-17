"""Contrato de um backend remoto (Mac)."""
from __future__ import annotations

from typing import Tuple


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

    def copy(self, local: str, remote: str) -> None:
        """Copia arquivo/diretorio local -> remoto (recursivo)."""
        raise NotImplementedError

    def pull(self, remote: str, local: str) -> None:
        """Copia arquivo remoto -> local (baixa artefato pro Windows)."""
        raise NotImplementedError

    def status(self) -> dict:
        """Informacoes do Mac remoto: xcode, swift, arch, disk."""
        raise NotImplementedError
