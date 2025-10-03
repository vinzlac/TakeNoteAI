#!/usr/bin/env python3
"""
Script pour configurer le token Hugging Face pour pyannote.audio
"""

import os
from pathlib import Path
from huggingface_hub import login

def setup_huggingface_token():
    """Configure le token Hugging Face."""
    print("🔑 Configuration du token Hugging Face pour pyannote.audio")
    print("=" * 60)
    
    # Vérifier si le token est déjà configuré
    token_file = Path.home() / ".cache" / "huggingface" / "token"
    if token_file.exists():
        print("✅ Token Hugging Face déjà configuré")
        return True
    
    print("📋 Pour utiliser pyannote.audio, vous devez :")
    print("1. Aller sur https://huggingface.co/settings/tokens")
    print("2. Créer un nouveau token (type: Read)")
    print("3. Copier le token")
    print()
    
    token = input("🔑 Collez votre token Hugging Face ici: ").strip()
    
    if not token:
        print("❌ Token vide, configuration annulée")
        return False
    
    try:
        # Tester le token
        login(token=token)
        print("✅ Token configuré avec succès!")
        print("💡 Vous pouvez maintenant utiliser pyannote.audio")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la configuration du token: {e}")
        return False

if __name__ == "__main__":
    setup_huggingface_token()
