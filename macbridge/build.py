"""Logica de build remoto no Mac.

Apos o build, empacota o .app em um .ipa (xcrun / zip) e devolve o caminho
remoto do artefato para que o CLI possa baixa-lo de volta pro Windows.
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


def package_command(cfg: dict, remote_path: str) -> str:
    """Monta o comando que empacota o .app num .ipa no Mac remoto.

    O xcodebuild deixa o .app em <remote_path>/build/<scheme>.app; aqui
    zipamos em <remote_path>/<scheme>.ipa para facilitar o pull.
    """
    project_name = cfg.get("project_name") or "App"
    scheme = cfg.get("scheme") or project_name
    ipa = f"{remote_path}/{scheme}.ipa"
    app = f"{remote_path}/build/{scheme}.app"
    # -FS mantem symlinks; -r recursivo. Silencioso (-q).
    return f"cd {remote_path} && rm -f {scheme}.ipa && zip -r -q {ipa} {app}"


def artifact_path(cfg: dict, remote_path: str) -> str:
    """Caminho remoto do .ipa gerado pelo build."""
    project_name = cfg.get("project_name") or "App"
    scheme = cfg.get("scheme") or project_name
    return f"{remote_path}/{scheme}.ipa"


def run_build(backend: Backend, cfg: dict, remote_path: str) -> dict:
    """Executa o build remoto e devolve o resultado estruturado.

    Retorna tambem o caminho remoto do .ipa (artifact) para ser baixado.
    """
    cmd = build_command(cfg, remote_path)
    print(f"[build] rodando no Mac: {cmd}")
    rc, out, err = backend.run(cmd)

    artifact = None
    if rc == 0:
        pkg = package_command(cfg, remote_path)
        print(f"[build] empacotando .ipa no Mac: {pkg}")
        prc, pout, perr = backend.run(pkg)
        out += "\n" + pout
        err += perr
        if prc == 0:
            artifact = artifact_path(cfg, remote_path)
        else:
            rc = prc  # falha no empacotamento propaga o erro
            print(f"[build] AVISO: falha ao empacotar .ipa (rc={prc})")

    return {
        "exit_code": rc,
        "stdout": out,
        "stderr": err,
        "command": cmd,
        "artifact": artifact,
    }
