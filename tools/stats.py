#!/usr/bin/env python3
"""Mostra o progresso da tradução (quantas strings já têm 'traducao')."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalog import catalog_path, load_catalog


def stat(name: str):
    path = catalog_path(name)
    if not path.exists():
        return None
    entries = load_catalog(path)["entries"]
    done = sum(1 for e in entries if e.get("traducao"))
    return len(entries), done


def bar(done: int, total: int, width: int = 30) -> str:
    if total == 0:
        return "[" + "-" * width + "]"
    filled = int(width * done / total)
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def main() -> int:
    grand_total = grand_done = 0
    for name in ("dll.json", "assets.json"):
        res = stat(name)
        if res is None:
            print(f"{name:14} (ainda não gerado)")
            continue
        total, done = res
        grand_total += total
        grand_done += done
        pct = (100 * done / total) if total else 0
        print(f"{name:14} {bar(done, total)} {done}/{total} ({pct:.1f}%)")
    if grand_total:
        pct = 100 * grand_done / grand_total
        print(f"{'TOTAL':14} {bar(grand_done, grand_total)} {grand_done}/{grand_total} ({pct:.1f}%)")
    else:
        print("\nNenhum texto extraído ainda. Rode os extratores após enviar os arquivos do jogo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
