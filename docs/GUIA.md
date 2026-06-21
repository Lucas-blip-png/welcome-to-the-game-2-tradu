# Guia completo — Traduzindo o Welcome to the Game 2 para PT-BR

Passo a passo do fluxo: **extrair → traduzir → injetar → testar**.

---

## 0. Pré-requisitos

- O jogo instalado (Steam) — você precisa de uma cópia legítima.
- **Python 3.10+** e as dependências:
  ```bash
  pip install -r tools/requirements.txt
  ```
- Para editar a DLL de forma automática: **.NET SDK 8+** (`dotnet`).
  Alternativa sem programar: **dnSpy** (Windows) — https://github.com/dnSpyEx/dnSpy
- (Recomendado) **backup** da pasta do jogo antes de qualquer substituição.

---

## 1. Enviar os arquivos do jogo

Copie os arquivos de `WTTG2_Data\` para a pasta `game_files/` deste repositório.
Veja a lista e a ordem em [`game_files/LEIA-ME.md`](../game_files/LEIA-ME.md).
Comece sempre pelo **`Assembly-CSharp.dll`**.

> Lembrete: `game_files/` é ignorado pelo Git — esses arquivos não são enviados
> ao repositório.

---

## 2. Extrair os textos

```bash
# Textos do código (a maior parte) -> translations/pt-BR/dll.json
python tools/extract_dll.py

# Textos de UI/assets -> translations/pt-BR/assets.json
python tools/extract_assets.py

# As fontes têm os acentos do PT-BR?
python tools/check_glyphs.py
```

Cada extrator **mescla** com o catálogo existente: rodar de novo **não apaga**
traduções já feitas (a chave é o `id` de cada entrada).

### Sobre o `check_glyphs.py` (importante)

Se aparecer `[FALTAM] ... á ã ç`, a fonte usada por aquele texto **não tem os
acentos** e eles virariam quadradinhos (□) no jogo. Soluções:

1. Ver se o texto usa outra fonte que já tenha os acentos.
2. **Expandir/regerar o atlas** da fonte (incluir a faixa Latin-1). Para fontes
   TextMeshPro isso é feito regenerando o *Font Asset*; para fontes dinâmicas
   (TTF embutido) normalmente os acentos já funcionam.
3. Último caso: evitar acentos só naquele rótulo específico.

Detectar isso **cedo** evita retrabalho na tradução inteira.

---

## 3. Traduzir

Abra os arquivos em `translations/pt-BR/` e preencha o campo **`traducao`** de
cada entrada (deixe `fonte` como está):

```json
{
  "id": "dll:1a2b3c4d5e6f",
  "fonte": "You have new mail.",
  "traducao": "Você tem uma nova mensagem.",
  "contexto": "EmailManager::CheckInbox"
}
```

Regras de ouro (ver também [`glossario.md`](../translations/pt-BR/glossario.md)):

- Preserve **placeholders/format**: `{0}`, `%s`, `\n`, tags `<color>`, `<b>`…
- Mantenha **nomes próprios** e nomes de programas/sites fictícios.
- Em **botões curtos**, use a forma mais enxuta (PT-BR estoura caixa fácil).

Acompanhe o progresso:

```bash
python tools/stats.py
```

> Dica: dá para editar os `.json` à mão, num editor, ou converter para planilha
> (CSV) e voltar — mantenha os campos `id` e `fonte` intactos.

---

## 4. Injetar as traduções

### 4a. Assets (UI, TextAsset) — UnityPy

```bash
python tools/inject_assets.py
```

Gera os arquivos modificados em `build/` (ex.: `build/resources.assets`).

### 4b. DLL — tool C# (Mono.Cecil), recomendado

```bash
cd tools/dll-tool
dotnet run -- inject ../../game_files/Assembly-CSharp.dll ../../translations/pt-BR/dll.json ../../build/Assembly-CSharp.dll
```

Gera `build/Assembly-CSharp.dll` já com as traduções aplicadas (o Cecil
recompõe a DLL com segurança — não precisa mexer em bytes na mão).

> O mesmo tool também extrai: `dotnet run -- extract <dll> <dll.json>`.

### 4c. DLL — alternativa manual com dnSpy (sem programar)

1. Abra `Assembly-CSharp.dll` no dnSpy.
2. Use a busca (Edit → Search) por uma frase em inglês do `dll.json`.
3. Clique direito no método → *Edit Method (C#)* → troque o texto pela
   `traducao` → *Compile* → *File → Save Module*.

Bom para ajustes pontuais; para muitas strings, prefira o tool C# (4b).

---

## 5. Instalar no jogo e testar

1. **Backup:** copie os originais (renomeie para `.bak`), ex.:
   `Assembly-CSharp.dll` → `Assembly-CSharp.dll.bak`.
2. Copie os arquivos de `build/` para os lugares correspondentes em
   `WTTG2_Data/` (a DLL vai em `WTTG2_Data/Managed/`).
3. Abra o jogo e percorra: menu principal, opções, e uma cena com bastante texto
   (ex.: caixa de e-mail / um site da deep web).

**Procure por:**

- ⬜ Quadradinhos no lugar de acentos → problema de **fonte** (volte ao passo 2).
- ✂️ Texto cortado/estourando caixa → **encurtar** a `traducao`.
- 🕳️ Texto ainda em inglês → faltou extrair/traduzir aquela string (pode estar
  num asset ou método ainda não coberto).
- 💥 Crash ao abrir → reverta para o `.bak` e revise a última mudança.

Anote o que achar e repita **3 → 4 → 5**.

---

## 6. Atualizações do jogo

Se o jogo for atualizado na Steam, os textos/offsets podem mudar. Basta
**re-extrair** (passo 2) sobre os novos arquivos: o catálogo mescla as novidades
e **preserva** o que você já traduziu (entradas novas vêm com `traducao` vazia).
Anote no `README`/PR a versão do jogo usada como alvo.

---

## Resumo dos comandos

```bash
pip install -r tools/requirements.txt        # uma vez
python tools/extract_dll.py                  # extrair DLL
python tools/extract_assets.py               # extrair assets
python tools/check_glyphs.py                 # checar fontes
python tools/stats.py                        # progresso
python tools/inject_assets.py                # injetar assets -> build/
# DLL -> build/ :
cd tools/dll-tool && dotnet run -- inject \
  ../../game_files/Assembly-CSharp.dll \
  ../../translations/pt-BR/dll.json \
  ../../build/Assembly-CSharp.dll
```
