#!/usr/bin/env python3
"""
TakeNote AI - Application principale pour convertir les fichiers audio en texte
Orchestre les étapes de conversion, nettoyage et transcription.
"""

import os
import sys
import argparse
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Import des modules locaux
from audio_converter import convert_audio
from audio_cleaner import clean_audio, analyze_audio
from audio_transcriber import transcribe_audio


class TakeNoteProcessor:
    """Classe principale pour traiter les fichiers audio."""
    
    def __init__(self, work_dir=None):
        """
        Initialise le processeur.
        
        Args:
            work_dir (str, optional): Répertoire de travail temporaire
        """
        self.work_dir = Path(work_dir) if work_dir else Path(tempfile.mkdtemp(prefix="takenote_"))
        self.work_dir.mkdir(exist_ok=True)
        
        # Fichiers temporaires
        self.converted_file = None
        self.cleaned_file = None
        self.final_output = None
        
        print(f"📁 Répertoire de travail: {self.work_dir}")
    
    def process_audio(self, input_path, output_path=None, 
                     convert_quality="high", 
                     clean_audio_flag=True,
                     whisper_model="base",
                     language=None,
                     output_format="txt",
                     keep_intermediate=False):
        """
        Traite un fichier audio complet : conversion -> nettoyage -> transcription.
        
        Args:
            input_path (str): Fichier audio d'entrée
            output_path (str, optional): Fichier de sortie final
            convert_quality (str): Qualité de conversion
            clean_audio_flag (bool): Activer le nettoyage audio
            whisper_model (str): Modèle Whisper à utiliser
            language (str, optional): Langue pour la transcription
            output_format (str): Format de sortie
            keep_intermediate (bool): Garder les fichiers intermédiaires
        
        Returns:
            str: Chemin du fichier de sortie final
        """
        input_path = Path(input_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Le fichier {input_path} n'existe pas")
        
        print(f"🚀 Début du traitement: {input_path.name}")
        print(f"   Taille: {input_path.stat().st_size / 1024 / 1024:.2f} MB")
        
        try:
            # Étape 1: Conversion (si nécessaire)
            if input_path.suffix.lower() not in ['.mp3']:
                print("\n📦 Étape 1: Conversion audio...")
                self.converted_file = self.work_dir / f"converted_{input_path.stem}.mp3"
                convert_audio(str(input_path), str(self.converted_file), convert_quality)
                current_file = self.converted_file
            else:
                print("\n📦 Étape 1: Fichier déjà en MP3, conversion ignorée")
                current_file = input_path
            
            # Étape 2: Nettoyage (si activé)
            if clean_audio_flag:
                print("\n🧹 Étape 2: Nettoyage audio...")
                self.cleaned_file = self.work_dir / f"cleaned_{current_file.stem}.mp3"
                clean_audio(str(current_file), str(self.cleaned_file))
                current_file = self.cleaned_file
            else:
                print("\n🧹 Étape 2: Nettoyage audio désactivé")
            
            # Étape 3: Transcription
            print("\n🎤 Étape 3: Transcription Whisper...")
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = input_path.parent / f"{input_path.stem}_transcript_{timestamp}.{output_format}"
            
            self.final_output = transcribe_audio(
                str(current_file),
                str(output_path),
                whisper_model,
                language,
                output_format
            )
            
            print(f"\n✅ Traitement terminé avec succès!")
            print(f"📄 Transcription sauvegardée: {self.final_output}")
            
            # Nettoyage des fichiers temporaires
            if not keep_intermediate:
                self.cleanup()
            
            return str(self.final_output)
            
        except Exception as e:
            print(f"\n❌ Erreur lors du traitement: {e}")
            self.cleanup()
            raise
    
    def analyze_only(self, input_path):
        """
        Analyse uniquement un fichier audio sans le traiter.
        
        Args:
            input_path (str): Fichier audio à analyser
        """
        print(f"🔍 Analyse du fichier: {Path(input_path).name}")
        analyze_audio(input_path)
    
    def cleanup(self):
        """Nettoie les fichiers temporaires."""
        if self.work_dir.exists() and self.work_dir != Path.cwd():
            try:
                shutil.rmtree(self.work_dir)
                print(f"🧹 Fichiers temporaires supprimés: {self.work_dir}")
            except Exception as e:
                print(f"⚠️  Impossible de supprimer les fichiers temporaires: {e}")
    
    def __del__(self):
        """Destructeur - nettoie automatiquement."""
        self.cleanup()


def main():
    parser = argparse.ArgumentParser(
        description="TakeNote AI - Convertit les fichiers audio en texte",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  %(prog)s audio.mp3                    # Traitement complet
  %(prog)s audio.m4a -o resultat.txt    # Spécifier la sortie
  %(prog)s audio.mp3 --no-clean         # Sans nettoyage
  %(prog)s audio.mp3 --analyze-only     # Analyse uniquement
  %(prog)s audio.mp3 -m large -l fr     # Modèle large, français
        """
    )
    
    parser.add_argument("input", help="Fichier audio d'entrée")
    parser.add_argument("-o", "--output", help="Fichier de sortie (optionnel)")
    parser.add_argument("-q", "--quality", choices=["high", "medium", "low"], 
                       default="high", help="Qualité de conversion (défaut: high)")
    parser.add_argument("--no-clean", action="store_true", 
                       help="Désactiver le nettoyage audio")
    parser.add_argument("-m", "--model", choices=["tiny", "base", "small", "medium", "large"], 
                       default="base", help="Modèle Whisper (défaut: base)")
    parser.add_argument("-l", "--language", help="Code langue (ex: fr, en)")
    parser.add_argument("-f", "--format", choices=["txt", "json", "srt", "vtt"], 
                       default="txt", help="Format de sortie (défaut: txt)")
    parser.add_argument("--keep-intermediate", action="store_true", 
                       help="Garder les fichiers intermédiaires")
    parser.add_argument("--analyze-only", action="store_true", 
                       help="Analyser le fichier sans le traiter")
    parser.add_argument("--work-dir", help="Répertoire de travail temporaire")
    
    args = parser.parse_args()
    
    try:
        processor = TakeNoteProcessor(args.work_dir)
        
        if args.analyze_only:
            processor.analyze_only(args.input)
        else:
            output_file = processor.process_audio(
                args.input,
                args.output,
                args.quality,
                not args.no_clean,
                args.model,
                args.language,
                args.format,
                args.keep_intermediate
            )
            
            print(f"\n🎉 Succès! Votre transcription est prête: {output_file}")
        
    except KeyboardInterrupt:
        print("\n⏹️  Traitement interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erreur fatale: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

