#!/usr/bin/env python3
"""
Script pour tester la configuration du token Hugging Face
"""

def test_huggingface_token():
    """Teste si le token Hugging Face est configuré correctement."""
    try:
        from huggingface_hub import whoami, login
        
        print("🔍 Test de la configuration Hugging Face...")
        
        # Essayer de récupérer les informations utilisateur
        try:
            user_info = whoami()
            print(f"✅ Token configuré correctement!")
            print(f"👤 Utilisateur: {user_info.get('name', 'Inconnu')}")
            print(f"📧 Email: {user_info.get('email', 'Non disponible')}")
            return True
            
        except Exception as e:
            print(f"❌ Token non configuré ou invalide: {e}")
            print("\n💡 Pour configurer le token:")
            print("1. Allez sur https://huggingface.co/settings/tokens")
            print("2. Créez un nouveau token (type: Read)")
            print("3. Exécutez: huggingface-cli login")
            print("4. Collez votre token")
            return False
            
    except ImportError:
        print("❌ huggingface_hub non installé")
        return False

def test_pyannote_access():
    """Teste l'accès aux modèles pyannote.audio."""
    try:
        from pyannote.audio import Pipeline
        
        print("\n🎤 Test d'accès aux modèles pyannote.audio...")
        
        # Essayer de charger le pipeline
        pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1")
        print("✅ Accès aux modèles pyannote.audio réussi!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur d'accès aux modèles: {e}")
        print("💡 Assurez-vous d'avoir accepté les conditions d'utilisation:")
        print("   https://huggingface.co/pyannote/speaker-diarization-3.1")
        return False

if __name__ == "__main__":
    print("🧪 Test de configuration Hugging Face pour TakeNote AI")
    print("=" * 60)
    
    # Test du token
    token_ok = test_huggingface_token()
    
    # Test d'accès aux modèles si le token est OK
    if token_ok:
        test_pyannote_access()
    
    print("\n" + "=" * 60)
    if token_ok:
        print("🎉 Configuration réussie! Vous pouvez utiliser pyannote.audio")
    else:
        print("⚠️  Configuration incomplète. Suivez les instructions ci-dessus")
