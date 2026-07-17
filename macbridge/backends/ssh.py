"""Backend SSH real para um Mac (nuvem ou local na mesma rede).

Requer `ssh` e `scp` no PATH do Windows (Git Bash ja traz os dois).
Opcional: chave SSH configurada para acesso sem senha.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Tuple

from macbridge.backends.base import Backend, CACHE_MARKER


def _shell_quote(s: str) -> str:
    """Escapa uma string para uso seguro dentro de aspas simples no shell."""
    return "'" + s.replace("'", "'\\''") + "'"


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

    def copy(self, local: str, remote: str, exclude: list = None) -> None:
        """Copia local -> remoto preservando a estrutura.

        Usa rsync quando disponivel (suporta --exclude direto). Caso
        contrario, faz o fallback para um pipe `tar` via ssh, que tambem
        permite excluir diretorios de cache de dependencias sem precisar
        do rsync instalado no Windows.
        """
        if shutil.which("rsync") is not None:
            self._copy_rsync(local, remote, exclude or [])
            return
        self._copy_tar(local, remote, exclude or [])

    def _copy_rsync(self, local: str, remote: str, exclude: list) -> None:
        rsync = ["rsync", "-az", "-e",
                 f"ssh -p {self._port} -o BatchMode=yes"
                 + (f" -i {self._key}" if self._key else "")]
        for name in exclude:
            rsync += ["--exclude", name]
        rsync += [str(local) + "/", f"{self._target()}:{remote}"]
        proc = subprocess.run(rsync, capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(f"Falha ao copiar {local}: {proc.stderr.strip()}")
        print(f"[rsync] {local} -> {self._target()}:{remote}"
              + (f" (excluindo: {', '.join(exclude)})" if exclude else ""))

    def _copy_tar(self, local: str, remote: str, exclude: list) -> None:
        # tar local -> ssh tar extract no remoto (exclui diretorios de cache)
        tar = ["tar", "cf", "-", "-C", str(local)]
        for name in exclude:
            tar += ["--exclude", f"./{name}"]
        tar += ["."]
        ssh = self._ssh_base() + [f"mkdir -p {remote} && tar xf - -C {remote}"]
        proc = subprocess.run(tar, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc.returncode != 0:
            raise RuntimeError(f"Falha ao empacotar {local}: {proc.stderr.decode().strip()}")
        sproc = subprocess.run(ssh, input=proc.stdout, capture_output=True, text=True)
        if sproc.returncode != 0:
            raise RuntimeError(f"Falha ao copiar {local}: {sproc.stderr.strip()}")
        print(f"[scp/tar] {local} -> {self._target()}:{remote}"
              + (f" (excluindo: {', '.join(exclude)})" if exclude else ""))

    def cache_get(self, remote_path: str) -> str:
        marker = f"{remote_path}/{CACHE_MARKER}"
        rc, out, _ = self.run(f"cat {marker} 2>/dev/null || true")
        return out.strip() if rc == 0 else ""

    def cache_put(self, remote_path: str, fingerprint: str) -> None:
        marker = f"{remote_path}/{CACHE_MARKER}"
        self.run(f"mkdir -p {remote_path} && printf '%s' {_shell_quote(fingerprint)} > {marker}")

    def pull(self, remote: str, local: str) -> None:
        if shutil.which("scp") is None:
            raise RuntimeError("'scp' nao encontrado no PATH.")
        dst = Path(local)
        dst.parent.mkdir(parents=True, exist_ok=True)
        scp = ["scp", "-P", str(self._port), "-o", "BatchMode=yes"]
        if self._key:
            scp += ["-i", str(self._key)]
        scp += [f"{self._target()}:{remote}", str(dst)]
        proc = subprocess.run(scp, capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(f"Falha ao baixar {remote}: {proc.stderr.strip()}")
        print(f"[scp] {self._target()}:{remote} -> {dst}")

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
