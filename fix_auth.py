#!/usr/bin/env python3
"""
Script pour corriger les problèmes d'authentification et d'avertissements
"""

import os
import warnings
from pathlib import Path

def suppress_warnings():
    """Supprime les avertissements dépréciés."""
    print("🔧 Configuration de la suppression des avertissements...")
    
    # Supprimer les avertissements TorchAudio
    warnings.filterwarnings("ignore", category=UserWarning, module="torchaudio")
    warnings.filterwarnings("ignore", category=UserWarning, module="speechbrain")
    warnings.filterwarnings("ignore", category=UserWarning, module="whisper")
    
    # Supprimer les avertissements de dépréciation
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    
    print("✅ Avertissements supprimés")

def setup_huggingface_auth():
    """Configure l'authentification Hugging Face."""
    print("🔧 Configuration de l'authentification Hugging Face...")
    
    # Vérifier si le token existe
    token_file = Path.home() / ".cache" / "huggingface" / "token"
    if token_file.exists():
        print("✅ Token Hugging Face trouvé")
        return True
    
    print("⚠️  Token Hugging Face non trouvé")
    print("💡 Pour utiliser SpeechBrain, vous devez :")
    print("   1. Créer un compte sur https://huggingface.co")
    print("   2. Générer un token sur https://huggingface.co/settings/tokens")
    print("   3. Lancer : huggingface-cli login")
    
    return False

def fix_model_paths():
    """Corrige les chemins des modèles."""
    print("🔧 Configuration des chemins des modèles...")
    
    # Créer les dossiers nécessaires
    Path("pretrained_models").mkdir(exist_ok=True)
    Path("model_checkpoints").mkdir(exist_ok=True)
    
    print("✅ Dossiers de modèles créés")

def main():
    """Fonction principale."""
    print("🚀 Correction des problèmes d'authentification et d'avertissements")
    print("=" * 60)
    
    # Supprimer les avertissements
    suppress_warnings()
    
    # Configurer l'authentification
    auth_ok = setup_huggingface_auth()
    
    # Corriger les chemins
    fix_model_paths()
    
    print("\n✅ Configuration terminée!")
    
    if not auth_ok:
        print("\n⚠️  Recommandation :")
        print("   Pour éviter les erreurs SpeechBrain, configurez l'authentification :")
        print("   huggingface-cli login")
        print("\n   Ou utilisez directement Whisper :")
        print("   python advanced_rag_transcription.py audio.mp3 --transcription-model whisper")

if __name__ == "__main__":
    main()
