#!/usr/bin/env python3
"""
Script pour télécharger et configurer les modèles pré-entraînés
"""

import os
import sys
import subprocess
from pathlib import Path

def check_model_requirements():
    """Vérifie les prérequis pour les modèles."""
    print("🔍 Vérification des prérequis pour les modèles...")
    
    try:
        import torch
        import transformers
        import speechbrain
        print("✅ Modules requis disponibles")
        return True
    except ImportError as e:
        print(f"❌ Module manquant: {e}")
        print("💡 Installez les dépendances avec: ./install_advanced.sh")
        return False

def download_whisper_models():
    """Télécharge les modèles Whisper."""
    print("\n🤖 Téléchargement des modèles Whisper...")
    
    try:
        import whisper
        
        models = ["base", "medium"]
        for model_size in models:
            print(f"🔄 Téléchargement du modèle Whisper {model_size}...")
            model = whisper.load_model(model_size)
            print(f"✅ Modèle {model_size} téléchargé et prêt")
            
    except Exception as e:
        print(f"❌ Erreur téléchargement Whisper: {e}")

def download_speechbrain_models():
    """Télécharge les modèles SpeechBrain."""
    print("\n🎤 Téléchargement des modèles SpeechBrain...")
    
    try:
        from speechbrain.pretrained import EncoderDecoderASR
        
        # Modèle de transcription français
        print("🔄 Téléchargement du modèle SpeechBrain français...")
        model = EncoderDecoderASR.from_hparams(
            source="speechbrain/asr-crdnn-commonvoice-fr",
            savedir="pretrained_models/asr-crdnn-commonvoice-fr",
            run_opts={"device": "cpu"}
        )
        print("✅ Modèle SpeechBrain français téléchargé")
        
    except Exception as e:
        print(f"❌ Erreur téléchargement SpeechBrain: {e}")

def download_transformers_models():
    """Télécharge les modèles Transformers."""
    print("\n🧠 Téléchargement des modèles Transformers...")
    
    try:
        from sentence_transformers import SentenceTransformer
        
        # Modèle d'embeddings
        print("🔄 Téléchargement du modèle d'embeddings...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Modèle d'embeddings téléchargé")
        
    except Exception as e:
        print(f"❌ Erreur téléchargement Transformers: {e}")

def download_keybert_model():
    """Télécharge le modèle KeyBERT."""
    print("\n🔑 Configuration de KeyBERT...")
    
    try:
        from keybert import KeyBERT
        from sentence_transformers import SentenceTransformer
        
        # KeyBERT utilise SentenceTransformer en arrière-plan
        print("🔄 Configuration de KeyBERT...")
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        keybert_model = KeyBERT(model=embedding_model)
        print("✅ KeyBERT configuré")
        
    except Exception as e:
        print(f"❌ Erreur configuration KeyBERT: {e}")

def check_model_status():
    """Vérifie le statut des modèles."""
    print("\n📊 Statut des modèles:")
    print("-" * 30)
    
    # Vérifier Whisper
    try:
        import whisper
        models_dir = Path.home() / ".cache" / "whisper"
        if models_dir.exists():
            models = list(models_dir.glob("*.pt"))
            print(f"🤖 Whisper: {len(models)} modèle(s) téléchargé(s)")
        else:
            print("🤖 Whisper: Aucun modèle téléchargé")
    except:
        print("🤖 Whisper: Non disponible")
    
    # Vérifier SpeechBrain
    pretrained_dir = Path("pretrained_models")
    if pretrained_dir.exists():
        sb_models = [d for d in pretrained_dir.iterdir() if d.is_dir()]
        print(f"🎤 SpeechBrain: {len(sb_models)} modèle(s) téléchargé(s)")
    else:
        print("🎤 SpeechBrain: Aucun modèle téléchargé")
    
    # Vérifier Transformers cache
    cache_dir = Path.home() / ".cache" / "huggingface" / "transformers"
    if cache_dir.exists():
        model_dirs = [d for d in cache_dir.iterdir() if d.is_dir()]
        print(f"🧠 Transformers: {len(model_dirs)} modèle(s) en cache")
    else:
        print("🧠 Transformers: Aucun modèle en cache")

def create_model_info():
    """Crée un fichier d'information sur les modèles."""
    print("\n📝 Création du fichier d'information...")
    
    info_content = """# Modèles pré-entraînés TakeNoteAI

## Modèles utilisés

### 🤖 Whisper (Transcription)
- **Modèles**: base, medium, large
- **Taille**: ~74MB (base), ~769MB (medium), ~1550MB (large)
- **Téléchargement**: Automatique au premier usage
- **Cache**: `~/.cache/whisper/`

### 🎤 SpeechBrain (Transcription avancée)
- **Modèle**: speechbrain/asr-crdnn-commonvoice-fr
- **Taille**: ~565MB
- **Téléchargement**: Automatique au premier usage
- **Cache**: `pretrained_models/asr-crdnn-commonvoice-fr/`

### 🧠 Sentence Transformers (Embeddings)
- **Modèle**: all-MiniLM-L6-v2
- **Taille**: ~90MB
- **Usage**: Génération d'embeddings sémantiques
- **Cache**: Hugging Face cache

### 🔑 KeyBERT (Extraction de mots-clés)
- **Base**: Sentence Transformers
- **Usage**: Extraction de mots-clés métiers
- **Taille**: Réutilise all-MiniLM-L6-v2

## Téléchargement automatique

Les modèles se téléchargent automatiquement au premier usage :
```bash
python advanced_rag_transcription.py audio.mp3
```

## Téléchargement manuel

Pour télécharger tous les modèles d'avance :
```bash
python setup_models.py --download-all
```

## Gestion du cache

### Nettoyer le cache
```bash
# Cache Hugging Face
rm -rf ~/.cache/huggingface/

# Cache Whisper
rm -rf ~/.cache/whisper/

# Modèles SpeechBrain locaux
rm -rf pretrained_models/
```

### Taille du cache
Les modèles occupent environ 4GB au total :
- Whisper (medium): ~769MB
- SpeechBrain: ~565MB
- Transformers: ~90MB
- KeyBERT: Réutilise Transformers

## Recommandations

1. **Premier usage** : Les modèles se téléchargent automatiquement
2. **Développement** : Gardez les modèles en cache local
3. **Déploiement** : Téléchargez les modèles dans les pipelines CI/CD
4. **Backup** : Les modèles ne sont pas versionnés (voir .gitignore)
"""
    
    with open("MODEL_INFO.md", "w", encoding="utf-8") as f:
        f.write(info_content)
    
    print("✅ Fichier MODEL_INFO.md créé")

def main():
    """Fonction principale."""
    print("🚀 Configuration des modèles pré-entraînés TakeNoteAI")
    print("=" * 60)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--download-all":
        print("📥 Mode téléchargement complet activé")
        
        if not check_model_requirements():
            return 1
        
        download_whisper_models()
        download_speechbrain_models()
        download_transformers_models()
        download_keybert_model()
        
        print("\n🎉 Tous les modèles ont été téléchargés !")
    
    else:
        print("📋 Mode information activé")
        print("💡 Utilisez --download-all pour télécharger tous les modèles")
    
    check_model_status()
    create_model_info()
    
    print(f"\n✅ Configuration terminée !")
    print(f"📖 Consultez MODEL_INFO.md pour plus d'informations")
    
    return 0

if __name__ == "__main__":
    exit(main())
