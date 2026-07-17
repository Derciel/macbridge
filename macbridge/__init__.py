"""macbridge - ponte Windows -> Mac para build iOS sem Xcode no Windows.

A ideia: voce escreve codigo no Windows (VS Code / Zed / editor qualquer),
o macbridge copia o projeto para um Mac (nuvem ou local) e roda o build
(xcodebuild ou swift build) la, devolvendo os logs e o artefato.
"""

__version__ = "0.1.0"
