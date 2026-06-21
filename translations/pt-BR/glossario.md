# Glossário e convenções — PT-BR

Padroniza termos para manter a tradução consistente. **Vamos preencher/ajustar
isto conforme os textos reais forem extraídos.**

## Convenções gerais

- **Tom:** informal-neutro (o jogo é sombrio/realista). Tratar o jogador por
  "você".
- **Não traduzir:** nomes próprios, nomes de personagens, nomes de sites/arquivos
  fictícios, comandos e nomes de programas dentro do jogo (a menos que claramente
  façam parte da narrativa).
- **Placeholders e formatação:** preserve exatamente `{0}`, `{1}`, `%s`, `\n`,
  `\t`, tags como `<color=...>`, `<b>`, etc. Traduza só o texto ao redor.
- **Comprimento:** PT-BR costuma ficar maior que o inglês. Em botões/rótulos
  curtos, prefira a forma mais enxuta para não estourar a caixa.
- **Acentuação:** usar normalmente (á, ã, ç, é, õ…), **desde que** a fonte
  suporte (ver `tools/check_glyphs.py`). Se a fonte não tiver o glifo, ajustamos
  a fonte — não tiramos o acento sem necessidade.

## Termos da interface (preencher conforme extração)

| Inglês            | PT-BR             | Observação            |
|-------------------|-------------------|-----------------------|
| New Game          | Novo Jogo         |                       |
| Continue          | Continuar         |                       |
| Options / Settings| Opções            |                       |
| Quit / Exit       | Sair              |                       |
| Back              | Voltar            |                       |
| Resume            | Retomar           |                       |
| Save / Load       | Salvar / Carregar |                       |
| Volume            | Volume            |                       |
| Fullscreen        | Tela cheia        |                       |
| Apply             | Aplicar           |                       |
| Inventory         | Inventário        |                       |

## Termos do mundo do jogo (preencher conforme extração)

| Inglês            | PT-BR             | Observação            |
|-------------------|-------------------|-----------------------|
| Deep Web          | Deep Web          | manter em inglês      |
| Email / Inbox     | E-mail / Caixa de entrada |               |
| Password          | Senha             |                       |
| Download          | Download / Baixar |                       |

> Conforme `extract_dll.py` e `extract_assets.py` rodarem, adicionamos aqui os
> termos recorrentes (nomes de sites, mensagens do "sequestrador", etc.) já com
> a forma padronizada.
