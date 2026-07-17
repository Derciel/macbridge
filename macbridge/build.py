"""Logica de build remoto no Mac.
"""
from __future__ import annotations

from pathlib import Path

from macbridge.backends.base import Backend


def build_command(cfg: dict, remote_path: str) -> str:
    """Monta o comando de build de acordo com o modo."""
    mode = (cfg.get("build_mode") or "xcodebuild").lower()
    project_name = cfg.get("project_name") or "App"
    scheme = cfg.get("scheme") or project_name
    configuration = cfg.get("configuration") or "Release"

    if mode == "swift":
        return f"cd {remote_path} && swift build -c release"

    # xcodebuild (padrao)
    return (
        f"cd {remote_path} && xcodebuild "
        f"-scheme {scheme} -configuration {configuration} "
        f"-destination 'generic/platform=iOS' build"
    )


def run_build(backend: Backend, cfg: dict, remote_path: str) -> dict:
    """Executa o build remoto e devolve o resultado estruturado."""
    cmd = build_command(cfg, remote_path)
    print(f"[build] rodando no Mac: {cmd}")
    rc, out, err = backend.run(cmd)
    return {"exit_code": rc, "stdout": out, "stderr": err, "command": cmd}
