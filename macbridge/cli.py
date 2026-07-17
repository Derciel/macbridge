"""CLI do macbridge."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from macbridge import __version__
from macbridge import config as cfg_mod
from macbridge.backends import create_backend
from macbridge import sync as sync_mod
from macbridge import build as build_mod


def _print_status(backend) -> None:
    s = backend.status()
    print("=== MacBridge Status ===")
    for k, v in s.items():
        print(f"  {k}: {v}")


def _pull_artifact(backend, cfg: dict, remote_path: str) -> str:
    """Baixa o .ipa do Mac de volta pro Windows (~/.macbridge/artifacts)."""
    artifact = build_mod.artifact_path(cfg, remote_path)
    local_dir = Path.home() / ".macbridge" / "artifacts"
    local_dir.mkdir(parents=True, exist_ok=True)
    project_name = cfg.get("project_name") or "App"
    scheme = cfg.get("scheme") or project_name
    local_ipa = local_dir / f"{scheme}.ipa"
    print(f"[pull] baixando artefato {artifact} -> {local_ipa}")
    backend.pull(artifact, str(local_ipa))
    print(f"[pull] pronto: {local_ipa} ({local_ipa.stat().st_size} bytes)")
    return str(local_ipa)


def cmd_init(args) -> int:
    cfg = cfg_mod.default_config()
    if args.backend:
        cfg["backend"] = args.backend
    if args.host:
        cfg["host"] = args.host
    if args.user:
        cfg["user"] = args.user
    cfg["project_name"] = args.project or Path.cwd().name
    if args.global_cfg:
        cfg_mod.save_global(cfg)
        print(f"[init] config global salva em {cfg_mod.GLOBAL_CONFIG}")
    else:
        cfg_mod.save_local(cfg)
        print(f"[init] config local salva em .macbridge.json")
    return 0


def cmd_status(args) -> int:
    cfg = cfg_mod.load_config()
    backend = create_backend(cfg)
    backend.connect()
    _print_status(backend)
    return 0


def cmd_doctor(args) -> int:
    print("=== MacBridge Doctor ===")
    ok = True
    # rsync e opcional (fallback para scp -r); nao deve quebrar o doctor.
    required = ("ssh", "scp", "python")
    optional = ("rsync",)
    import shutil
    for tool in required:
        present = shutil.which(tool)
        state = "OK" if present else "FALTANDO"
        if not present:
            ok = False
        print(f"  {tool}: {state} ({present or 'n/a'})")
    for tool in optional:
        present = shutil.which(tool)
        state = "OK" if present else "opcional (usando scp -r)"
        print(f"  {tool}: {state} ({present or 'n/a'})")
    cfg = cfg_mod.load_config()
    print(f"  backend atual: {cfg.get('backend')}")
    print(f"  projeto: {cfg.get('project_name') or '(nao definido)'}")
    print("\nResultado:", "tudo pronto" if ok else "falta ferramenta no PATH")
    return 0 if ok else 1


def cmd_sync(args) -> int:
    cfg = cfg_mod.load_config()
    backend = create_backend(cfg)
    backend.connect()
    remote = cfg.get("remote_path") or "~/builds"
    sync_mod.sync(backend, cfg.get("local_root", "."), remote)
    print("[sync] pronto")
    return 0


def cmd_build(args) -> int:
    cfg = cfg_mod.load_config()
    cfg["project_name"] = args.project or cfg.get("project_name") or Path.cwd().name
    if args.configuration:
        cfg["configuration"] = args.configuration
    if args.mode:
        cfg["build_mode"] = args.mode
    backend = create_backend(cfg)
    backend.connect()
    remote = cfg.get("remote_path") or "~/builds"
    # sincroniza antes de buildar (a menos que --no-sync)
    if not args.no_sync:
        sync_mod.sync(backend, ".", remote)
    result = build_mod.run_build(backend, cfg, remote)
    print("\n--- LOG DO BUILD (Mac) ---")
    print(result["stdout"])
    if result["stderr"]:
        print("--- ERROS ---")
        print(result["stderr"])
    print(f"\nExit code: {result['exit_code']}")
    if result["exit_code"] == 0 and result.get("artifact") and not args.no_pull:
        _pull_artifact(backend, cfg, remote)
    return result["exit_code"]


def cmd_pull(args) -> int:
    cfg = cfg_mod.load_config()
    cfg["project_name"] = args.project or cfg.get("project_name") or Path.cwd().name
    backend = create_backend(cfg)
    backend.connect()
    remote = cfg.get("remote_path") or "~/builds"
    _pull_artifact(backend, cfg, remote)
    return 0


def cmd_ui(args) -> int:
    from macbridge import server as server_mod
    if args.open:
        import webbrowser
        webbrowser.open(f"http://{args.host}:{args.port}/")
    server_mod.serve(host=args.host, port=args.port)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="macbridge",
        description="Ponte Windows -> Mac para build iOS sem Xcode no Windows.",
    )
    p.add_argument("--version", action="version", version=f"macbridge {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    pi = sub.add_parser("init", help="configura backend/projeto")
    pi.add_argument("--backend", choices=["mock", "ssh"])
    pi.add_argument("--host")
    pi.add_argument("--user")
    pi.add_argument("--project")
    pi.add_argument("--global", dest="global_cfg", action="store_true",
                    help="salva na config global (~/.macbridge)")
    pi.set_defaults(func=cmd_init)

    sub.add_parser("status", help="mostra info do Mac remoto").set_defaults(func=cmd_status)
    sub.add_parser("doctor", help="verifica ferramentas no PATH").set_defaults(func=cmd_doctor)

    ps = sub.add_parser("sync", help="envia o projeto para o Mac")
    ps.set_defaults(func=cmd_sync)

    pb = sub.add_parser("build", help="sincroniza + build no Mac")
    pb.add_argument("--project")
    pb.add_argument("--configuration", choices=["Debug", "Release"])
    pb.add_argument("--mode", choices=["xcodebuild", "swift"])
    pb.add_argument("--no-sync", action="store_true")
    pb.add_argument("--no-pull", action="store_true",
                    help="nao baixar o .ipa de volta pro Windows apos o build")
    pb.set_defaults(func=cmd_build)

    pp = sub.add_parser("pull", help="baixa o .ipa do Mac para o Windows")
    pp.add_argument("--project")
    pp.set_defaults(func=cmd_pull)

    pu = sub.add_parser("ui", help="sobe a interface web local (macbridge ui)")
    pu.add_argument("--host", default="127.0.0.1")
    pu.add_argument("--port", type=int, default=8765)
    pu.add_argument("--open", action="store_true",
                    help="tenta abrir no navegador padrao")
    pu.set_defaults(func=cmd_ui)

    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (RuntimeError, ValueError, FileNotFoundError) as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
