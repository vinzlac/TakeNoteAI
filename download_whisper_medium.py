#!/usr/bin/env python3
"""
Script pour télécharger uniquement le modèle 'medium' de Whisper
"""

import whisper
import sys
from pathlib import Path

def download_whisper_medium():
    """
    Télécharge uniquement le modèle 'medium' de Whisper.
    """
    try:
        print("🔄 Téléchargement du modèle Whisper 'medium'...")
        print("   (Cela peut prendre quelques minutes selon votre connexion)")
        
        # Forcer le téléchargement du modèle medium
        model = whisper.load_model("medium")
        
        print("✅ Modèle 'medium' téléchargé avec succès!")
        print(f"📁 Emplacement: {Path.home()}/.cache/whisper/")
        
        # Afficher les informations du modèle
        print(f"📊 Informations du modèle:")
        print(f"   - Nom: {model.dims}")
        print(f"   - Taille: ~1.4 GB")
        print(f"   - Qualité: Bonne (équilibre vitesse/qualité)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du téléchargement: {e}")
        return False

def main():
    """Fonction principale."""
    print("🎤 TakeNote AI - Téléchargement du modèle Whisper 'medium'")
    print("=" * 60)
    
    success = download_whisper_medium()
    
    if success:
        print("\n🎉 Téléchargement terminé!")
        print("💡 Vous pouvez maintenant utiliser le modèle 'medium' avec:")
        print("   python takenote.py votre_audio.mp3 -m medium")
        print("   python audio_transcriber.py votre_audio.mp3 -m medium")
    else:
        print("\n💥 Échec du téléchargement")
        sys.exit(1)

if __name__ == "__main__":
    main()
