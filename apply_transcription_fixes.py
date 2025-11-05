#!/usr/bin/env python3
"""
Applique des corrections simples sur un texte de transcription/résumé.

Fonctions clés:
- Remplacer des confusions fréquentes (ex: "Métin" → "meeting", "Fourvia" → "Forvia").
- Support d'un fichier de mapping utilisateur (JSON) pour surcharger/ajouter des corrections.
- Préservation de la casse (minuscule, Capitale, MAJUSCULES).

Usage:
  python3 apply_transcription_fixes.py input.md --out output/summaries/input_corrected.md
  python3 apply_transcription_fixes.py input.md --map my_corrections.json --inplace

Format du fichier --map (JSON):
{
  "metin": "meeting",
  "planine": "planning",
  "fourvia": "Forvia"
}
"""

import argparse
import json
import re
from pathlib import Path
from typing import Dict


DEFAULT_MAP: Dict[str, str] = {
    # Variantes/erreurs fréquentes → correction
    "metin": "meeting",
    "métin": "meeting",
    "meting": "meeting",
    "metting": "meeting",
    "fourvia": "Forvia",
    "forvia": "Forvia",
    "planine": "planning",
    "observis": "observability",
}


def load_user_map(path: Path | None) -> Dict[str, str]:
    if not path:
        return {}
    if not path.exists():
        raise FileNotFoundError(f"Mapping utilisateur inexistant: {path}")
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise ValueError("Le fichier de mapping JSON doit contenir un objet { clef: valeur }.")
    # Normaliser clés en minuscule
    return {str(k).lower(): str(v) for k, v in data.items()}


def preserve_case(original: str, replacement: str) -> str:
    """Adapte la casse du remplacement à celle du mot original."""
    if original.isupper():
        return replacement.upper()
    if original.istitle():
        return replacement[:1].upper() + replacement[1:]
    return replacement


def apply_fixes(text: str, mapping: Dict[str, str]) -> str:
    # Construire un gros regex de mots à corriger (insensible à la casse)
    # Utilise des frontières de mot pour éviter les sous-matches.
    keys = sorted(mapping.keys(), key=len, reverse=True)
    if not keys:
        return text
    pattern = re.compile(r"\b(" + "|".join(map(re.escape, keys)) + r")\b", re.IGNORECASE)

    def _repl(match: re.Match) -> str:
        orig = match.group(0)
        fixed = mapping.get(orig.lower(), orig)
        return preserve_case(orig, fixed)

    return pattern.sub(_repl, text)


def main() -> int:
    parser = argparse.ArgumentParser(description="Appliquer des corrections de transcription simples")
    parser.add_argument("input_file", help="Fichier texte/markdown à corriger")
    parser.add_argument("--map", dest="map_file", help="Fichier JSON de mapping utilisateur")
    parser.add_argument("--out", dest="out_file", help="Fichier de sortie corrigé")
    parser.add_argument("--inplace", action="store_true", help="Écraser le fichier d'entrée")
    args = parser.parse_args()

    inp = Path(args.input_file)
    if not inp.exists():
        print(f"❌ Introuvable: {inp}")
        return 1

    user_map = load_user_map(Path(args.map_file)) if args.map_file else {}
    mapping = DEFAULT_MAP.copy()
    mapping.update(user_map)

    original = inp.read_text(encoding='utf-8', errors='ignore')
    corrected = apply_fixes(original, mapping)

    if args.inplace:
        inp.write_text(corrected, encoding='utf-8')
        print(f"✅ Corrections appliquées (inplace): {inp}")
        return 0

    if args.out_file:
        out_path = Path(args.out_file)
    else:
        out_dir = Path("output/summaries")
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / (inp.stem + "_corrected" + inp.suffix)

    out_path.write_text(corrected, encoding='utf-8')
    print(f"✅ Fichier corrigé: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


