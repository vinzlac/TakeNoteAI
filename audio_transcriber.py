#!/usr/bin/env python3
"""
Script de transcription audio - Convertit les fichiers audio en texte via Whisper
"""

import os
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime
import whisper


def transcribe_audio(input_path, output_path=None, model_size="base", language=None, 
                    output_format="txt", include_timestamps=False):
    """
    Transcrit un fichier audio en texte via Whisper.
    
    Args:
        input_path (str): Chemin vers le fichier audio
        output_path (str, optional): Chemin de sortie. Si None, génère automatiquement
        model_size (str): Taille du modèle Whisper ("tiny", "base", "small", "medium", "large")
        language (str, optional): Code langue (ex: "fr", "en"). Si None, détection automatique
        output_format (str): Format de sortie ("txt", "json", "srt", "vtt")
        include_timestamps (bool): Inclure les timestamps dans la sortie
    
    Returns:
        str: Chemin du fichier de sortie
    """
    input_path = Path(input_path)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Le fichier {input_path} n'existe pas")
    
    # Vérification de l'extension
    if input_path.suffix.lower() not in ['.mp3', '.m4a', '.wav', '.flac', '.aac', '.ogg']:
        raise ValueError(f"Format non supporté: {input_path.suffix}")
    
    # Génération du nom de sortie si non fourni
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = input_path.parent / f"{input_path.stem}_transcript_{timestamp}.{output_format}"
    else:
        output_path = Path(output_path)
    
    try:
        print(f"🔄 Chargement du modèle Whisper '{model_size}'...")
        model = whisper.load_model(model_size)
        
        print(f"🎤 Transcription en cours: {input_path.name}")
        print("   (Cela peut prendre quelques minutes selon la durée du fichier)")
        
        # Transcription
        result = model.transcribe(
            str(input_path),
            language=language,
            verbose=True
        )
        
        # Sauvegarde selon le format demandé
        if output_format == "txt":
            save_as_text(result, output_path, include_timestamps)
        elif output_format == "json":
            save_as_json(result, output_path)
        elif output_format == "srt":
            save_as_srt(result, output_path)
        elif output_format == "vtt":
            save_as_vtt(result, output_path)
        else:
            raise ValueError(f"Format de sortie non supporté: {output_format}")
        
        print(f"✅ Transcription réussie: {input_path.name} -> {output_path.name}")
        print(f"📊 Statistiques:")
        print(f"   - Durée: {result.get('duration', 0):.2f} secondes")
        print(f"   - Langue détectée: {result.get('language', 'Inconnue')}")
        print(f"   - Longueur du texte: {len(result.get('text', ''))} caractères")
        
        return str(output_path)
        
    except Exception as e:
        print(f"❌ Erreur lors de la transcription: {e}")
        raise


def save_as_text(result, output_path, include_timestamps=False):
    """Sauvegarde la transcription en format texte simple."""
    with open(output_path, 'w', encoding='utf-8') as f:
        if include_timestamps and 'segments' in result:
            for segment in result['segments']:
                start_time = format_time(segment['start'])
                end_time = format_time(segment['end'])
                f.write(f"[{start_time} - {end_time}] {segment['text'].strip()}\n\n")
        else:
            f.write(result['text'])


def save_as_json(result, output_path):
    """Sauvegarde la transcription en format JSON."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


def save_as_srt(result, output_path):
    """Sauvegarde la transcription en format SRT (sous-titres)."""
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, segment in enumerate(result.get('segments', []), 1):
            start_time = format_time_srt(segment['start'])
            end_time = format_time_srt(segment['end'])
            text = segment['text'].strip()
            
            f.write(f"{i}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{text}\n\n")


def save_as_vtt(result, output_path):
    """Sauvegarde la transcription en format VTT (WebVTT)."""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("WEBVTT\n\n")
        
        for segment in result.get('segments', []):
            start_time = format_time_vtt(segment['start'])
            end_time = format_time_vtt(segment['end'])
            text = segment['text'].strip()
            
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{text}\n\n")


def format_time(seconds):
    """Formate le temps en HH:MM:SS."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def format_time_srt(seconds):
    """Formate le temps pour SRT (HH:MM:SS,mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def format_time_vtt(seconds):
    """Formate le temps pour VTT (HH:MM:SS.mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def list_available_models():
    """Affiche la liste des modèles Whisper disponibles."""
    models = ["tiny", "base", "small", "medium", "large"]
    print("📋 Modèles Whisper disponibles:")
    for model in models:
        print(f"   - {model}")
    print("\n💡 Recommandations:")
    print("   - tiny/base: Rapide, qualité correcte")
    print("   - small/medium: Équilibré vitesse/qualité")
    print("   - large: Meilleure qualité, plus lent")


def main():
    parser = argparse.ArgumentParser(description="Transcrit les fichiers audio en texte via Whisper")
    parser.add_argument("input", help="Fichier audio d'entrée")
    parser.add_argument("-o", "--output", help="Fichier de sortie (optionnel)")
    parser.add_argument("-m", "--model", choices=["tiny", "base", "small", "medium", "large"], 
                       default="base", help="Modèle Whisper à utiliser (défaut: base)")
    parser.add_argument("-l", "--language", help="Code langue (ex: fr, en). Détection automatique si non spécifié")
    parser.add_argument("-f", "--format", choices=["txt", "json", "srt", "vtt"], 
                       default="txt", help="Format de sortie (défaut: txt)")
    parser.add_argument("--timestamps", action="store_true", 
                       help="Inclure les timestamps dans la sortie (format txt uniquement)")
    parser.add_argument("--list-models", action="store_true", 
                       help="Afficher la liste des modèles disponibles")
    
    args = parser.parse_args()
    
    if args.list_models:
        list_available_models()
        return
    
    try:
        output_file = transcribe_audio(
            args.input,
            args.output,
            args.model,
            args.language,
            args.format,
            args.timestamps
        )
        print(f"📁 Transcription sauvegardée: {output_file}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

