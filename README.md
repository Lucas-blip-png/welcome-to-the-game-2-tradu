# Tradução PT-BR — Welcome to the Game 2

Projeto de **tradução para português do Brasil** do jogo *Welcome to the Game 2*
(Reflect Studios), feito editando os arquivos do jogo (Unity).

> ⚠️ **Status:** estrutura e ferramentas prontas (Fase 0). Falta enviar os
> arquivos do jogo para começar a extração dos textos. Veja
> [`game_files/LEIA-ME.md`](game_files/LEIA-ME.md).

## Como funciona

O jogo guarda texto em dois lugares:

1. **`Assembly-CSharp.dll`** (em `WTTG2_Data/Managed/`) — a maior parte dos
   textos (diálogos, e-mails, mensagens, rótulos). Editado com o tool C#
   (`tools/dll-tool`, Mono.Cecil) ou pelo **dnSpy**.
2. **Arquivos `*.assets`** (UI Text, TextMeshPro, `TextAsset`) e as **fontes**.
   Editados com **UnityPy** (`tools/extract_assets.py` / `tools/inject_assets.py`).

O fluxo é: **extrair** os textos para catálogos JSON → **traduzir** os JSON →
**injetar** de volta → gerar os arquivos modificados em `build/` → testar no jogo.

## O que NÃO entra no Git

Os **arquivos originais do jogo são protegidos por copyright** e ficam fora do
versionamento (`.gitignore`). Versionamos apenas: os **textos da tradução**
(`translations/pt-BR/*.json`), as **ferramentas** e a **documentação** — que é a
forma correta de publicar uma tradução de fã. Você precisa ter o jogo (Steam)
para extrair e aplicar a tradução.

## Estrutura

```
translations/pt-BR/   catálogos de tradução (dll.json, assets.json) + glossário
tools/                scripts de extração/injeção (Python + tool C# da DLL)
docs/GUIA.md          passo a passo completo
game_files/           arquivos ORIGINAIS do jogo (você coloca aqui; ignorado no Git)
build/                arquivos modificados gerados (ignorado no Git)
```

## Início rápido

```bash
# 1. dependências Python
pip install -r tools/requirements.txt

# 2. coloque os arquivos do jogo em game_files/  (ver game_files/LEIA-ME.md)

# 3. extrair os textos
python tools/extract_dll.py            # -> translations/pt-BR/dll.json
python tools/extract_assets.py         # -> translations/pt-BR/assets.json
python tools/check_glyphs.py           # confere se as fontes têm acentos PT-BR

# 4. traduzir: preencher o campo "traducao" nos .json
python tools/stats.py                  # acompanha o progresso

# 5. injetar e gerar os arquivos modificados em build/
python tools/inject_assets.py
#    DLL: ver docs/GUIA.md (tool C# Mono.Cecil ou dnSpy)
```

Passo a passo detalhado em [`docs/GUIA.md`](docs/GUIA.md).

## Aviso legal

Tradução de fã, sem fins lucrativos. *Welcome to the Game 2* é © Reflect Studios.
Este repositório **não** distribui arquivos do jogo — apenas textos traduzidos e
ferramentas. Use somente com uma cópia legítima do jogo.
