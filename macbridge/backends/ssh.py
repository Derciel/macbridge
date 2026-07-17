"""Backend SSH real para um Mac (nuvem ou local na mesma rede).

Requer `ssh` e `scp` no PATH do Windows (Git Bash ja traz os dois).
Opcional: chave SSH configurada para acesso sem senha.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Tuple

from macbridge.backends.base import Backend


class SshBackend(Backend):
    """Executa comandos via `ssh` e copia arquivos via `scp`."""

    def __init__(self, cfg: dict) -> None:
        super().__init__(cfg)
        self._host = cfg.get("host") or ""
        self._user = cfg.get("user") or ""
        self._port = int(cfg.get("port") or 22)
        self._key = cfg.get("ssh_key") or ""

    # --- helpers --------------------------------------------------------
    def _target(self) -> str:
        if self._user:
            return f"{self._user}@{self._host}"
        return self._host

    def _ssh_base(self) -> list[str]:
        cmd = ["ssh", "-p", str(self._port), "-o", "BatchMode=yes",
               "-o", "ConnectTimeout=10"]
        if self._key:
            cmd += ["-i", str(self._key)]
        if shutil.which("ssh") is None:
            raise RuntimeError("'ssh' nao encontrado no PATH. Instale Git Bash ou OpenSSH.")
        cmd.append(self._target())
        return cmd

    def connect(self) -> None:
        if shutil.which("ssh") is None:
            raise RuntimeError("'ssh' nao encontrado no PATH.")
        proc = subprocess.run(
            self._ssh_base() + ["echo", "ok"],
            capture_output=True, text=True,
        )
        if proc.returncode != 0:
            raise RuntimeError(
                f"Falha ao conectar em {self._target()}: {proc.stderr.strip()}"
            )
        print(f"[ssh] conectado a {self._target()}")

    def run(self, cmd: str) -> Tuple[int, str, str]:
        proc = subprocess.run(
            self._ssh_base() + [cmd],
            capture_output=True, text=True,
        )
        return proc.returncode, proc.stdout, proc.stderr

    def copy(self, local: str, remote: str) -> None:
        if shutil.which("scp") is None:
            raise RuntimeError("'scp' nao encontrado no PATH.")
        scp = ["scp", "-P", str(self._port), "-r", "-o", "BatchMode=yes"]
        if self._key:
            scp += ["-i", str(self._key)]
        scp += [str(local), f"{self._target()}:{remote}"]
        proc = subprocess.run(scp, capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(f"Falha ao copiar {local}: {proc.stderr.strip()}")
        print(f"[scp] {local} -> {self._target()}:{remote}")

    def status(self) -> dict:
        rc, out, err = self.run("xcodebuild -version; swift --version; uname -m; df -h /")
        if rc != 0:
            return {"backend": "ssh", "error": err.strip() or "sem resposta"}
        parts = out.splitlines()
        return {
            "backend": "ssh",
            "xcode": parts[0] if parts else "?",
            "swift": parts[2] if len(parts) > 2 else "?",
            "arch": parts[-2] if len(parts) > 3 else "?",
            "host": self._target(),
        }
