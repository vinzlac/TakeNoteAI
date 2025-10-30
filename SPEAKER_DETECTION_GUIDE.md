# 🎤 Guide de détection des speakers (locuteurs)

## ⚠️ Problème avec pyannote.audio

Le script `whisper_speaker_diarization.py` rencontre actuellement des problèmes de compatibilité avec PyTorch 2.8.0 et torchcodec. L'erreur `AudioDecoder is not defined` est liée à des dépendances FFmpeg manquantes.

## ✅ Solutions recommandées

### **Option 1 : Utiliser `whisper_balanced_diarization.py` (RECOMMANDÉ)**

Ce script offre la **meilleure qualité sans pyannote.audio** grâce à une approche équilibrée :

```bash
python whisper_balanced_diarization.py input/CallHugoRemoteAccelerator.mp3 -m large -l fr
```

**Avantages** :
- ✅ Pas de dépendances complexes
- ✅ Excellente qualité de détection
- ✅ Analyse multi-critères (pauses, énergie, texte)
- ✅ Compatible avec tous les systèmes

---

### **Option 2 : Utiliser `whisper_simple_diarization.py`**

Pour une approche plus rapide avec sensibilité ajustable :

```bash
python whisper_simple_diarization.py input/CallHugoRemoteAccelerator.mp3 -m large -l fr --sensitivity medium
```

**Sensibilités disponibles** :
- `high` : Détecte plus de changements de locuteurs
- `medium` : Équilibré (recommandé)
- `low` : Moins de changements, pour conversations fluides

---

### **Option 3 : Réparer pyannote.audio (Avancé)**

Si vous souhaitez vraiment utiliser pyannote.audio :

#### Étape 1 : Installer FFmpeg avec Homebrew
```bash
brew install ffmpeg@7
```

#### Étape 2 : Créer des liens symboliques
```bash
# Vérifier quelle version est installée
ffmpeg -version

# Créer les liens vers les bibliothèques FFmpeg
brew link ffmpeg@7
```

#### Étape 3 : Réinstaller les dépendances Python
```bash
source venv/bin/activate
pip uninstall -y torchcodec pyannote.audio
pip install --upgrade pyannote.audio
```

#### Étape 4 : Configurer le token Hugging Face
```bash
# Créer un token sur https://huggingface.co/settings/tokens
# Accepter les conditions sur https://huggingface.co/pyannote/speaker-diarization-3.1

export HF_TOKEN="votre_token_huggingface"
```

**Cependant**, cette approche est complexe et peut ne pas résoudre tous les problèmes de compatibilité.

---

## 📊 Comparaison des scripts disponibles

| Script | Qualité | Vitesse | Complexité | Status |
|--------|---------|---------|------------|--------|
| `whisper_speaker_diarization.py` | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ❌ Problème compatibilité |
| `whisper_balanced_diarization.py` | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ✅ **RECOMMANDÉ** |
| `whisper_simple_diarization.py` | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ✅ Fonctionne bien |
| `whisper_clean_diarization.py` | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ✅ Alternative simple |
| `whisper_pause_based_diarization.py` | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ✅ Basé sur pauses |

---

## 🚀 Commande recommandée pour votre cas

Pour transcrire `CallHugoRemoteAccelerator.mp3` avec détection des speakers :

```bash
# Meilleure option actuellement
python whisper_balanced_diarization.py input/CallHugoRemoteAccelerator.mp3 -m large -l fr -f json

# Ou en format texte simple
python whisper_balanced_diarization.py input/CallHugoRemoteAccelerator.mp3 -m large -l fr

# Ou avec sensibilité ajustable
python whisper_simple_diarization.py input/CallHugoRemoteAccelerator.mp3 -m large -l fr --sensitivity high
```

---

## 📝 Exemples de sortie

### Format texte (TXT)
```
[00:00:05 - 00:00:12] SPEAKER_00: Bonjour Hugo, merci d'avoir pris le temps.

[00:00:13 - 00:00:18] SPEAKER_01: Avec plaisir, je suis disponible.
```

### Format JSON
```json
{
  "metadata": {
    "language": "fr",
    "duration": 1562.5,
    "speakers": ["SPEAKER_00", "SPEAKER_01"],
    "method": "balanced_diarization"
  },
  "segments": [
    {
      "start": 5.0,
      "end": 12.0,
      "text": "Bonjour Hugo, merci d'avoir pris le temps.",
      "speaker": "SPEAKER_00",
      "confidence": -0.35
    }
  ]
}
```

---

## 💡 Conseils pour améliorer la détection

1. **Utilisez un modèle Whisper plus grand** : `large` ou `medium` pour meilleure précision
2. **Spécifiez la langue** : `-l fr` pour le français améliore la transcription
3. **Choisissez le bon format** : 
   - `txt` pour lecture humaine
   - `json` pour traitement automatique
   - `srt` pour sous-titres vidéo
4. **Ajustez la sensibilité** (avec `whisper_simple_diarization.py`) selon le type de conversation

---

## 🔧 Dépannage

### Erreur : "AudioDecoder is not defined"
➡️ Utilisez `whisper_balanced_diarization.py` au lieu de `whisper_speaker_diarization.py`

### Trop de changements de speakers détectés
➡️ Utilisez `--sensitivity low` avec `whisper_simple_diarization.py`

### Pas assez de changements de speakers détectés
➡️ Utilisez `--sensitivity high` avec `whisper_simple_diarization.py`

### Transcription lente avec modèle `large`
➡️ Utilisez le modèle `medium` ou `base` pour plus de rapidité

---

## 📚 Ressources

- [Documentation Whisper](https://github.com/openai/whisper)
- [Documentation pyannote.audio](https://github.com/pyannote/pyannote-audio)
- [Guide FFmpeg installation](https://formulae.brew.sh/formula/ffmpeg)

