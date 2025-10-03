# 🎤 TakeNote AI

Application Python pour convertir les fichiers audio en texte via Whisper, avec nettoyage et optimisation automatique.

## 📋 Fonctionnalités

- **Conversion audio** : Support des formats MP3, M4A, WAV, FLAC, AAC
- **Nettoyage automatique** : Réduction de bruit, normalisation, optimisation pour Whisper
- **Transcription intelligente** : Utilisation de Whisper avec détection automatique de langue
- **🎤 Identification des locuteurs** : Détection automatique des changements de locuteurs
- **Formats de sortie multiples** : TXT, JSON, SRT, VTT
- **Scripts modulaires** : Utilisation individuelle ou orchestrée

## 🛠️ Prérequis

### Système
- **Python 3.8+** installé (sur macOS, utilisez `python3`)
- **FFmpeg** installé (requis pour le traitement audio)

### Optimisations Mac M4 Pro
- **PyTorch avec MPS** : Accélération GPU native via Metal Performance Shaders
- **ARM64 optimisé** : Versions natives pour Apple Silicon

### Identification des locuteurs (optionnel)
- **Token Hugging Face** : Requis pour l'identification avancée des locuteurs
- **Acceptation des conditions** : Nécessaire pour accéder aux modèles pyannote.audio

### Installation de FFmpeg

#### macOS (via Homebrew)
```bash
brew install ffmpeg
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install ffmpeg
```

#### Windows
Télécharger depuis [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html) et ajouter au PATH.

## 🚀 Installation

### Installation automatique (recommandée)
```bash
git clone <votre-repo>
cd TakeNoteAI
./install.sh
```

### Installation manuelle

1. **Cloner le projet**
```bash
git clone <votre-repo>
cd TakeNoteAI
```

2. **Créer un environnement virtuel (recommandé)**
```bash
# Sur macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Sur Windows
python -m venv venv
venv\Scripts\activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

### Vérification des optimisations Mac M4 Pro
```bash
# Vérifier que MPS est disponible
python3 -c "import torch; print(f'MPS available: {torch.backends.mps.is_available()}')"
```

### Configuration pour l'identification des locuteurs

#### 1. Créer un token Hugging Face
1. Allez sur [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Créez un nouveau token (type: **Read**)
3. Copiez le token généré

#### 2. Configurer le token
```bash
# Méthode 1: Via huggingface-cli (recommandée)
huggingface-cli login

# Méthode 2: Via script Python
python3 setup_huggingface_token.py

# Méthode 3: Variable d'environnement
export HUGGINGFACE_HUB_TOKEN="votre_token_ici"
```

#### 3. Accepter les conditions d'utilisation
Pour utiliser l'identification avancée des locuteurs, acceptez les conditions sur ces liens :

- [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
- [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0)
- [pyannote/speaker-diarization-community-1](https://huggingface.co/pyannote/speaker-diarization-community-1)

#### 4. Tester la configuration
```bash
python3 test_hf_token.py
```

### Vérification de l'installation
```bash
# Sur macOS/Linux
python3 test_setup.py

# Sur Windows
python test_setup.py
```

## 📖 Utilisation

### Lancement rapide
```bash
# Lancement simple
./run.sh audio.mp3

# Avec options
./run.sh audio.m4a -m large -l fr
```

### Script principal (recommandé)

```bash
# Traitement complet d'un fichier
python3 takenote.py audio.mp3

# Spécifier la sortie
python3 takenote.py audio.m4a -o transcription.txt

# Utiliser un modèle plus précis (plus lent)
python3 takenote.py audio.mp3 -m large

# Spécifier la langue
python3 takenote.py audio.mp3 -l fr

# Format de sortie différent
python3 takenote.py audio.mp3 -f json

# Analyser un fichier sans le traiter
python3 takenote.py audio.mp3 --analyze-only
```

### Scripts individuels

#### 1. Conversion audio
```bash
# Convertir un fichier en MP3 propre
python3 audio_converter.py input.m4a

# Spécifier la qualité
python3 audio_converter.py input.wav -q high
```

#### 2. Nettoyage audio
```bash
# Nettoyer un fichier audio
python3 audio_cleaner.py input.mp3

# Analyser la qualité
python3 audio_cleaner.py input.mp3 --analyze

# Désactiver certaines options
python3 audio_cleaner.py input.mp3 --no-noise-reduction
```

#### 3. Transcription
```bash
# Transcription basique
python3 audio_transcriber.py input.mp3

# Modèle et langue spécifiques
python3 audio_transcriber.py input.mp3 -m large -l fr

# Format avec timestamps
python3 audio_transcriber.py input.mp3 -f srt

# Lister les modèles disponibles
python3 audio_transcriber.py --list-models
```

#### 4. Identification des locuteurs
```bash
# Script principal (recommandé) - Diarisation propre
python3 whisper_clean_diarization.py audio.mp3

# Avec options avancées
python3 whisper_clean_diarization.py audio.mp3 -m large -l fr -f json

# Script hybride (si pyannote.audio configuré)
python3 whisper_speaker_diarization.py audio.mp3 -m base -f txt

# Script simplifié (basique)
python3 whisper_simple_diarization.py audio.mp3 --sensitivity high
```

#### 5. Téléchargement de modèles Whisper
```bash
# Télécharger un modèle spécifique
python3 download_whisper_model.py large

# Télécharger le modèle medium
python3 download_whisper_medium.py
```

## ⚙️ Options avancées

### Modèles Whisper
- `tiny` : Rapide, qualité correcte (~39 MB)
- `base` : Équilibré, recommandé (~74 MB)
- `small` : Bonne qualité (~244 MB)
- `medium` : Très bonne qualité (~769 MB)
- `large` : Meilleure qualité (~1550 MB)

### Qualités de conversion
- `high` : 192kbps, 44.1kHz (recommandé)
- `medium` : 128kbps, 44.1kHz
- `low` : 96kbps, 22kHz

### Formats de sortie
- `txt` : Texte simple
- `json` : Données complètes avec métadonnées
- `srt` : Sous-titres SRT
- `vtt` : Sous-titres WebVTT

## 📁 Structure du projet

```
TakeNoteAI/
├── takenote.py                      # Script principal d'orchestration
├── audio_converter.py               # Conversion audio
├── audio_cleaner.py                 # Nettoyage audio
├── audio_transcriber.py             # Transcription Whisper
├── whisper_clean_diarization.py     # 🎤 Identification des locuteurs (recommandé)
├── whisper_speaker_diarization.py   # Identification hybride (Whisper + pyannote.audio)
├── whisper_simple_diarization.py    # Identification basique
├── download_whisper_model.py        # Téléchargement de modèles Whisper
├── download_whisper_medium.py       # Téléchargement du modèle medium
├── setup_huggingface_token.py       # Configuration du token HF
├── test_hf_token.py                 # Test de la configuration HF
├── run.sh                           # Script de lancement rapide
├── install.sh                       # Script d'installation automatique
├── test_setup.py                    # Script de test d'installation
├── requirements.txt                 # Dépendances Python
├── .gitignore                      # Fichiers à ignorer
└── README.md                       # Documentation
```

## 🔧 Dépannage

### Erreur FFmpeg
```
ffmpeg: command not found
```
**Solution** : Vérifier l'installation de FFmpeg et qu'il est dans le PATH.

### Erreur de mémoire
```
CUDA out of memory
```
**Solution** : Utiliser un modèle plus petit (`tiny` ou `base`) ou réduire la qualité.

### Optimisations Mac M4 Pro
- **MPS automatique** : PyTorch utilise automatiquement Metal Performance Shaders
- **ARM64 natif** : Toutes les dépendances sont optimisées pour Apple Silicon
- **Performance GPU** : Accélération native sur les puces M1/M2/M3/M4

### Fichier audio corrompu
```
Error: Invalid data found
```
**Solution** : Vérifier l'intégrité du fichier audio ou essayer de le reconvertir.

### Performance lente
**Solutions** :
- Utiliser un modèle plus petit
- Réduire la qualité de conversion
- Vérifier l'espace disque disponible

### Problèmes d'identification des locuteurs

#### Erreur de token Hugging Face
```
401 Client Error: Unauthorized
```
**Solution** : Vérifier que le token est correctement configuré avec `python3 test_hf_token.py`

#### Erreur de conditions d'utilisation
```
403 Client Error: Forbidden
```
**Solution** : Accepter les conditions d'utilisation sur les 3 liens pyannote.audio mentionnés plus haut

#### Erreur torchcodec/FFmpeg
```
torchcodec is not installed correctly
```
**Solution** : Utiliser le script `whisper_clean_diarization.py` qui évite ces dépendances

#### Un seul locuteur détecté
**Solutions** :
- Utiliser `--sensitivity high` avec `whisper_simple_diarization.py`
- Vérifier que l'audio contient bien plusieurs locuteurs
- Ajuster les paramètres de détection dans le script

## 🎯 Exemples d'utilisation

### Transcription d'une réunion
```bash
python3 takenote.py reunion.m4a -m medium -l fr -f srt
```

### Transcription avec identification des locuteurs
```bash
# Méthode recommandée (sans dépendances)
python3 whisper_clean_diarization.py reunion.mp3 -m large -f json

# Méthode avancée (avec pyannote.audio)
python3 whisper_speaker_diarization.py reunion.mp3 -m base -f txt
```

### Conversion rapide
```bash
python3 takenote.py podcast.mp3 -m tiny --no-clean
```

### Analyse de qualité
```bash
python3 takenote.py audio.wav --analyze-only
```

### Configuration complète pour l'identification des locuteurs
```bash
# 1. Configurer le token
huggingface-cli login

# 2. Tester la configuration
python3 test_hf_token.py

# 3. Utiliser l'identification
python3 whisper_clean_diarization.py audio.mp3 -m large
```

## 📝 Notes

- Les modèles Whisper sont téléchargés automatiquement au premier usage
- Les fichiers temporaires sont supprimés automatiquement
- Utilisez `--keep-intermediate` pour conserver les fichiers intermédiaires
- Le nettoyage audio améliore significativement la qualité de transcription
- **Identification des locuteurs** : Le script `whisper_clean_diarization.py` est recommandé pour éviter les problèmes de dépendances
- **Token Hugging Face** : Nécessaire uniquement pour l'identification avancée avec pyannote.audio
- **Conditions d'utilisation** : Doivent être acceptées sur les 3 liens pyannote.audio pour utiliser l'identification hybride

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou soumettre une pull request.

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

---

**TakeNote AI** - Transformez vos fichiers audio en texte avec intelligence artificielle 🚀
