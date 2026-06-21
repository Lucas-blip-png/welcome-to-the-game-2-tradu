#!/usr/bin/env python3
"""Extrai textos traduzíveis dos arquivos *.assets para o catálogo assets.json.

Varre os arquivos do jogo com UnityPy e coleta strings de:
  - TextAsset (m_Script)              -> diálogos/config guardados como arquivos de texto
  - MonoBehaviour com typetree        -> UI Text, TextMeshPro, dropdowns, etc.

Uso:
    python tools/extract_assets.py [arquivo_ou_pasta ...]
    (padrão: game_files/)

Requer: UnityPy  (pip install -r tools/requirements.txt)

Obs.: alguns MonoBehaviour só têm typetree quando o Unity embute essa info no
build. Se faltar, o UnityPy precisa do Assembly-CSharp.dll para gerar o typetree
(tratamos isso na fase de extração com os arquivos reais).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalog import GAME_FILES_DIR, catalog_path, load_catalog, merge_entries, save_catalog

TEXT_FIELDS = {"m_Text", "m_text", "text", "m_String"}
NAME_RE = re.compile(r"(.+\.assets|level\d+|globalgamemanagers(\.assets)?|.+\.unity3d|.+\.bundle)$")
SKIP_SUFFIXES = {".resS", ".resource", ".dll", ".config", ".md", ".gitkeep"}


def discover(targets) -> list[Path]:
    files: list[Path] = []
    for t in targets:
        t = Path(t)
        if t.is_dir():
            for p in sorted(t.rglob("*")):
                if p.is_file() and p.suffix not in SKIP_SUFFIXES and NAME_RE.match(p.name):
                    files.append(p)
        elif t.is_file():
            files.append(t)
    return files


def walk_strings(node, path=""):
    """Percorre um typetree (dict/list) e gera (campo, valor) dos campos de texto."""
    if isinstance(node, dict):
        for k, v in node.items():
            child = f"{path}.{k}" if path else k
            if isinstance(v, str):
                if k in TEXT_FIELDS and v.strip():
                    yield child, v
            else:
                yield from walk_strings(v, child)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk_strings(v, f"{path}[{i}]")


def extract_file(path: Path) -> list[dict]:
    import UnityPy

    env = UnityPy.load(str(path))
    fname = path.name
    out: list[dict] = []
    for obj in env.objects:
        try:
            tname = obj.type.name
        except Exception:
            continue
        try:
            if tname == "TextAsset":
                data = obj.read()
                script = getattr(data, "m_Script", None)
                if script is None:
                    script = getattr(data, "text", None)
                name = getattr(data, "m_Name", "") or ""
                if isinstance(script, (bytes, bytearray)):
                    try:
                        script = script.decode("utf-8")
                    except UnicodeDecodeError:
                        continue  # provavelmente binário, ignora
                if isinstance(script, str) and script.strip():
                    out.append({"id": f"{fname}:{obj.path_id}:m_Script",
                                "fonte": script, "traducao": "",
                                "contexto": f"TextAsset '{name}'"})
            elif tname == "MonoBehaviour":
                st = getattr(obj, "serialized_type", None)
                if not (st and getattr(st, "node", None)):
                    continue  # sem typetree embutido
                tree = obj.read_typetree()
                name = tree.get("m_Name", "") if isinstance(tree, dict) else ""
                for field, value in walk_strings(tree):
                    out.append({"id": f"{fname}:{obj.path_id}:{field}",
                                "fonte": value, "traducao": "",
                                "contexto": f"MonoBehaviour '{name}' [{field}]"})
        except Exception as e:
            print(f"  ! aviso: {tname} path_id={getattr(obj, 'path_id', '?')}: {e}", file=sys.stderr)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", help="arquivos/pastas (padrão: game_files/)")
    ap.add_argument("-o", "--output", default=str(catalog_path("assets.json")))
    args = ap.parse_args()

    targets = args.paths or [GAME_FILES_DIR]
    files = discover(targets)
    if not files:
        print("Nenhum arquivo .assets/level* encontrado. "
              "Envie os arquivos do jogo para game_files/ (ver game_files/LEIA-ME.md).",
              file=sys.stderr)
        return 1

    all_entries: list[dict] = []
    for f in files:
        print(f"Extraindo: {f.name}")
        try:
            all_entries += extract_file(f)
        except Exception as e:
            print(f"  ! erro abrindo {f}: {e}", file=sys.stderr)

    out = Path(args.output)
    data = load_catalog(out)
    novos, atualizados = merge_entries(data, all_entries)
    save_catalog(out, data)
    print(f"OK: {len(all_entries)} strings | +{novos} novas, {atualizados} atualizadas "
          f"| total: {len(data['entries'])}")
    print(f"-> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
