// MacBridge VS Code extension
// Abre uma Webview com a UI de chat e executa o CLI `macbridge` de verdade,
// via child_process. Nenhuma dependencia externa em runtime (apenas vscode + node).

const vscode = require("vscode");
const cp = require("child_process");
const path = require("path");
const fs = require("fs");

function getUiHtml() {
  // pega o index.html da UI do pacote (relativo a esta extensao -> ../ui/index.html)
  const uiPath = path.join(__dirname, "..", "ui", "index.html");
  if (fs.existsSync(uiPath)) return fs.readFileSync(uiPath, "utf8");
  return "<h1>MacBridge UI nao encontrada</h1>";
}

function runCli(args) {
  return new Promise((resolve) => {
    const py = process.platform === "win32" ? "python" : "python3";
    cp.execFile(py, ["-m", "macbridge", ...args], { timeout: 300000 },
      (err, stdout, stderr) => {
        resolve({
          ok: !err,
          exit_code: err && err.code ? err.code : 0,
          stdout: stdout.toString(),
          stderr: stderr.toString(),
        });
      });
  });
}

function activate(context) {
  const disposable = vscode.commands.registerCommand("macbridge.open", () => {
    const panel = vscode.window.createWebviewPanel(
      "macbridge", "MacBridge · Sala de Build",
      vscode.ViewColumn.One, { enableScripts: true, retainContextWhenHidden: true }
    );
    panel.webview.html = getUiHtml();

    // a UI envia {type:'run', args:[...]} pela webview; respondemos com a saida real
    panel.webview.onDidReceiveMessage(async (msg) => {
      if (msg && msg.type === "run") {
        const out = await runCli(msg.args || []);
        panel.webview.postMessage({ type: "result", id: msg.id, ...out });
      }
    }, undefined, context.subscriptions);
  });

  context.subscriptions.push(disposable);
}

function deactivate() {}

module.exports = { activate, deactivate };
