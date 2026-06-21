"""Utilitários compartilhados para os catálogos de tradução (JSON).

Cada catálogo é um JSON no formato:

    {
      "language": "pt-BR",
      "game": "Welcome to the Game 2",
      "entries": [
        {"id": "...", "fonte": "texto original", "traducao": "", "contexto": "..."}
      ]
    }

- "fonte"    = texto original em inglês (chave para reinjetar).
- "traducao" = texto em PT-BR (preenchido por nós; vazio = pendente).
- "id"       = identificador estável usado para mesclar re-extrações sem perder trabalho.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parent.parent
TRANSLATIONS_DIR = REPO_ROOT / "translations" / "pt-BR"
GAME_FILES_DIR = REPO_ROOT / "game_files"
BUILD_DIR = REPO_ROOT / "build"


def catalog_path(name: str) -> Path:
    return TRANSLATIONS_DIR / name


def dll_id(fonte: str) -> str:
    """ID estável p/ um literal da DLL — igual no extrator Python e no tool C#."""
    return "dll:" + hashlib.sha1(fonte.encode("utf-8")).hexdigest()[:12]


def load_catalog(path: Path) -> dict:
    path = Path(path)
    if path.exists():
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}
    data.setdefault("language", "pt-BR")
    data.setdefault("game", "Welcome to the Game 2")
    data.setdefault("entries", [])
    return data


def save_catalog(path: Path, data: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def merge_entries(data: dict, new_entries: Iterable[dict]) -> tuple[int, int]:
    """Mescla preservando 'traducao' já feita. Retorna (novos, atualizados)."""
    by_id = {e["id"]: e for e in data["entries"]}
    novos = atualizados = 0
    for e in new_entries:
        cur = by_id.get(e["id"])
        if cur is None:
            e.setdefault("traducao", "")
            data["entries"].append(e)
            by_id[e["id"]] = e
            novos += 1
        elif cur.get("fonte") != e.get("fonte") or (e.get("contexto") and cur.get("contexto") != e.get("contexto")):
            cur["fonte"] = e.get("fonte", cur.get("fonte"))
            if e.get("contexto"):
                cur["contexto"] = e["contexto"]
            atualizados += 1
    return novos, atualizados
