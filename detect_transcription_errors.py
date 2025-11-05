#!/usr/bin/env python3
"""
Détection simple d'erreurs de transcription par plausibilité sémantique (FR).

Principe (1er temps):
- On parcourt les phrases du texte.
- Pour chaque mot candidat, on remplace le mot par un token <mask> et on demande
  à un modèle FR (CamemBERT) ses meilleures prédictions.
- Si le mot original n'apparaît pas dans le top-k et que sa probabilité est très basse,
  on le marque comme "suspect" et on suggère les meilleures alternatives.

Usage:
  python3 detect_transcription_errors.py path/to/file.md --topk 5 --max-sentences 500

Notes:
- Optimisé M4 (threads CPU). Pas besoin de GPU pour ce check.
- Vous pouvez fournir un fichier d'allowlist pour ignorer des mots métiers:
  --allowlist keywords.txt
"""

import os
import re
import sys
import json
import difflib
import math
import time
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional

import torch

# Optimisations M4 CPU threads
if torch.backends.mps.is_available():
    torch.set_num_threads(14)
    os.environ['OMP_NUM_THREADS'] = '14'
    os.environ['MKL_NUM_THREADS'] = '14'
    os.environ['NUMEXPR_NUM_THREADS'] = '14'
    print("🚀 Optimisations Mac M4 activées (threads CPU)")

try:
    from transformers import pipeline
except Exception as e:
    print(f"❌ transformers non disponible: {e}")
    print("💡 Installez avec: uv add transformers sentencepiece || pip install transformers sentencepiece")
    sys.exit(1)

# Correcteur orthographique FR (optionnel mais recommandé)
try:
    from spellchecker import SpellChecker
    SPELLCHECK_AVAILABLE = True
except Exception:
    SPELLCHECK_AVAILABLE = False

# Output manager optionnel
try:
    from output_manager import OutputManager
    OUTPUT_MANAGER = OutputManager()
except Exception:
    OUTPUT_MANAGER = None


SENTENCE_SPLIT_REGEX = re.compile(r"(?<=[.!?])\s+")
WORD_REGEX = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ'-]{2,}$")


def read_text_from_file(path: Path) -> str:
    text = path.read_text(encoding='utf-8', errors='ignore')
    # Si markdown, supprimer les blocs de code pour éviter bruit
    text = re.sub(r"```[\s\S]*?```", " ", text)
    return text


def split_sentences(text: str) -> List[str]:
    # Split simple basé ponctuation. Suffisant pour un 1er temps.
    sentences = SENTENCE_SPLIT_REGEX.split(text.strip())
    # Nettoyage basique
    sentences = [s.strip() for s in sentences if s and len(s.strip()) > 0]
    return sentences


def load_allowlist(path: Optional[Path]) -> set:
    allow = set()
    if path and path.exists():
        for line in path.read_text(encoding='utf-8', errors='ignore').splitlines():
            w = line.strip()
            if w and not w.startswith('#'):
                allow.add(w)
                allow.add(w.lower())
                allow.add(w.capitalize())
    return allow


CONFUSION_MAP = {
    # Confusions ASR fréquentes FR/EN ou proches
    "metin": "meeting",
    "métin": "meeting",
    "meting": "meeting",
    "metting": "meeting",
    "fourvia": "Forvia",
    "forvia": "Forvia",
    "planine": "planning",
    "observis": "observability",
}


def mask_and_score_sentence(nlp_fill, sentence: str, topk: int, allowlist: set,
                            max_tokens: int = 40) -> List[Dict]:
    """Retourne une liste d'anomalies pour la phrase.
    Pour limiter le coût, on ne teste qu'un sous-ensemble de tokens (<= max_tokens).
    """
    tokens = sentence.split()
    anomalies = []

    # Heuristique: ignorer phrases trop longues pour rester rapide
    step = max(1, math.ceil(len(tokens) / max_tokens))

    for i in range(0, len(tokens), step):
        original = tokens[i]
        # Filtrer tokens candidats (mots alphabétiques; éviter pronoms/courts)
        if not WORD_REGEX.match(original):
            continue
        if original.lower() in allowlist:
            continue

        # Construire phrase masquée
        masked_tokens = tokens.copy()
        masked_tokens[i] = "<mask>"
        masked_sentence = " ".join(masked_tokens)

        try:
            preds = nlp_fill(masked_sentence)
        except Exception as e:
            # Certaines phrases peuvent échouer si mal tokenisées
            continue

        # Normaliser comparaisons (CamemBERT peut proposer casse différente)
        original_norm = original.strip().strip("'–- ")
        original_lower = original_norm.lower()

        suggested = []
        found = False
        best_score = None
        for p in preds[:topk]:
            tok = p.get('token_str', '').strip()
            score = float(p.get('score', 0.0))
            if best_score is None:
                best_score = score
            suggested.append((tok, score))
            if tok.lower() == original_lower:
                found = True

        # Marquer comme suspect si original absent du top-k ET meilleur score raisonnablement > au seuil
        # Heuristique: si best_score > 0.25 et original pas dans top-k, probabilité faible pour original.
        if not found and (best_score or 0.0) > 0.25:
            anomalies.append({
                'token': original,
                'position': i,
                'suggestions': suggested[:topk]
            })

    return anomalies


def spelling_anomalies(sentence: str, allowlist: set, spell: Optional[SpellChecker]) -> List[Dict]:
    if not SPELLCHECK_AVAILABLE or spell is None:
        return []
    anomalies: List[Dict] = []
    tokens = sentence.split()
    # Normaliser pour le correcteur (minuscule), mais garder l'original pour le report
    for i, original in enumerate(tokens):
        if not WORD_REGEX.match(original):
            continue
        low = original.lower()
        if low in allowlist:
            continue
        if low in CONFUSION_MAP:
            anomalies.append({
                'token': original,
                'position': i,
                'suggestions': [(CONFUSION_MAP[low], 0.99)]
            })
            continue
        # Ignorer mots très courts
        if len(low) <= 2:
            continue
        if low not in spell:
            # Proposer 3 corrections probables
            suggs = list(spell.candidates(low))
            # Heuristique: prioriser similarité (difflib) décroissante
            scored = []
            for s in suggs:
                sim = difflib.SequenceMatcher(None, low, s).ratio()
                scored.append((s, float(sim)))
            scored.sort(key=lambda x: x[1], reverse=True)
            anomalies.append({
                'token': original,
                'position': i,
                'suggestions': scored[:5]
            })
    return anomalies


def ensure_output_path(filename: str) -> Path:
    if OUTPUT_MANAGER:
        # Utiliser un sous-dossier d'analyse si possible
        base = Path("output/analysis")
        base.mkdir(parents=True, exist_ok=True)
        return base / filename
    else:
        p = Path("output/analysis")
        p.mkdir(parents=True, exist_ok=True)
        return p / filename


def main():
    parser = argparse.ArgumentParser(description="Détecteur d'erreurs de transcription FR (plausibilité sémantique + orthographe)")
    parser.add_argument("input_file", help="Fichier texte/markdown/json à analyser")
    parser.add_argument("--topk", type=int, default=5, help="Top-k prédictions pour validation")
    parser.add_argument("--max-sentences", type=int, default=500, help="Limite de phrases à analyser")
    parser.add_argument("--allowlist", type=str, help="Fichier de mots à ignorer (mots métiers)")
    args = parser.parse_args()

    inp = Path(args.input_file)
    if not inp.exists():
        print(f"❌ Fichier introuvable: {inp}")
        return 1

    # Charger texte (JSON: extraire champs texte si possible)
    text = read_text_from_file(inp)
    if inp.suffix.lower() == ".json":
        try:
            data = json.loads(text)
            # Heuristique: chercher transcription complète
            text = (
                data.get('transcription', {}).get('text')
                or data.get('transcription', {}).get('full_text')
                or data.get('text')
                or text
            )
        except Exception:
            pass

    sentences = split_sentences(text)
    if args.max_sentences and len(sentences) > args.max_sentences:
        sentences = sentences[:args.max_sentences]

    allowlist = load_allowlist(Path(args.allowlist)) if args.allowlist else set()

    print(f"🔎 Analyse de {len(sentences)} phrases (topk={args.topk})...")

    # Modèle FR fill-mask
    nlp_fill = pipeline("fill-mask", model="camembert-base", device=0 if torch.backends.mps.is_available() else -1)
    # Correcteur FR
    spell = SpellChecker(language='fr') if SPELLCHECK_AVAILABLE else None

    report: List[Dict] = []
    total_anomalies = 0
    start = time.time()

    for idx, sent in enumerate(sentences, 1):
        anomalies = mask_and_score_sentence(nlp_fill, sent, args.topk, allowlist)
        # Ajouter anomalies d'orthographe/confusions évidentes
        anomalies += spelling_anomalies(sent, allowlist, spell)
        if anomalies:
            total_anomalies += len(anomalies)
            report.append({
                'sentence_index': idx,
                'sentence': sent,
                'anomalies': anomalies
            })

    duration = time.time() - start
    print(f"✅ Analyse terminée en {duration:.2f}s — {total_anomalies} anomalies potentielles")

    # Sauvegarde rapport Markdown
    out_name = f"transcription_anomalies_{int(time.time())}.md"
    out_path = ensure_output_path(out_name)
    with out_path.open('w', encoding='utf-8') as f:
        f.write(f"# 🔍 Anomalies potentielles de transcription\n\n")
        f.write(f"- Fichier analysé: {inp.name}\n")
        f.write(f"- Phrases analysées: {len(sentences)}\n")
        f.write(f"- Anomalies détectées: {total_anomalies}\n")
        f.write(f"- Modèle: camembert-base (fill-mask)\n")
        f.write(f"- top-k: {args.topk}\n\n")

        for item in report:
            f.write(f"## Phrase {item['sentence_index']}\n")
            f.write(f"> {item['sentence']}\n\n")
            for a in item['anomalies']:
                sugg = ", ".join([f"{tok} ({score:.2f})" for tok, score in a['suggestions']])
                f.write(f"- Mot suspect: `{a['token']}` — suggestions: {sugg}\n")
            f.write("\n")

    print(f"📄 Rapport: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


