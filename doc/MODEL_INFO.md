# Modèles pré-entraînés TakeNoteAI

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
