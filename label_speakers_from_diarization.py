#!/usr/bin/env python3
"""
Assigne des noms de locuteurs à une diarisation existante.
Heuristiques basées sur le contexte: début/fin (Antoine), segments courts/questions (Moi), reste (Cyril).
"""

import argparse
import json
from pathlib import Path
from datetime import datetime
import os
import torch

# Optimisations M4
if torch.backends.mps.is_available():
    torch.set_num_threads(14)
    os.environ["OMP_NUM_THREADS"] = "14"
    os.environ["MKL_NUM_THREADS"] = "14"
    os.environ["NUMEXPR_NUM_THREADS"] = "14"
    print("🚀 Optimisations Mac M4 activées")


QUESTION_STARTERS = (
    "est-ce", "tu", "vous", "quoi", "comment", "pourquoi",
    "combien", "quand", "où", "ok", "d'accord", "alors"
)


def format_time(seconds: float) -> str:
    """Formate le temps en HH:MM:SS."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def is_short_question(text: str) -> bool:
    """Détecte une question courte (intervention du candidat)."""
    if not text:
        return False
    lower = text.strip().lower()
    if "?" in lower and len(lower) <= 120:
        return True
    if len(lower) <= 80 and lower.startswith(QUESTION_STARTERS):
        return True
    return False


def assign_speaker_names(
    segments,
    early_seconds: int,
    late_seconds: int,
    name_early: str,
    name_main: str,
    name_short: str,
):
    """Assigne des noms de locuteurs aux segments."""
    if not segments:
        return []

    total_duration = max(seg.get("end", 0) for seg in segments)
    named_segments = []

    for seg in segments:
        start = seg.get("start", 0)
        end = seg.get("end", 0)
        text = seg.get("text", "").strip()

        if start <= early_seconds or start >= max(0, total_duration - late_seconds):
            speaker_name = name_early
        elif is_short_question(text):
            speaker_name = name_short
        else:
            speaker_name = name_main

        named_segments.append({
            **seg,
            "speaker_name": speaker_name,
            "start": start,
            "end": end,
            "text": text,
        })

    return named_segments


def save_as_text(named_segments, output_path: Path, source_name: str = "unknown"):
    """Sauvegarde en format texte compatible avec les parseurs existants."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    total_duration = max(seg.get("end", 0) for seg in named_segments) if named_segments else 0
    duration_str = format_time(total_duration)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# Transcription: {source_name}\n")
        f.write(f"# Durée: {duration_str}\n")
        f.write(f"# Généré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("===\n")

        for seg in named_segments:
            start_time = format_time(seg["start"])
            speaker_name = seg["speaker_name"]
            text = seg["text"]
            f.write(f"[{start_time}] {speaker_name}: {text}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Assigne des noms de locuteurs à une diarisation JSON",
    )
    parser.add_argument("input", help="Fichier JSON de diarisation (ex: *_speakers.json)")
    parser.add_argument("-o", "--output", help="Fichier de sortie (txt)")
    parser.add_argument("--early-seconds", type=int, default=300, help="Fenêtre début (sec) pour Antoine")
    parser.add_argument("--late-seconds", type=int, default=180, help="Fenêtre fin (sec) pour Antoine")
    parser.add_argument("--name-early", default="Antoine Gayte", help="Nom du locuteur début/fin")
    parser.add_argument("--name-main", default="Cyril Chalaud", help="Nom du locuteur principal")
    parser.add_argument("--name-short", default="Moi", help="Nom du locuteur interventions courtes")

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ Fichier introuvable: {input_path}")
        return 1

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    segments = data.get("segments", [])
    if not segments:
        print("❌ Aucun segment trouvé dans le JSON")
        return 1

    named_segments = assign_speaker_names(
        segments,
        early_seconds=args.early_seconds,
        late_seconds=args.late_seconds,
        name_early=args.name_early,
        name_main=args.name_main,
        name_short=args.name_short,
    )

    if args.output:
        output_path = Path(args.output)
    else:
        stem = input_path.stem.replace("_speakers", "")
        output_path = Path("output/readable_transcripts") / f"{stem}_transcript.txt"

    source_name = data.get("metadata", {}).get("source", input_path.name)
    save_as_text(named_segments, output_path, source_name=source_name)
    print(f"✅ Transcription nommée générée: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
