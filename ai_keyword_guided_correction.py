#!/usr/bin/env python3
"""
Correction IA guidée par mots-clés pour les transcriptions/résumés (FR).

Idée:
- Entrée: fichier texte/markdown/JSON + liste de mots-clés métier (fichier .txt ou liste CSV).
- Pour chaque phrase, on identifie les tokens proches des mots-clés (similarité) puis on valide avec un modèle maské FR (CamemBERT):
  si le mot-clé proposé apparaît dans le top-k des prédictions, on remplace.
- Produit: fichier corrigé + rapport des remplacements.

Usage:
  python3 ai_keyword_guided_correction.py input.md --keywords keywords.txt --out output/summaries/input_kw_corrected.md
  python3 ai_keyword_guided_correction.py transcription.json --keywords "Forvia,Azure,meeting" --inplace
"""

import argparse
import json
import re
import difflib
from pathlib import Path
from typing import List, Tuple, Dict, Optional

import torch
from transformers import pipeline


SENTENCE_SPLIT_REGEX = re.compile(r"(?<=[.!?])\s+")
WORD_REGEX = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ'_-]{2,}$")


def read_text(path: Path) -> str:
    raw = path.read_text(encoding='utf-8', errors='ignore')
    if path.suffix.lower() == '.json':
        try:
            data = json.loads(raw)
            raw = (
                data.get('transcription', {}).get('text')
                or data.get('transcription', {}).get('full_text')
                or data.get('text')
                or raw
            )
        except Exception:
            pass
    # retirer blocs code markdown
    raw = re.sub(r"```[\s\S]*?```", " ", raw)
    return raw


def write_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')


def split_sentences(text: str) -> List[str]:
    s = SENTENCE_SPLIT_REGEX.split(text.strip())
    return [x.strip() for x in s if x and x.strip()]


def load_keywords(arg: Optional[str]) -> List[str]:
    if not arg:
        return []
    p = Path(arg)
    if p.exists():
        content = p.read_text(encoding='utf-8', errors='ignore')
        if p.suffix.lower() in {'.txt', ''}:
            kws = [l.strip() for l in content.splitlines() if l.strip() and not l.strip().startswith('#')]
            return kws
        else:
            # fallback: split by commas
            return [t.strip() for t in content.split(',') if t.strip()]
    # else treat as csv string
    return [t.strip() for t in arg.split(',') if t.strip()]


def preserve_case(original: str, replacement: str) -> str:
    if original.isupper():
        return replacement.upper()
    if original.istitle():
        return replacement[:1].upper() + replacement[1:]
    return replacement


def best_keyword_candidate(token: str, keywords: List[str], min_ratio: float = 0.50, debug: bool = False) -> Optional[str]:
    """
    Trouve le mot-clé le plus similaire au token donné.
    Utilise uniquement la similarité, pas de mapping prédéfini.
    """
    token_l = token.lower()
    best: Tuple[str, float] | None = None
    
    for kw in keywords:
        kw_l = kw.lower()
        # Si exact match (insensible casse), retourner directement
        if token_l == kw_l:
            return kw
        # Calcul de similarité
        r = difflib.SequenceMatcher(None, token_l, kw_l).ratio()
        if debug:
            print(f"  Debug: '{token_l}' vs '{kw_l}' = {r:.3f}")
        if r >= min_ratio and (best is None or r > best[1]):
            best = (kw, r)
    
    if best and debug:
        print(f"  → Meilleur candidat: '{best[0]}' (ratio: {best[1]:.3f})")
    return best[0] if best else None


def lm_confirms(nlp_fill, sentence_tokens: List[str], index: int, candidate: str, topk: int = 5, 
                similarity_score: float = 0.0, debug: bool = False) -> bool:
    masked = sentence_tokens.copy()
    masked[index] = '<mask>'
    masked_sentence = ' '.join(masked)
    try:
        preds = nlp_fill(masked_sentence)
    except Exception:
        return False
    cand_l = candidate.lower()
    if debug:
        print(f"  LM prédictions pour '{masked_sentence}':")
        for i, p in enumerate(preds[:topk], 1):
            print(f"    {i}. {p.get('token_str', '').strip()} (score: {p.get('score', 0):.3f})")
    
    # Chercher dans le top-k élargi (topk * 2) pour être plus permissif
    extended_topk = min(topk * 2, len(preds))
    for p in preds[:extended_topk]:
        if p.get('token_str', '').strip().lower() == cand_l:
            if debug:
                print(f"  ✓ '{candidate}' confirmé par LM (top-{extended_topk})")
            return True
    
    # Si similarité raisonnable (>0.50) ET meilleur score LM pas très élevé (<0.15),
    # accepter quand même (cas où transcription erronée mais contexte peu clair)
    # ET si le candidat est dans les mots-clés fournis (donc c'est intentionnel)
    if similarity_score > 0.50 and preds and preds[0].get('score', 0) < 0.15:
        if debug:
            print(f"  ✓ '{candidate}' accepté (similarité {similarity_score:.2f} > 0.50, confiance LM faible {preds[0].get('score', 0):.3f})")
        return True
    
    if debug:
        print(f"  ✗ '{candidate}' non confirmé par LM")
    return False


def correct_text_with_keywords(text: str, keywords: List[str], nlp_fill, topk: int = 5, debug: bool = False) -> Tuple[str, List[Dict]]:
    # Préserver la structure originale (lignes/paragraphes)
    lines = text.split('\n')
    changes: List[Dict] = []
    corrected_lines: List[str] = []

    for line in lines:
        if not line.strip():
            corrected_lines.append(line)
            continue
        
        # Traiter phrase par phrase dans la ligne
        sentences = split_sentences(line)
        corrected_line_parts = []
        
        for sent in sentences:
            tokens = sent.split()
            for i, tok in enumerate(tokens):
                if not WORD_REGEX.match(tok):
                    continue
                cand = best_keyword_candidate(tok, keywords, debug=debug)
                if not cand:
                    continue
                # Calculer le score de similarité pour le passer à lm_confirms
                tok_l = tok.lower()
                cand_l = cand.lower()
                sim_score = difflib.SequenceMatcher(None, tok_l, cand_l).ratio()
                if debug:
                    print(f"\n🔍 Analyse: '{tok}' → candidat: '{cand}' (similarité: {sim_score:.3f})")
                if lm_confirms(nlp_fill, tokens, i, cand, topk=topk, similarity_score=sim_score, debug=debug):
                    new_tok = preserve_case(tok, cand)
                    if new_tok != tok:
                        if debug:
                            print(f"  ✅ Remplacement: '{tok}' → '{new_tok}'")
                        changes.append({'sentence': sent, 'from': tok, 'to': new_tok})
                        tokens[i] = new_tok
            corrected_line_parts.append(' '.join(tokens))
        
        corrected_lines.append(' '.join(corrected_line_parts) if corrected_line_parts else line)

    return ('\n'.join(corrected_lines), changes)


def main() -> int:
    parser = argparse.ArgumentParser(description='Correction IA guidée par mots-clés (CamemBERT fill-mask)')
    parser.add_argument('input_file', help='Fichier texte/markdown/JSON à corriger')
    parser.add_argument('--keywords', help='Fichier .txt de mots-clés (1 par ligne) ou liste CSV')
    parser.add_argument('--topk', type=int, default=5, help='Top-k du modèle maské pour valider')
    parser.add_argument('--out', help='Chemin du fichier corrigé')
    parser.add_argument('--inplace', action='store_true', help='Ecrire les corrections dans le fichier d\'entree')
    parser.add_argument('--debug', action='store_true', help='Mode debug (affiche details de la detection/correction)')
    args = parser.parse_args()

    inp = Path(args.input_file)
    if not inp.exists():
        print(f"❌ Introuvable: {inp}")
        return 1

    kws = load_keywords(args.keywords)
    if not kws:
        print("⚠️  Aucun mot-clé fourni — aucune correction guidée ne sera appliquée.")

    text = read_text(inp)

    device = 0 if torch.backends.mps.is_available() else -1
    print("🔄 Chargement de CamemBERT large (almanach/camembert-large)...")
    try:
        # Utiliser le modèle large officiel (335M paramètres, plus performant)
        nlp_fill = pipeline('fill-mask', model='almanach/camembert-large', device=device)
        print("✅ Modèle large chargé (~335M paramètres, CCNet 135GB)")
    except Exception as e:
        print(f"⚠️  Modèle large non disponible: {e}")
        print("🔄 Fallback vers CamemBERT base...")
        nlp_fill = pipeline('fill-mask', model='camembert-base', device=device)
        print("✅ Modèle base chargé (~110M paramètres)")

    corrected, changes = correct_text_with_keywords(text, kws, nlp_fill, topk=args.topk, debug=args.debug)

    if args.inplace:
        write_text(inp, corrected)
        out_path = inp
    else:
        out_path = Path(args.out) if args.out else Path('output/summaries') / (inp.stem + '_kw_corrected' + inp.suffix)
        write_text(out_path, corrected)

    # Rapport
    report_path = Path('output/analysis') / (inp.stem + '_kw_corrections.json')
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps({'changes_count': len(changes), 'changes': changes}, ensure_ascii=False, indent=2), encoding='utf-8')

    print(f"✅ Corrections appliquées: {len(changes)} remplacements | sortie: {out_path}")
    print(f"📄 Rapport: {report_path}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())


