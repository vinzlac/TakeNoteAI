#!/usr/bin/env python3
"""
Script pour générer une transcription lisible depuis un fichier JSON RAG
Format: timestamp, personne (si disponible), texte
"""

import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

# Import du gestionnaire de sortie
try:
    from output_manager import OutputManager
    OUTPUT_MANAGER = OutputManager()
except ImportError:
    print("⚠️  output_manager.py non trouvé, utilisation des chemins par défaut")
    OUTPUT_MANAGER = None


def format_timestamp(seconds: float) -> str:
    """Formate un timestamp en format HH:MM:SS."""
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def extract_speaker(segment: dict) -> Optional[str]:
    """Extrait le nom du locuteur depuis un segment."""
    # Vérifier différents champs possibles
    if 'speaker' in segment:
        return segment['speaker']
    if 'speaker_label' in segment:
        return segment['speaker_label']
    if 'speaker_id' in segment:
        return f"Speaker {segment['speaker_id']}"
    return None


def generate_readable_transcript(json_file: str, output_file: Optional[str] = None) -> str:
    """
    Génère une transcription lisible depuis un fichier JSON RAG.
    
    Args:
        json_file: Chemin vers le fichier JSON de transcription
        output_file: Chemin de sortie (optionnel)
    
    Returns:
        Chemin du fichier généré
    """
    json_path = Path(json_file)
    
    if not json_path.exists():
        raise FileNotFoundError(f"Le fichier {json_file} n'existe pas")
    
    # Charger le JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extraire les métadonnées
    metadata = data.get('metadata', {})
    filename = metadata.get('filename', json_path.stem)
    
    # Extraire les segments
    transcription = data.get('transcription', {})
    segments = transcription.get('segments', [])
    
    if not segments:
        raise ValueError("Aucun segment trouvé dans le fichier JSON")
    
    # Calculer la durée à partir du dernier segment si non disponible dans metadata
    duration = metadata.get('duration', 0)
    if duration == 0 and segments:
        last_segment = max(segments, key=lambda x: x.get('end', 0))
        duration = last_segment.get('end', 0)
    
    # Générer le nom de sortie si non fourni
    if output_file is None:
        base_name = json_path.stem.replace('_advanced_rag', '').replace('_advanced_rag_keywords', '')
        # Créer un répertoire pour les transcriptions lisibles
        readable_dir = Path("output/readable_transcripts")
        readable_dir.mkdir(parents=True, exist_ok=True)
        output_file = str(readable_dir / f"{base_name}_transcript.txt")
    else:
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file = str(output_file)
    
    # Générer la transcription
    lines = []
    lines.append(f"# Transcription: {filename}")
    lines.append(f"# Durée: {format_timestamp(duration)}")
    lines.append(f"# Généré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("=" * 80)
    lines.append("")
    
    for segment in segments:
        start = segment.get('start', 0)
        end = segment.get('end', 0)
        text = segment.get('text', '').strip()
        speaker = extract_speaker(segment)
        
        if not text:
            continue
        
        # Format: [HH:MM:SS] [Personne:] Texte
        timestamp_str = format_timestamp(start)
        
        if speaker:
            lines.append(f"[{timestamp_str}] {speaker}: {text}")
        else:
            lines.append(f"[{timestamp_str}] {text}")
    
    # Écrire le fichier
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"✅ Transcription lisible générée: {output_file}")
    print(f"📊 Statistiques:")
    print(f"   - Segments: {len(segments)}")
    print(f"   - Durée totale: {format_timestamp(duration)}")
    
    return output_file


def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(
        description="Génère une transcription lisible depuis un fichier JSON RAG",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  %(prog)s transcription.json
  %(prog)s transcription.json -o ma_transcription.txt
  %(prog)s output/transcriptions/*.json
        """
    )
    
    parser.add_argument("json_file", help="Fichier JSON de transcription RAG")
    parser.add_argument("-o", "--output", help="Fichier de sortie (optionnel)")
    
    args = parser.parse_args()
    
    try:
        output_file = generate_readable_transcript(args.json_file, args.output)
        print(f"\n📄 Fichier disponible: {output_file}")
        return 0
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
