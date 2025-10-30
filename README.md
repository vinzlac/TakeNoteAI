# 🎤 TakeNote AI

Application Python avancée pour la transcription audio avec RAG (Retrieval-Augmented Generation), analyse intelligente et optimisations Mac M4.

## 📋 Fonctionnalités

### 🎯 **Fonctionnalités de base**
- **Conversion audio** : Support des formats MP3, M4A, WAV, FLAC, AAC
- **Nettoyage automatique** : Réduction de bruit, normalisation, optimisation pour Whisper
- **Transcription intelligente** : Whisper + SpeechBrain avec détection automatique de langue
- **🎤 Identification des locuteurs** : Détection automatique des changements de locuteurs
- **Formats de sortie multiples** : TXT, JSON, SRT, VTT

### 🚀 **Fonctionnalités avancées RAG**
- **Transcription RAG** : Système complet de transcription avec embeddings sémantiques
- **Mots-clés métiers** : Extraction automatique et personnalisée de mots-clés techniques
- **Analyse intelligente** : Réponses aux questions en langage naturel
- **Résumés automatiques** : Génération de résumés exécutifs, business et détaillés
- **Base vectorielle** : Stockage et recherche sémantique avec ChromaDB
- **Workflow complet** : Scripts tout-en-un pour automatisation complète

### ⚡ **Optimisations Mac M4**
- **GPU M4 natif** : Accélération via Metal Performance Shaders (MPS)
- **Multi-threading** : Optimisation CPU avec 14 threads
- **Mémoire unifiée** : Exploitation de la mémoire 48GB du M4
- **Performance** : 1min audio → ~15-20 secondes de traitement

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
./install_advanced.sh  # Pour les fonctionnalités RAG avancées
```

### Installation avec uv (alternative moderne)
```bash
# 1) Installer uv (macOS)
# Via Homebrew
brew install uv
# ou via script officiel
# curl -LsSf https://astral.sh/uv/install.sh | sh

# 2) Initialiser le projet (crée pyproject.toml)
uv init

# 3) Installer les dépendances principales
uv add openai-whisper ffmpeg-python torch torchaudio chromadb sentence-transformers keybert spacy psutil

# 4) Verrouiller les versions (génère uv.lock)
uv lock

# 5) Exécuter un script
uv run python rag_ultra_simple.py audio.mp3
```
Notes:
- Avec uv, `requirements.txt` devient optionnel (uv utilise `pyproject.toml` + `uv.lock`).
- Conservez `requirements.txt` si vous souhaitez garder la compatibilité `pip`.

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

3. **Installer les dépendances de base**
```bash
pip install -r requirements.txt
```

4. **Installer les dépendances RAG (optionnel)**
```bash
./install_advanced.sh
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

Astuce uv: vous pouvez remplacer `python3` par `uv run python` (ex: `uv run python rag_ultra_simple.py audio.mp3`).

### 🚀 **Scripts RAG tout-en-un (recommandés)**

#### Script ultra-simple (quotidien)
```bash
# Workflow complet automatisé
python3 rag_ultra_simple.py audio.mp3
```

#### Script complet avec mots-clés
```bash
# Avec mots-clés personnalisés
python3 rag_complete_workflow.py audio.mp3 --keywords "Azure,Microsoft"

# Avec questions personnalisées
python3 rag_complete_workflow.py audio.mp3 --questions "Quels sont les risques ?" "Actions prioritaires ?"
```

#### Script simplifié
```bash
# Workflow intermédiaire
python3 rag_simple.py audio.mp3
```

### 🎯 **Scripts individuels RAG**

#### Transcription RAG avec mots-clés
```bash
# Transcription avec mots-clés personnalisés
python3 advanced_rag_transcription_with_keywords.py audio.mp3 --keywords "Azure,Microsoft"

# Avec fichier de mots-clés
python3 advanced_rag_transcription_with_keywords.py audio.mp3 --keywords-file keywords.txt
```

#### Génération de mots-clés
```bash
# Extraire les mots-clés d'une transcription
python3 generate_keywords_from_transcription.py transcription.json --top 25
```

#### Analyse intelligente
```bash
# Poser une question sur une transcription
python3 simple_audio_analyzer.py transcription.json "Quels risques sont identifiés ?"

# Interface interactive
python3 ask_audio.py
```

#### Résumés automatiques
```bash
# Résumé exécutif
python3 audio_summarizer.py transcription.json --type executif

# Tous les types de résumés
python3 audio_summarizer.py transcription.json --type all

# Interface interactive
python3 resume_audio.py
```

### 📋 **Scripts de base (classiques)**

#### Lancement rapide
```bash
# Lancement simple
./run.sh audio.mp3

# Avec options
./run.sh audio.m4a -m large -l fr
```

#### Script principal (recommandé)
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
├── 🚀 SCRIPTS RAG AVANCÉS
│   ├── rag_ultra_simple.py                    # Script tout-en-un ultra-simple (quotidien)
│   ├── rag_complete_workflow.py               # Workflow complet avec mots-clés
│   ├── rag_simple.py                          # Workflow simplifié
│   ├── advanced_rag_transcription.py          # Transcription RAG de base
│   ├── advanced_rag_transcription_with_keywords.py # Transcription RAG + mots-clés
│   ├── simple_audio_analyzer.py               # Analyse Q&A intelligente
│   ├── audio_summarizer.py                    # Génération de résumés
│   ├── generate_keywords_from_transcription.py # Extraction automatique de mots-clés
│   ├── ask_audio.py                           # Interface Q&A interactive
│   ├── resume_audio.py                        # Interface résumés interactive
│   └── show_summary.py                        # Affichage résumés terminal
│
├── 🎯 SCRIPTS DE BASE
│   ├── takenote.py                            # Script principal d'orchestration
│   ├── audio_converter.py                     # Conversion audio
│   ├── audio_cleaner.py                       # Nettoyage audio
│   ├── audio_transcriber.py                   # Transcription Whisper
│   ├── whisper_clean_diarization.py           # 🎤 Identification des locuteurs (recommandé)
│   ├── whisper_speaker_diarization.py         # Identification hybride
│   ├── whisper_simple_diarization.py          # Identification basique
│   ├── download_whisper_model.py              # Téléchargement de modèles Whisper
│   ├── download_whisper_medium.py             # Téléchargement du modèle medium
│   ├── setup_huggingface_token.py             # Configuration du token HF
│   └── test_hf_token.py                       # Test de la configuration HF
│
├── 🔧 SCRIPTS DE GESTION
│   ├── clean_rag_data.py                      # Nettoyage des données RAG
│   ├── rag_accumulation_manager.py            # Gestion accumulation vs nettoyage
│   ├── detect_m4_capabilities.py              # Détection optimisations M4
│   ├── optimize_rag_for_m4.py                 # Application optimisations M4
│   ├── explain_quality_score.py               # Explication scores de qualité
│   └── check_files.py                         # Vérification fichiers JSON
│
├── 📚 DOCUMENTATION
│   ├── README.md                              # Documentation principale
│   ├── README_ADVANCED.md                     # Documentation fonctionnalités avancées
│   ├── GUIDE_FINAL_SCRIPTS.md                 # Guide final des scripts
│   ├── GUIDE_WORKFLOW_COMPLET.md              # Guide workflow complet
│   ├── GUIDE_MOTS_CLES.md                     # Guide mots-clés
│   ├── GUIDE_ACCUMULATION_RAG.md              # Guide accumulation RAG
│   ├── GUIDE_MAC_M4_OPTIMIZATION.md           # Guide optimisations M4
│   └── .cursor/rules/                         # Règles Cursor pour l'IA
│
├── 🛠️ INSTALLATION & CONFIGURATION
│   ├── install.sh                             # Installation automatique
│   ├── install_advanced.sh                    # Installation fonctionnalités avancées
│   ├── run.sh                                 # Script de lancement rapide
│   ├── test_setup.py                          # Script de test d'installation
│   ├── requirements.txt                       # Dépendances Python
│   ├── pyproject.toml                         # Dépendances (uv/PEP 621)
│   ├── uv.lock                                # Verrouillage des versions (uv)
│   └── .gitignore                             # Fichiers à ignorer
│
└── 📊 DONNÉES & SORTIES
    ├── chroma_db/                             # Base de données vectorielle
    ├── model_checkpoints/                     # Modèles pré-entraînés
    ├── pretrained_models/                     # Modèles téléchargés
    ├── *.json                                 # Fichiers de transcription RAG
    ├── resume_*.md                            # Résumés générés
    ├── keywords_*.txt                         # Fichiers de mots-clés
    └── workflow_results_*.json                # Résultats de workflows
```

## 🔧 Dépannage

### 🚨 **Erreurs RAG courantes**

#### Erreur SpeechBrain Decoder
```
❌ 'ModuleDict' object has no attribute 'decoder'
```
**Solution** : Utiliser le modèle `speechbrain/asr-crdnn-commonvoice-fr` avec `transcribe_file()`.

#### Erreur ChromaDB Metadata
```
❌ Expected metadata value to be a str, got ['Microsoft', 'Azure'] which is a list
```
**Solution** : Convertir les listes en strings : `", ".join(keywords)`.

#### Erreurs de nettoyage (normales)
```
❌ Erreur lors de la suppression de keywords_generated_*.txt: [Errno 2] No such file or directory
```
**Statut** : Ces erreurs sont normales - fichiers inexistants ou déjà supprimés.

### 🎯 **Erreurs de base**

#### Erreur FFmpeg
```
ffmpeg: command not found
```
**Solution** : Vérifier l'installation de FFmpeg et qu'il est dans le PATH.

#### Erreur de mémoire
```
CUDA out of memory
```
**Solution** : Utiliser un modèle plus petit (`tiny` ou `base`) ou réduire la qualité.

#### Fichier audio corrompu
```
Error: Invalid data found
```
**Solution** : Vérifier l'intégrité du fichier audio ou essayer de le reconvertir.

### ⚡ **Optimisations Mac M4**

#### Vérification M4
```bash
# Vérifier les capacités M4
python3 detect_m4_capabilities.py

# Optimiser les scripts
python3 optimize_rag_for_m4.py
```

#### Performance attendue M4
- **1min audio** : ~15-20 secondes
- **5min audio** : ~45-60 secondes
- **10min audio** : ~90-120 secondes

#### Optimisations automatiques
- **MPS GPU** : Accélération Metal Performance Shaders
- **Multi-threading** : 14 threads CPU optimisés
- **Mémoire unifiée** : Exploitation 48GB du M4

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

## 🚀 Fonctionnalités Avancées RAG

### 🎯 **Workflow complet automatisé**

#### Script tout-en-un (recommandé pour l'usage quotidien)
```bash
# Workflow ultra-simple : Transcription → Analyse → Résumé
python3 rag_ultra_simple.py audio.mp3
```

#### Script complet avec personnalisation
```bash
# Avec mots-clés personnalisés
python3 rag_complete_workflow.py audio.mp3 --keywords "Azure,Microsoft"

# Avec questions spécifiques
python3 rag_complete_workflow.py audio.mp3 --questions "Quels sont les risques ?" "Actions prioritaires ?"
```

### 🔧 **Gestion des données RAG**

#### Nettoyage et accumulation
```bash
# Nettoyer toutes les données RAG
python3 clean_rag_data.py --all

# Vérifier l'état des données
python3 clean_rag_data.py --status

# Décision intelligente accumulation vs nettoyage
python3 rag_accumulation_manager.py --recommendations
```

#### Optimisations Mac M4
```bash
# Détecter les capacités M4
python3 detect_m4_capabilities.py

# Optimiser tous les scripts pour M4
python3 optimize_rag_for_m4.py
```

### 📊 **Analyse et résumés**

#### Questions en langage naturel
```bash
# Interface interactive
python3 ask_audio.py

# Questions directes
python3 simple_audio_analyzer.py transcription.json "Quels risques sont identifiés ?"
```

#### Génération de résumés
```bash
# Résumés automatiques
python3 audio_summarizer.py transcription.json --type executif
python3 audio_summarizer.py transcription.json --type business
python3 audio_summarizer.py transcription.json --type detaille

# Interface interactive
python3 resume_audio.py
```

### 🔍 **Extraction de mots-clés**

#### Génération automatique
```bash
# Extraire les mots-clés d'une transcription
python3 generate_keywords_from_transcription.py transcription.json --top 25
```

#### Utilisation avec transcription
```bash
# Transcription avec mots-clés personnalisés
python3 advanced_rag_transcription_with_keywords.py audio.mp3 --keywords "Azure,Microsoft"
```

### 🎯 **Fonctionnalités techniques incluses**

- 🎤 **Transcription avancée** : Whisper + SpeechBrain optimisés
- 🔍 **Extraction de mots-clés métiers** : KeyBERT + filtrage intelligent
- 🧠 **Embeddings sémantiques** : Sentence Transformers
- 💾 **Base de données vectorielle** : ChromaDB avec recherche
- 🔗 **Analyse intelligente** : Q&A en langage naturel
- 📋 **Résumés automatiques** : Exécutif, business, détaillé
- ⚡ **Optimisations M4** : GPU MPS + multi-threading
- 🔧 **Gestion des données** : Nettoyage et accumulation intelligente

📖 **Documentation complète** : Voir [README_ADVANCED.md](README_ADVANCED.md)

## 📝 Notes importantes

### 🎯 **Fonctionnalités RAG**
- **Installation** : `./install_advanced.sh` pour toutes les fonctionnalités avancées
- **Scripts recommandés** : `rag_ultra_simple.py` pour usage quotidien
- **Performance M4** : Optimisations automatiques détectées et appliquées
- **Gestion des données** : Nettoyage régulier recommandé pour éviter l'accumulation

### 🎤 **Transcription**
- **Modèles** : Whisper téléchargés automatiquement au premier usage
- **Qualité** : Nettoyage audio améliore significativement la transcription
- **Identification locuteurs** : `whisper_clean_diarization.py` recommandé (sans dépendances)
- **Mots-clés** : Support pour améliorer la précision de transcription

### 🔧 **Configuration**
- **Token Hugging Face** : Nécessaire pour l'identification avancée avec pyannote.audio
- **Conditions d'utilisation** : Acceptées sur les liens pyannote.audio pour identification hybride
- **Fichiers temporaires** : Supprimés automatiquement (utiliser `--keep-intermediate` pour conserver)
- **Optimisations M4** : Détection et configuration automatiques

### 📊 **Données et sorties**
- **Formats** : JSON (complet), TXT (texte), SRT/VTT (sous-titres)
- **Base vectorielle** : ChromaDB pour recherche sémantique
- **Résumés** : Exécutif, business, détaillé automatiquement générés
- **Mots-clés** : Extraction automatique + support personnalisé

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou soumettre une pull request.

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

---

## 🎉 **Démarrage rapide**

### Pour commencer immédiatement :
```bash
# 1. Installation complète
./install.sh
./install_advanced.sh

# 2. Usage quotidien ultra-simple
python3 rag_ultra_simple.py votre_audio.mp3

# 3. Avec mots-clés personnalisés
python3 rag_complete_workflow.py votre_audio.mp3 --keywords "VotreEntreprise,Technologie,Mots-clés"
```

### Pour les utilisateurs avancés :
- **Scripts individuels** : Utilisez les scripts spécialisés selon vos besoins
- **Optimisations M4** : Détection et application automatiques
- **Gestion des données** : Nettoyage et accumulation intelligente
- **Analyse personnalisée** : Questions en langage naturel
- **Résumés adaptatifs** : Exécutif, business, détaillé

---

**🎤 TakeNote AI** - Transcription audio intelligente avec RAG, analyse et optimisations Mac M4 🚀

*Transformez vos réunions, interviews et conférences en insights actionables avec l'intelligence artificielle*
