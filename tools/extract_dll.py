#!/usr/bin/env python3
"""Extrai os literais de string do Assembly-CSharp.dll para o catálogo dll.json.

Lê o heap de "user strings" (#US) do assembly .NET — onde ficam os literais de
string usados pelo código (instruções ldstr). NÃO modifica nada.

Uso:
    python tools/extract_dll.py [caminho/Assembly-CSharp.dll]
    (padrão: game_files/Assembly-CSharp.dll)

Para INJETAR as traduções de volta na DLL use o tool C# (tools/dll-tool, via
Mono.Cecil) ou o dnSpy — ver docs/GUIA.md. Este script é só de leitura.

Requer: dnfile  (pip install -r tools/requirements.txt)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalog import GAME_FILES_DIR, catalog_path, dll_id, load_catalog, merge_entries, save_catalog


def read_compressed_uint(data: bytes, pos: int) -> tuple[int, int]:
    """Lê um inteiro com tamanho comprimido (formato ECMA-335). Retorna (valor, nova_pos)."""
    b0 = data[pos]
    if b0 & 0x80 == 0:
        return b0, pos + 1
    if b0 & 0xC0 == 0x80:
        return ((b0 & 0x3F) << 8) | data[pos + 1], pos + 2
    return (((b0 & 0x1F) << 24) | (data[pos + 1] << 16)
            | (data[pos + 2] << 8) | data[pos + 3]), pos + 4


def iter_user_strings(heap: bytes):
    """Gera (offset, texto) de cada string no heap #US."""
    pos = 1  # offset 0 é a string vazia (1 byte 0x00)
    n = len(heap)
    while pos < n:
        start = pos
        try:
            length, p = read_compressed_uint(heap, pos)
        except IndexError:
            break
        if length == 0:
            pos = p
            continue
        raw = heap[p:p + length]
        pos = p + length
        # último byte é flag (0x00/0x01); o texto são os bytes anteriores em UTF-16LE
        text = raw[:-1].decode("utf-16-le", errors="replace") if length > 1 else ""
        if text:
            yield start, text


def get_us_heap(dll_path: Path) -> bytes:
    import dnfile

    pe = dnfile.dnPE(str(dll_path))
    us = getattr(pe.net, "user_strings", None)
    if us is not None:
        for attr in ("__data__", "data", "_data"):
            b = getattr(us, attr, None)
            if isinstance(b, (bytes, bytearray)):
                return bytes(b)
    md = getattr(pe.net, "metadata", None)
    streams = getattr(md, "streams", None) if md else None
    if streams and hasattr(streams, "get"):
        for key in (b"#US", "#US"):
            s = streams.get(key)
            if s is not None:
                for attr in ("__data__", "data", "_data"):
                    b = getattr(s, attr, None)
                    if isinstance(b, (bytes, bytearray)):
                        return bytes(b)
    raise RuntimeError("não localizei o heap #US — é um Assembly-CSharp.dll .NET válido?")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dll", nargs="?", default=str(GAME_FILES_DIR / "Assembly-CSharp.dll"),
                    help="caminho do Assembly-CSharp.dll (padrão: game_files/Assembly-CSharp.dll)")
    ap.add_argument("-o", "--output", default=str(catalog_path("dll.json")),
                    help="catálogo de saída (padrão: translations/pt-BR/dll.json)")
    ap.add_argument("--min-len", type=int, default=2, help="ignora strings com menos de N caracteres")
    args = ap.parse_args()

    dll_path = Path(args.dll)
    if not dll_path.exists():
        print(f"ERRO: não encontrei {dll_path}.\n"
              f"Envie o Assembly-CSharp.dll para game_files/ (ver game_files/LEIA-ME.md).",
              file=sys.stderr)
        return 1

    print(f"Lendo literais de: {dll_path}")
    heap = get_us_heap(dll_path)
    seen: dict[str, dict] = {}
    for _off, text in iter_user_strings(heap):
        if len(text) < args.min_len or text in seen:
            continue
        seen[text] = {"id": dll_id(text), "fonte": text, "traducao": "",
                      "contexto": "Assembly-CSharp.dll (ldstr)"}

    out = Path(args.output)
    data = load_catalog(out)
    novos, atualizados = merge_entries(data, list(seen.values()))
    save_catalog(out, data)
    print(f"OK: {len(seen)} literais únicos | +{novos} novos, {atualizados} atualizados "
          f"| total no catálogo: {len(data['entries'])}")
    print(f"-> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
