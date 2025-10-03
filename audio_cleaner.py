#!/usr/bin/env python3
"""
Script de nettoyage audio - Nettoie les fichiers audio pour améliorer la transcription
en supprimant le bruit, normalisant le volume et optimisant la qualité.
"""

import os
import sys
import argparse
from pathlib import Path
import ffmpeg


def clean_audio(input_path, output_path=None, noise_reduction=True, normalize=True):
    """
    Nettoie un fichier audio pour optimiser la transcription Whisper.
    
    Args:
        input_path (str): Chemin vers le fichier audio d'entrée
        output_path (str, optional): Chemin de sortie. Si None, génère automatiquement
        noise_reduction (bool): Appliquer la réduction de bruit
        normalize (bool): Normaliser le volume
    
    Returns:
        str: Chemin du fichier de sortie
    """
    input_path = Path(input_path)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Le fichier {input_path} n'existe pas")
    
    # Génération du nom de sortie si non fourni
    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}_cleaned.mp3"
    else:
        output_path = Path(output_path)
    
    try:
        # Configuration de base pour le nettoyage
        input_stream = ffmpeg.input(str(input_path))
        
        # Filtres de nettoyage
        filters = []
        
        # Réduction de bruit (si activée)
        if noise_reduction:
            filters.append("afftdn=nf=-25")  # Réduction de bruit FFT
        
        # Normalisation du volume (si activée)
        if normalize:
            filters.append("loudnorm=I=-16:TP=-1.5:LRA=11")  # Normalisation LUFS
        
        # Filtre de haute qualité pour la parole
        filters.extend([
            "highpass=f=80",  # Filtre passe-haut pour éliminer les basses fréquences
            "lowpass=f=8000",  # Filtre passe-bas pour éliminer les hautes fréquences
            "compand=attacks=0.3:decays=0.8:points=-90/-90|-60/-60|-40/-20|-30/-8:gain=5"  # Compression dynamique
        ])
        
        # Application des filtres
        if filters:
            audio = input_stream.audio.filter("|".join(filters))
        else:
            audio = input_stream.audio
        
        # Configuration de sortie optimisée pour Whisper
        (
            ffmpeg
            .output(
                audio,
                str(output_path),
                acodec='mp3',
                ac=1,  # Mono
                ar=16000,  # 16kHz optimal pour Whisper
                ab='64k',  # Bitrate réduit mais suffisant
                **{'q:a': 2}
            )
            .overwrite_output()
            .run(quiet=True)
        )
        
        print(f"✅ Nettoyage réussi: {input_path.name} -> {output_path.name}")
        return str(output_path)
        
    except ffmpeg.Error as e:
        print(f"❌ Erreur lors du nettoyage: {e}")
        raise


def analyze_audio(input_path):
    """
    Analyse un fichier audio pour diagnostiquer les problèmes potentiels.
    
    Args:
        input_path (str): Chemin vers le fichier audio
    """
    input_path = Path(input_path)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Le fichier {input_path} n'existe pas")
    
    try:
        # Récupération des informations du fichier
        probe = ffmpeg.probe(str(input_path))
        audio_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
        
        if not audio_stream:
            print("❌ Aucun flux audio trouvé dans le fichier")
            return
        
        print(f"📊 Analyse du fichier: {input_path.name}")
        print(f"   Format: {audio_stream.get('codec_name', 'Inconnu')}")
        print(f"   Durée: {float(probe['format']['duration']):.2f} secondes")
        print(f"   Taille: {int(probe['format']['size']) / 1024 / 1024:.2f} MB")
        print(f"   Sample rate: {audio_stream.get('sample_rate', 'Inconnu')} Hz")
        print(f"   Canaux: {audio_stream.get('channels', 'Inconnu')}")
        print(f"   Bitrate: {audio_stream.get('bit_rate', 'Inconnu')} bps")
        
        # Recommandations
        sample_rate = int(audio_stream.get('sample_rate', 0))
        channels = int(audio_stream.get('channels', 0))
        
        recommendations = []
        if sample_rate < 16000:
            recommendations.append("Sample rate trop bas (< 16kHz)")
        if channels > 1:
            recommendations.append("Fichier stéréo - conversion en mono recommandée")
        if int(audio_stream.get('bit_rate', 0)) < 64000:
            recommendations.append("Bitrate faible - qualité audio potentiellement dégradée")
        
        if recommendations:
            print("⚠️  Recommandations:")
            for rec in recommendations:
                print(f"   - {rec}")
        else:
            print("✅ Fichier audio de bonne qualité")
            
    except ffmpeg.Error as e:
        print(f"❌ Erreur lors de l'analyse: {e}")


def main():
    parser = argparse.ArgumentParser(description="Nettoie les fichiers audio pour optimiser la transcription")
    parser.add_argument("input", help="Fichier audio d'entrée")
    parser.add_argument("-o", "--output", help="Fichier de sortie (optionnel)")
    parser.add_argument("--no-noise-reduction", action="store_true", 
                       help="Désactiver la réduction de bruit")
    parser.add_argument("--no-normalize", action="store_true", 
                       help="Désactiver la normalisation du volume")
    parser.add_argument("--analyze", action="store_true", 
                       help="Analyser le fichier sans le nettoyer")
    
    args = parser.parse_args()
    
    try:
        if args.analyze:
            analyze_audio(args.input)
        else:
            output_file = clean_audio(
                args.input, 
                args.output, 
                noise_reduction=not args.no_noise_reduction,
                normalize=not args.no_normalize
            )
            print(f"📁 Fichier nettoyé sauvegardé: {output_file}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

