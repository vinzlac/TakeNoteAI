#!/usr/bin/env python3
"""
Script générique pour télécharger n'importe quel modèle Whisper
Usage: python download_whisper_model.py <model_name>
"""

import whisper
import sys
import argparse
from pathlib import Path

# Modèles Whisper disponibles avec leurs informations
WHISPER_MODELS = {
    "tiny": {
        "size": "~39 MB",
        "description": "Très rapide, qualité basique",
        "use_case": "Tests rapides, ressources limitées"
    },
    "base": {
        "size": "~74 MB", 
        "description": "Rapide, qualité correcte",
        "use_case": "Usage général, équilibre vitesse/qualité"
    },
    "small": {
        "size": "~244 MB",
        "description": "Modéré, bonne qualité",
        "use_case": "Usage professionnel léger"
    },
    "medium": {
        "size": "~769 MB",
        "description": "Bon équilibre vitesse/qualité",
        "use_case": "Usage professionnel standard"
    },
    "large": {
        "size": "~1550 MB",
        "description": "Meilleure qualité, plus lent",
        "use_case": "Usage professionnel haute qualité"
    }
}

def list_available_models():
    """Affiche la liste des modèles Whisper disponibles avec leurs informations."""
    print("📋 Modèles Whisper disponibles:")
    print("=" * 80)
    
    for model_name, info in WHISPER_MODELS.items():
        print(f"🎤 {model_name.upper():<8} | {info['size']:<12} | {info['description']}")
        print(f"   💡 Usage: {info['use_case']}")
        print()

def download_whisper_model(model_name):
    """
    Télécharge un modèle Whisper spécifique.
    
    Args:
        model_name (str): Nom du modèle à télécharger
        
    Returns:
        bool: True si le téléchargement a réussi, False sinon
    """
    if model_name not in WHISPER_MODELS:
        print(f"❌ Erreur: Le modèle '{model_name}' n'existe pas.")
        print(f"📋 Modèles disponibles: {', '.join(WHISPER_MODELS.keys())}")
        return False
    
    model_info = WHISPER_MODELS[model_name]
    
    print(f"🎤 TakeNote AI - Téléchargement du modèle Whisper '{model_name}'")
    print("=" * 70)
    print(f"📊 Informations du modèle:")
    print(f"   - Taille: {model_info['size']}")
    print(f"   - Description: {model_info['description']}")
    print(f"   - Usage recommandé: {model_info['use_case']}")
    print()
    
    try:
        print(f"🔄 Téléchargement du modèle '{model_name}' en cours...")
        print("   (Cela peut prendre plusieurs minutes selon votre connexion)")
        print()
        
        # Forcer le téléchargement du modèle
        model = whisper.load_model(model_name)
        
        print(f"✅ Modèle '{model_name}' téléchargé avec succès!")
        print(f"📁 Emplacement: {Path.home()}/.cache/whisper/")
        print()
        
        # Afficher les informations techniques du modèle
        print(f"📊 Informations techniques:")
        print(f"   - Dimensions: {model.dims}")
        print(f"   - Taille réelle: {model_info['size']}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du téléchargement: {e}")
        return False

def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(
        description="Télécharge un modèle Whisper spécifique",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  %(prog)s tiny                    # Télécharge le modèle tiny
  %(prog)s base                    # Télécharge le modèle base  
  %(prog)s small                   # Télécharge le modèle small
  %(prog)s medium                  # Télécharge le modèle medium
  %(prog)s large                   # Télécharge le modèle large
  %(prog)s --list                  # Liste tous les modèles disponibles
        """
    )
    
    parser.add_argument(
        "model", 
        nargs="?", 
        help="Nom du modèle à télécharger (tiny, base, small, medium, large)"
    )
    parser.add_argument(
        "--list", 
        action="store_true", 
        help="Afficher la liste des modèles disponibles"
    )
    
    args = parser.parse_args()
    
    # Si --list est spécifié, afficher la liste et quitter
    if args.list:
        list_available_models()
        return
    
    # Si aucun modèle n'est spécifié, afficher l'aide
    if not args.model:
        parser.print_help()
        print("\n💡 Utilisez --list pour voir tous les modèles disponibles")
        sys.exit(1)
    
    # Télécharger le modèle spécifié
    success = download_whisper_model(args.model.lower())
    
    if success:
        print("🎉 Téléchargement terminé!")
        print(f"💡 Vous pouvez maintenant utiliser le modèle '{args.model}' avec:")
        print(f"   python takenote.py votre_audio.mp3 -m {args.model}")
        print(f"   python audio_transcriber.py votre_audio.mp3 -m {args.model}")
    else:
        print("💥 Échec du téléchargement")
        sys.exit(1)

if __name__ == "__main__":
    main()
