"""Servidor HTTP local do macbridge: serve a UI e expoe /api/run.

Stdlib puro (http.server). A UI (ui/index.html) e uma SPA que chama /api/run,
que executa o proprio CLI do macbridge e devolve stdout/stderr/exit_code.
Se o servidor nao estiver rodando, a UI cai num modo mock (texto simulado).
"""
from __future__ import annotations

import json
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

UI_DIR = Path(__file__).resolve().parent.parent / "ui"


def run_cli(args: list[str]) -> dict:
    """Executa `macbridge <args>` e devolve a saida real."""
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "macbridge", *args],
            capture_output=True, text=True, timeout=300,
        )
        return {
            "ok": proc.returncode == 0,
            "exit_code": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "args": args,
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "exit_code": -1, "stdout": "", "stderr": "timeout (300s)", "args": args}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "exit_code": -1, "stdout": "", "stderr": str(exc), "args": args}


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body: bytes, ctype: str = "application/json") -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        if self.path in ("/", "/index.html", "/ui"):
            html = (UI_DIR / "index.html").read_bytes()
            return self._send(200, html, "text/html; charset=utf-8")
        if self.path == "/health":
            return self._send(200, b'{"ok":true}', "application/json")
        # arquivos estaticos da ui/
        cand = (UI_DIR / self.path.lstrip("/")).resolve()
        if str(cand).startswith(str(UI_DIR.resolve())) and cand.is_file():
            ctype = "text/html; charset=utf-8" if cand.suffix == ".html" else "text/plain"
            return self._send(200, cand.read_bytes(), ctype)
        self._send(404, b'{"error":"not found"}')

    def do_POST(self):  # noqa: N802
        if self.path == "/api/run":
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b"{}"
            try:
                payload = json.loads(raw or b"{}")
            except json.JSONDecodeError:
                payload = {}
            args = payload.get("args", [])
            if not isinstance(args, list):
                args = [str(args)]
            result = run_cli([str(a) for a in args])
            return self._send(200, json.dumps(result, ensure_ascii=False).encode("utf-8"))
        self._send(404, b'{"error":"not found"}')

    def log_message(self, *a):  # silencia logs do servidor
        pass


def serve(host: str = "127.0.0.1", port: int = 8765) -> None:
    httpd = ThreadingHTTPServer((host, port), Handler)
    url = f"http://{host}:{port}/"
    print(f"[ui] MacBridge UI em {url}")
    print(f"[ui] Abra no navegador. Ctrl+C para parar.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[ui] encerrando.")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    serve()
