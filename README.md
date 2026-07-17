# MacBridge

**Ponte Windows → Mac para build de apps iOS sem precisar do Xcode no Windows.**

Você escreve o código no Windows (VS Code, Zed, editor qualquer), o MacBridge
copia o projeto para um Mac (nuvem ou local) e roda o build (`xcodebuild` /
`swift build`) lá, devolvendo os logs e o artefato para o Windows.

> ⚠️ **Realidade honesta:** o Xcode não roda no Windows e não é portável. O
> MacBridge **não** é um "Xcode para Windows" — é um *fluxo de build remoto*.
> O compilador pesado continua rodando em um Mac (mesmo que alugado na nuvem).
> Isso respeita o EULA da Apple e as leis de engenharia reversa.

---

## Por que existe
Todo dev no Windows que quer fazer app iOS esbarra no mesmo problemas:
precisa de um Mac pra compilar e publicar. O MacBridge automatiza a ponte
Windows ↔ Mac, que hoje é manual e dolorosa.

## Como funciona
```
[ Windows: voce escreve ]  --sync-->  [ Mac: xcodebuild/swift build ]  --log/ipa-->  [ Windows ]
```

Backends:
- `mock` — simula um Mac (desenvolvimento offline, valida o fluxo sem custo)
- `ssh`  — Mac real (nuvem tipo MacinCloud/AWS EC2 Mac, ou Mac na mesma rede)

## Instalação (Windows, via Git Bash / MSYS)
```bash
cd macbridge
python -m pip install -e .
```

## Uso
```bash
# 1. checa ferramentas no PATH (ssh, scp, python, rsync)
macbridge doctor

# 2. configura (modo mock primeiro, pra testar)
macbridge init --backend mock --project MeuApp

# 3. status do "Mac"
macbridge status

# 4. sincroniza + build
macbridge build

# com Mac real (SSH):
macbridge init --backend ssh --host 10.0.0.5 --user dev --project MeuApp
macbridge build --configuration Release
```

## Roadmap (open-source, contribuições bem-vindas)
- [ ] integração com VS Code / Zed (extensão que chama `macbridge build`)
- [ ] download do `.ipa` de volta pro Windows
- [ ] cache de dependências (não reenviar Pods/SPM a cada build)
- [ ] upload direto pra TestFlight (via `xcrun altool`)
- [ ] suporte a `fastlane` no Mac remoto

## Licença
MIT. Não é produto Apple, não é afiliado, não usa marca nem binários da Apple.
