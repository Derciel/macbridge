"""Configuracao do macbridge.

O macbridge usa duas camadas de configuracao:
  1. Global: ~/.macbridge/config.json  (credenciais do Mac remoto)
  2. Local:  ./.macbridge.json          (caminhos do projeto atual)

A config local sobrescreve a global quando ambas existem.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

GLOBAL_DIR = Path.home() / ".macbridge"
GLOBAL_CONFIG = GLOBAL_DIR / "config.json"
LOCAL_CONFIG = Path.cwd() / ".macbridge.json"


def default_config() -> Dict[str, Any]:
    return {
        "backend": "mock",          # "mock" (simulado) ou "ssh" (Mac real)
        "host": "",                 # endereco do Mac (ex.: 10.0.0.5 ou user@mac)
        "user": "",                 # usuario ssh no Mac
        "port": 22,                 # porta ssh
        "ssh_key": "",              # caminho da chave privada (opcional)
        "remote_path": "~/builds",  # onde o projeto e copiado no Mac
        "project_name": "",         # nome do app / scheme
        "build_mode": "xcodebuild", # "xcodebuild" ou "swift"
        "scheme": "",               # scheme do xcodebuild (vazio = project_name)
        "configuration": "Release", # Debug ou Release
    }


def load_config() -> Dict[str, Any]:
    cfg = default_config()
    if GLOBAL_CONFIG.exists():
        cfg.update(_read(GLOBAL_CONFIG))
    if LOCAL_CONFIG.exists():
        cfg.update(_read(LOCAL_CONFIG))
    return cfg


def save_global(cfg: Dict[str, Any]) -> None:
    GLOBAL_DIR.mkdir(parents=True, exist_ok=True)
    GLOBAL_CONFIG.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")


def save_local(cfg: Dict[str, Any]) -> None:
    LOCAL_CONFIG.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")


def _read(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError(f"Config invalida em {path}: {exc}") from exc
