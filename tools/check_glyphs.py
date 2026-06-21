#!/usr/bin/env python3
"""Verifica se as fontes do jogo cobrem os caracteres acentuados do PT-BR.

Procura fontes em game_files/ (TTF embutidas em assets Font do Unity e/ou
arquivos .ttf/.otf soltos) e checa a cobertura de:
    á à â ã é ê í ó ô õ ú ü ç  (e maiúsculas)

Se faltar algum, a tradução aparece com quadradinhos (□) no jogo e será preciso
regenerar/expandir o atlas da fonte. Fontes TextMeshPro (bitmap/SDF) não têm TTF
embutido e precisam ser checadas pelo atlas — o script avisa nesses casos.

Requer: UnityPy, fonttools
"""
from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalog import GAME_FILES_DIR

PT_CHARS = "áàâãéêíóôõúüçÁÀÂÃÉÊÍÓÔÕÚÜÇ"


def covered_codepoints_from_ttf(ttf_bytes: bytes) -> set[int]:
    from fontTools.ttLib import TTFont

    font = TTFont(io.BytesIO(ttf_bytes), fontNumber=0, lazy=True)
    cps: set[int] = set()
    try:
        for table in font["cmap"].tables:
            cps.update(table.cmap.keys())
    except Exception:
        pass
    return cps


def report(name: str, cps: set[int]) -> bool:
    missing = [c for c in PT_CHARS if ord(c) not in cps]
    if missing:
        print(f"  [FALTAM] {name}: {' '.join(missing)}")
        return False
    print(f"  [OK]     {name}: cobre todos os acentos PT-BR")
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", help="arquivos/pastas (padrão: game_files/)")
    args = ap.parse_args()

    targets = [Path(p) for p in args.paths] or [GAME_FILES_DIR]
    import UnityPy

    found_any = False
    all_ok = True

    # 1) .ttf/.otf soltos
    for t in targets:
        if t.is_dir():
            for p in sorted(t.rglob("*")):
                if p.suffix.lower() in (".ttf", ".otf"):
                    found_any = True
                    all_ok &= report(p.name, covered_codepoints_from_ttf(p.read_bytes()))

    # 2) fontes embutidas em assets Unity (Font.m_FontData)
    for t in targets:
        try:
            env = UnityPy.load(str(t))
        except Exception:
            continue
        for obj in env.objects:
            try:
                if obj.type.name != "Font":
                    continue
                data = obj.read()
                name = getattr(data, "m_Name", "Font") or "Font"
                blob = getattr(data, "m_FontData", None)
                if blob:
                    found_any = True
                    all_ok &= report(f"{name} (Unity Font)", covered_codepoints_from_ttf(bytes(blob)))
                else:
                    print(f"  [?]      {name}: fonte sem TTF embutido "
                          f"(provável bitmap/TMP — checar atlas manualmente)")
            except Exception as e:
                print(f"  ! aviso ao ler fonte: {e}", file=sys.stderr)

    if not found_any:
        print("Nenhuma fonte encontrada em game_files/. "
              "Envie os arquivos *.assets que contêm as fontes.", file=sys.stderr)
        return 1
    print("\nResumo:", "todas as fontes cobrem PT-BR ✅" if all_ok
          else "há fontes SEM acentos — será preciso ajustar o atlas ⚠️")
    return 0 if all_ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
