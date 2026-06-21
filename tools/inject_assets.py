#!/usr/bin/env python3
"""Reinjeta as traduções de assets.json nos arquivos *.assets -> pasta build/.

Lê translations/pt-BR/assets.json, abre cada arquivo original em game_files/,
aplica as traduções (só entradas com 'traducao' preenchida) e grava a versão
modificada em build/ com o mesmo nome.

Uso:
    python tools/inject_assets.py

Requer: UnityPy

ATENÇÃO: sempre faça backup dos arquivos originais do jogo antes de substituir.
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalog import BUILD_DIR, GAME_FILES_DIR, catalog_path, load_catalog


def split_path(path: str) -> list:
    """'options[2].m_Text' -> ['options', 2, 'm_Text']"""
    tokens: list = []
    buf = ""
    for ch in path:
        if ch == ".":
            if buf:
                tokens.append(buf)
                buf = ""
        elif ch == "[":
            if buf:
                tokens.append(buf)
                buf = ""
        elif ch == "]":
            if buf:
                tokens.append(int(buf))
                buf = ""
        else:
            buf += ch
    if buf:
        tokens.append(buf)
    return tokens


def set_by_path(tree, path: str, value) -> None:
    tokens = split_path(path)
    node = tree
    for t in tokens[:-1]:
        node = node[t]
    node[tokens[-1]] = value


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-i", "--input", default=str(catalog_path("assets.json")))
    ap.add_argument("--game-files", default=str(GAME_FILES_DIR))
    ap.add_argument("--out", default=str(BUILD_DIR))
    args = ap.parse_args()

    import UnityPy

    data = load_catalog(Path(args.input))
    by_file: dict[str, list] = defaultdict(list)
    for e in data["entries"]:
        if not e.get("traducao"):
            continue
        try:
            fname, path_id, field = e["id"].split(":", 2)
            by_file[fname].append((int(path_id), field, e["traducao"]))
        except ValueError:
            print(f"  ! id inválido, pulando: {e['id']}", file=sys.stderr)

    if not by_file:
        print("Nada para injetar (nenhuma entrada com 'traducao' preenchida).")
        return 0

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    game_dir = Path(args.game_files)

    total = 0
    for fname, edits in by_file.items():
        src = game_dir / fname
        if not src.exists():
            print(f"  ! original não encontrado: {src} (pulando {len(edits)} edições)", file=sys.stderr)
            continue
        print(f"Injetando {len(edits)} traduções em {fname}")
        env = UnityPy.load(str(src))
        wanted: dict[int, list] = defaultdict(list)
        for pid, field, value in edits:
            wanted[pid].append((field, value))
        for obj in env.objects:
            if obj.path_id not in wanted:
                continue
            try:
                if obj.type.name == "TextAsset":
                    data_obj = obj.read()
                    for _field, value in wanted[obj.path_id]:
                        data_obj.m_Script = value
                    data_obj.save()
                else:
                    tree = obj.read_typetree()
                    for field, value in wanted[obj.path_id]:
                        set_by_path(tree, field, value)
                    obj.save_typetree(tree)
                total += len(wanted[obj.path_id])
            except Exception as e:
                print(f"  ! falha em path_id={obj.path_id}: {e}", file=sys.stderr)
        dst = out_dir / fname
        with open(dst, "wb") as f:
            f.write(env.file.save())
        print(f"  -> {dst}")

    print(f"OK: {total} traduções injetadas. Arquivos em {out_dir}/.")
    print("Lembre: faça backup dos originais do jogo antes de substituir.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
