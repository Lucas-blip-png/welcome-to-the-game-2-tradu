# Coloque aqui os arquivos do jogo

Esta pasta guarda os **arquivos originais** do *Welcome to the Game 2* que serão
lidos pelas ferramentas. **Nada aqui é enviado ao Git** (está no `.gitignore`),
porque são arquivos com copyright.

## Onde encontrar (Steam)

```
C:\Program Files (x86)\Steam\steamapps\common\Welcome to the Game II\WTTG2_Data\
```

(Para achar a pasta: Steam → clique direito no jogo → *Gerenciar* →
*Procurar arquivos locais*.)

## O que enviar — e em que ordem

**1º — o mais importante (textos principais):**

- `WTTG2_Data\Managed\Assembly-CSharp.dll`

**2º — UI, textos de tela e fontes:**

- `WTTG2_Data\resources.assets` (e o `resources.assets.resS`, se existir)
- `WTTG2_Data\sharedassets0.assets`, `sharedassets1.assets`, … (e seus `.resS`)
- `WTTG2_Data\level0`, `level1`, … (arquivos de cena, sem extensão)
- `WTTG2_Data\globalgamemanagers` e `globalgamemanagers.assets`

> Os arquivos `.resS` são "pares" dos `.assets` — se enviar um `.assets`, mande
> junto o `.resS` de mesmo nome (quando existir).

Arquivos grandes (centenas de MB) podem ficar para depois: comece pelo
`Assembly-CSharp.dll` e pelos `.assets` menores. As ferramentas avisam se
faltar algo.

## Como colocar aqui

Copie os arquivos para dentro desta pasta (`game_files/`) mantendo os nomes
originais. Não precisa recriar a estrutura de subpastas do jogo.

Depois, rode (a partir da raiz do repositório):

```bash
python tools/extract_dll.py
python tools/extract_assets.py
python tools/check_glyphs.py
```
