"""Backend simulado (mock) para desenvolvimento no Windows sem um Mac real.

Permite validar todo o fluxo do macbridge offline. O "build" e simulado
com um log realista de xcodebuild, e o artefato e um .ipa de mentira.
"""
from __future__ import annotations

import os
import random
import time
from pathlib import Path
from typing import Tuple

from macbridge.backends.base import Backend


class MockBackend(Backend):
    """Simula um Mac remoto. Nao faz SSH de verdade."""

    def connect(self) -> None:
        print(f"[mock] conectando a Mac simulado: {self.cfg.get('host') or 'localhost'}")

    def run(self, cmd: str) -> Tuple[int, str, str]:
        print(f"[mock] $ {cmd}")
        # Simula latencia de rede
        time.sleep(0.2)

        # Deteccao por substring: 'xcodebuild' mas nao 'swift ... xcodebuild'
        if "xcodebuild" in cmd and "swift" not in cmd.split("xcodebuild", 1)[-1][:6]:
            return self._fake_xcodebuild(cmd)
        if "swift build" in cmd:
            return self._fake_swift_build(cmd)
        if cmd.startswith("xcodebuild -version"):
            return 0, "Xcode 15.4\nBuild version 15F31d", ""
        if cmd.startswith("swift --version"):
            return 0, "swift-driver version: 1.10.1 Apple Swift version 5.10", ""
        if cmd.startswith("uname -m"):
            return 0, "arm64", ""
        if cmd.startswith("df -h"):
            return 0, "/dev/disk1s1  460Gi  120Gi  340Gi  26%  /", ""
        if cmd.startswith("mkdir -p"):
            return 0, "", ""
        return 0, f"[mock] ok: {cmd}", ""

    def copy(self, local: str, remote: str) -> None:
        src = Path(local)
        print(f"[mock] copiando {src} -> {remote}")
        time.sleep(0.1)

    def status(self) -> dict:
        return {
            "backend": "mock",
            "xcode": "15.4 (Build 15F31d)",
            "swift": "5.10",
            "arch": "arm64",
            "disk_free": "340 GiB",
            "host": self.cfg.get("host") or "localhost",
        }

    # --- internos -------------------------------------------------------
    def _fake_xcodebuild(self, cmd: str) -> Tuple[int, str, str]:
        scheme = self.cfg.get("scheme") or self.cfg.get("project_name") or "App"
        lines = [
            "Prepare packages",
            "ComputeTargetPrebuildModuleDependencies",
            "CreateBuildRequest",
            "Build target App of project App.xcodeproj",
            "Compile Swift Module 'App' (12 sources)",
            "Link Storyboards",
            "ProcessInfoPlistFile Info.plist",
            "CodeSign App.app",
            f"** BUILD SUCCEEDED ** [{random.randint(8, 40)}s]",
        ]
        out = "\n".join(lines)
        # gera artefato fake
        artifact = Path.home() / ".macbridge" / "artifacts" / f"{scheme}.ipa"
        artifact.parent.mkdir(parents=True, exist_ok=True)
        artifact.write_bytes(b"PK\x03\x04 FAKE IPA ARTIFACT")
        out += f"\n[artifact] {artifact}"
        return 0, out, ""

    def _fake_swift_build(self, cmd: str) -> Tuple[int, str, str]:
        lines = [
            "Building for production...",
            "[12/12] Linking App",
            "Build complete! (3.21s)",
        ]
        return 0, "\n".join(lines), ""
