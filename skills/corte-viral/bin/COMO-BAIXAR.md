# deep-filter (DeepFilterNet) · como baixar

O `deep-filter` é o programa de IA que limpa o ruído da voz (open source, licença MIT/Apache 2.0, projeto
https://github.com/Rikorose/DeepFilterNet). Ele não vem no pacote: o Claude baixa a versão certa na primeira instalação,
direto do GitHub oficial, release **v0.5.6**.

| Computador | Arquivo da release v0.5.6 | Salvar como |
| --- | --- | --- |
| Mac com chip Apple (M1, M2, M3, M4...) | `deep-filter-0.5.6-aarch64-apple-darwin` | `bin/deep-filter` |
| Mac com processador Intel | `deep-filter-0.5.6-x86_64-apple-darwin` | `bin/deep-filter` |
| Windows (64 bits) | `deep-filter-0.5.6-x86_64-pc-windows-msvc.exe` | `bin/deep-filter.exe` |
| Linux | `deep-filter-0.5.6-x86_64-unknown-linux-musl` | `bin/deep-filter` |

Endereço de cada arquivo: `https://github.com/Rikorose/DeepFilterNet/releases/download/v0.5.6/<arquivo>`

## Mac
```bash
cd ~/.claude/skills/corte-viral/bin
ARQ=deep-filter-0.5.6-$( [ "$(uname -m)" = arm64 ] && echo aarch64 || echo x86_64 )-apple-darwin
curl -L -o deep-filter "https://github.com/Rikorose/DeepFilterNet/releases/download/v0.5.6/$ARQ"
chmod +x deep-filter
xattr -d com.apple.quarantine deep-filter 2>/dev/null || true
./deep-filter --version      # deve mostrar: deep_filter 0.5.6
```

## Windows (PowerShell)
```powershell
cd $env:USERPROFILE\.claude\skills\corte-viral\bin
Invoke-WebRequest -Uri "https://github.com/Rikorose/DeepFilterNet/releases/download/v0.5.6/deep-filter-0.5.6-x86_64-pc-windows-msvc.exe" -OutFile deep-filter.exe
.\deep-filter.exe --version
```

Sem o `deep-filter`, a edição funciona do mesmo jeito: só pula a etapa de limpeza por IA (o `limpar_voz.sh` avisa e segue
com o resto do tratamento de voz).
