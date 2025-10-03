#!/usr/bin/env python3
"""
Script de conversion audio - Convertit les fichiers audio (mp3, m4a) en mp3 propre
pour optimiser la transcription Whisper.
"""

import os
import sys
import argparse
from pathlib import Path
import ffmpeg


def convert_audio(input_path, output_path=None, quality="high"):
    """
    Convertit un fichier audio en mp3 avec les paramètres optimaux pour Whisper.
    
    Args:
        input_path (str): Chemin vers le fichier audio d'entrée
        output_path (str, optional): Chemin de sortie. Si None, génère automatiquement
        quality (str): Qualité de conversion ("high", "medium", "low")
    
    Returns:
        str: Chemin du fichier de sortie
    """
    input_path = Path(input_path)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Le fichier {input_path} n'existe pas")
    
    # Vérification de l'extension
    if input_path.suffix.lower() not in ['.mp3', '.m4a', '.wav', '.flac', '.aac']:
        raise ValueError(f"Format non supporté: {input_path.suffix}")
    
    # Génération du nom de sortie si non fourni
    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}_converted.mp3"
    else:
        output_path = Path(output_path)
    
    # Paramètres de qualité
    quality_settings = {
        "high": {"bitrate": "192k", "sample_rate": 44100},
        "medium": {"bitrate": "128k", "sample_rate": 44100},
        "low": {"bitrate": "96k", "sample_rate": 22050}
    }
    
    settings = quality_settings.get(quality, quality_settings["high"])
    
    try:
        # Configuration ffmpeg pour une conversion optimale
        (
            ffmpeg
            .input(str(input_path))
            .output(
                str(output_path),
                acodec='mp3',
                ac=1,  # Mono pour Whisper
                ar=settings["sample_rate"],  # Sample rate
                ab=settings["bitrate"],  # Bitrate
                **{'q:a': 2}  # Qualité audio
            )
            .overwrite_output()
            .run(quiet=True)
        )
        
        print(f"✅ Conversion réussie: {input_path.name} -> {output_path.name}")
        return str(output_path)
        
    except ffmpeg.Error as e:
        print(f"❌ Erreur lors de la conversion: {e}")
        raise


def main():
    parser = argparse.ArgumentParser(description="Convertit les fichiers audio en mp3 propre")
    parser.add_argument("input", help="Fichier audio d'entrée (mp3, m4a, wav, flac, aac)")
    parser.add_argument("-o", "--output", help="Fichier de sortie (optionnel)")
    parser.add_argument("-q", "--quality", choices=["high", "medium", "low"], 
                       default="high", help="Qualité de conversion (défaut: high)")
    
    args = parser.parse_args()
    
    try:
        output_file = convert_audio(args.input, args.output, args.quality)
        print(f"📁 Fichier converti sauvegardé: {output_file}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

