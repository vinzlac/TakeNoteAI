#!/usr/bin/env python3
"""
Script de nettoyage audio - Nettoie les fichiers audio pour améliorer la transcription
en supprimant le bruit, normalisant le volume et optimisant la qualité.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path


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
        # Construction de la commande FFmpeg
        cmd = [
            'ffmpeg',
            '-i', str(input_path),
            '-y'  # Overwrite output
        ]
        
        # Filtres de nettoyage
        filters = []
        
        # Filtres de base pour la parole (toujours appliqués)
        filters.extend([
            "highpass=f=80",  # Filtre passe-haut pour éliminer les basses fréquences
            "lowpass=f=8000",  # Filtre passe-bas pour éliminer les hautes fréquences
        ])
        
        # Réduction de bruit (si activée)
        if noise_reduction:
            filters.append("anlmdn=s=0.0001:p=0.02")  # Réduction de bruit non-locale
        
        # Normalisation du volume (si activée)
        if normalize:
            filters.append("volume=2.0")  # Normalisation simple
        
        # Ajouter les filtres à la commande
        if filters:
            cmd.extend(['-af', ','.join(filters)])
        
        # Configuration de sortie optimisée pour Whisper
        cmd.extend([
            '-acodec', 'mp3',
            '-ac', '1',  # Mono
            '-ar', '16000',  # 16kHz optimal pour Whisper
            '-ab', '64k',  # Bitrate réduit mais suffisant
            '-q:a', '2',
            str(output_path)
        ])
        
        # Exécution de la commande
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Erreur FFmpeg: {result.stderr}")
            raise subprocess.CalledProcessError(result.returncode, cmd, result.stderr)
        
        print(f"✅ Nettoyage réussi: {input_path.name} -> {output_path.name}")
        return str(output_path)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors du nettoyage: {e}")
        raise
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
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
        # Récupération des informations du fichier avec ffprobe
        cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', str(input_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Erreur lors de l'analyse: {result.stderr}")
            return
        
        import json
        probe = json.loads(result.stdout)
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
            
    except Exception as e:
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

