# MacBridge — extensão VS Code

Ponte **Windows → Mac** para build de apps iOS direto do editor. Escreva no Windows, compile no Mac (nuvem ou local) e receba o `.ipa` de volta — sem Xcode no Windows.

## O que faz
- Comando **`MacBridge: Abrir sala de build`** abre uma Webview com a UI de chat.
- A UI executa o CLI `macbridge` de verdade (build / status / sync / doctor / init) e mostra o log do Mac remoto.
- Funciona com o backend `mock` (simulado, sem Mac) ou `ssh` (Mac real / alugado).

## Pré-requisitos
- Python 3.10+ com o `macbridge` instalado (`pip install macbridge` ou `pip install -e .` no repo).
- Ferramentas `ssh`/`scp` no PATH (já vêm com o Git Bash no Windows).

## Uso
1. Instale a extensão (`.vsix` ou marketplace).
2. `Ctrl+Shift+P` → **MacBridge: Abrir sala de build**.
3. Use os atalhos ou digite comandos em linguagem natural.

## Legal
Não é um clone do Xcode. É uma ponte de build que usa a toolchain aberta da Apple em um Mac legítimo (nuvem ou seu). Respeita o EULA da Apple.
