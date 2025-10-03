# 🎤 TakeNote AI

Application Python pour convertir les fichiers audio en texte via Whisper, avec nettoyage et optimisation automatique.

## 📋 Fonctionnalités

- **Conversion audio** : Support des formats MP3, M4A, WAV, FLAC, AAC
- **Nettoyage automatique** : Réduction de bruit, normalisation, optimisation pour Whisper
- **Transcription intelligente** : Utilisation de Whisper avec détection automatique de langue
- **Formats de sortie multiples** : TXT, JSON, SRT, VTT
- **Scripts modulaires** : Utilisation individuelle ou orchestrée

## 🛠️ Prérequis

### Système
- **Python 3.8+** installé (sur macOS, utilisez `python3`)
- **FFmpeg** installé (requis pour le traitement audio)

### Optimisations Mac M4 Pro
- **PyTorch avec MPS** : Accélération GPU native via Metal Performance Shaders
- **ARM64 optimisé** : Versions natives pour Apple Silicon

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
├── takenote.py              # Script principal d'orchestration
├── audio_converter.py       # Conversion audio
├── audio_cleaner.py         # Nettoyage audio
├── audio_transcriber.py     # Transcription Whisper
├── run.sh                   # Script de lancement rapide
├── install.sh               # Script d'installation automatique
├── test_setup.py            # Script de test d'installation
├── requirements.txt         # Dépendances Python
├── .gitignore              # Fichiers à ignorer
└── README.md               # Documentation
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

## 🎯 Exemples d'utilisation

### Transcription d'une réunion
```bash
python3 takenote.py reunion.m4a -m medium -l fr -f srt
```

### Conversion rapide
```bash
python3 takenote.py podcast.mp3 -m tiny --no-clean
```

### Analyse de qualité
```bash
python3 takenote.py audio.wav --analyze-only
```

## 📝 Notes

- Les modèles Whisper sont téléchargés automatiquement au premier usage
- Les fichiers temporaires sont supprimés automatiquement
- Utilisez `--keep-intermediate` pour conserver les fichiers intermédiaires
- Le nettoyage audio améliore significativement la qualité de transcription

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou soumettre une pull request.

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

---

**TakeNote AI** - Transformez vos fichiers audio en texte avec intelligence artificielle 🚀
