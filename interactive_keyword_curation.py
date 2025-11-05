#!/usr/bin/env python3
"""
Curateur interactif de mots-clés/corrections pour transcriptions.

But:
- Parcourir les "mots suspects" et/ou termes détectés dans un texte/rapport
  et demander à l'utilisateur si le mot est correct, à ignorer, ou à remplacer
  par un autre (ex: "Métin" -> "meeting").

Entrées:
- Fichier texte/markdown/JSON à analyser (résumé/transcription)
- Optionnel: rapport d'anomalies (detect_transcription_errors.py)
- Optionnel: liste initiale de mots-clés (.txt, 1 par ligne)

Sorties:
- curated_keywords.txt (mots validés)
- curated_corrections.json (mapping {source->remplacement})
- Optionnel: application directe des corrections sur le fichier (--apply)

Usage:
  python3 interactive_keyword_curation.py output/summaries/resume_detaille.md \
      --anomalies output/analysis/transcription_anomalies_*.md \
      --keywords keywords_domain.txt --apply
"""

import argparse
import json
import re
from pathlib import Path
from typing import List, Set, Dict, Tuple


WORD_REGEX = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ'_-]{3,}$")


def read_text(path: Path) -> str:
    text = path.read_text(encoding='utf-8', errors='ignore')
    if path.suffix.lower() == '.json':
        try:
            data = json.loads(text)
            text = (
                data.get('transcription', {}).get('text')
                or data.get('transcription', {}).get('full_text')
                or data.get('text')
                or text
            )
        except Exception:
            pass
    return text


def extract_candidates_from_text(text: str, max_per_word: int = 3) -> Set[str]:
    candidates: Set[str] = set()
    for raw in set(text.replace('\n', ' ').split(' ')):
        tok = raw.strip(" ,.;:!?()[]{}\"'`«»\t\r")
        if not tok:
            continue
        if WORD_REGEX.match(tok):
            candidates.add(tok)
    return candidates


def extract_candidates_from_anomalies(path: Path) -> Set[str]:
    if not path.exists():
        return set()
    content = path.read_text(encoding='utf-8', errors='ignore')
    # Cherche les lignes: - Mot suspect: `XXX`
    suspects = set()
    for line in content.splitlines():
        m = re.search(r"Mot suspect:\s*`([^`]+)`", line)
        if m:
            suspects.add(m.group(1).strip())
    return suspects


def load_keywords(path: Path | None) -> Set[str]:
    if not path or not path.exists():
        return set()
    return {l.strip() for l in path.read_text(encoding='utf-8', errors='ignore').splitlines() if l.strip() and not l.strip().startswith('#')}


def interactive_curation(candidates: List[str]) -> Tuple[Set[str], Dict[str, str]]:
    validated: Set[str] = set()
    mapping: Dict[str, str] = {}
    print("\n=== Curateur interactif ===")
    print("Tapez: Enter = garder tel quel comme mot-clé | r = remplacer | s = ignorer | q = quitter")
    for term in candidates:
        while True:
            ans = input(f"Mot: '{term}' [Enter/r/s/q]: ").strip().lower()
            if ans == 'q':
                return validated, mapping
            if ans == 's':
                # ignorer
                break
            if ans == 'r':
                repl = input("  -> Remplacer par: ").strip()
                if repl:
                    mapping[term] = repl
                    print(f"  ✓ Mapping: {term} -> {repl}")
                    break
                else:
                    print("  (vide ignoré)")
                    continue
            # Enter / défaut: valider comme mot-clé
            validated.add(term)
            print(f"  ✓ Ajouté aux mots-clés: {term}")
            break
    return validated, mapping


def write_outputs(validated: Set[str], mapping: Dict[str, str], base_dir: Path):
    base_dir.mkdir(parents=True, exist_ok=True)
    kw_path = base_dir / 'curated_keywords.txt'
    map_path = base_dir / 'curated_corrections.json'
    kw_path.write_text('\n'.join(sorted(validated)), encoding='utf-8')
    map_path.write_text(json.dumps(mapping, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\n✅ Sauvé: {kw_path}")
    print(f"✅ Sauvé: {map_path}")


def apply_mapping_inplace(input_file: Path, mapping: Dict[str, str]):
    from apply_transcription_fixes import apply_fixes  # réutilise la logique existante
    original = input_file.read_text(encoding='utf-8', errors='ignore')
    corrected = apply_fixes(original, {k.lower(): v for k, v in mapping.items()})
    input_file.write_text(corrected, encoding='utf-8')
    print(f"✅ Corrections appliquées au fichier: {input_file}")


def main() -> int:
    ap = argparse.ArgumentParser(description='Curateur interactif de mots-clés et corrections')
    ap.add_argument('input_file', help='Fichier à analyser (txt/md/json)')
    ap.add_argument('--anomalies', help='Rapport d’anomalies (md) pour lister les mots suspects', default='')
    ap.add_argument('--keywords', help='Liste initiale de mots-clés (txt)', default='')
    ap.add_argument('--apply', action='store_true', help='Appliquer immédiatement les corrections choisies (inplace)')
    args = ap.parse_args()

    inp = Path(args.input_file)
    if not inp.exists():
        print(f"❌ Introuvable: {inp}")
        return 1

    text = read_text(inp)
    base_candidates = extract_candidates_from_text(text)
    suspects = extract_candidates_from_anomalies(Path(args.anomalies)) if args.anomalies else set()
    initial_kws = load_keywords(Path(args.keywords)) if args.keywords else set()

    # Construire la liste à curator: suspects d’abord, puis le reste, sans doublons
    ordered: List[str] = []
    seen: Set[str] = set()
    for src in [suspects, initial_kws, base_candidates]:
        for t in sorted(src):
            if t not in seen:
                seen.add(t)
                ordered.append(t)

    validated, mapping = interactive_curation(ordered)
    write_outputs(validated, mapping, Path('output/curation'))

    if args.apply and mapping:
        apply_mapping_inplace(inp, mapping)

    return 0


if __name__ == '__main__':
    raise SystemExit(main())


