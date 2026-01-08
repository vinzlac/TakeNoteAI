# 🔄 Workflow Complet : De l'Audio aux Résumés

## 📋 Étapes obligatoires

### **Étape 1 : Générer le fichier JSON (OBLIGATOIRE)**
```bash
# Traiter votre fichier audio avec le script RAG
python advanced_rag_transcription.py votre_audio.mp3
```

**Résultat** : Fichier JSON généré automatiquement (ex: `votre_audio_advanced_rag_20251003_214507.json`)

### **Étape 2 : Analyser et résumer (OPTIONNEL)**
Une fois le fichier JSON créé, vous pouvez utiliser tous les scripts d'analyse :

```bash
# Questions spécifiques
python simple_audio_analyzer.py fichier.json --question "Quels risques ?"

# Résumés complets
python audio_summarizer.py fichier.json --type executive

# Interface interactive
python resume_audio.py

# Affichage simple
python show_summary.py
```

## 🎯 Workflow Recommandé

### **🚀 Démarrage rapide**
```bash
# 1. Traiter votre audio (OBLIGATOIRE)
python advanced_rag_transcription.py mon_audio.mp3

# 2. Générer un résumé (OPTIONNEL)
python resume_audio.py
```

### **📊 Analyse complète**
```bash
# 1. Traiter l'audio
python advanced_rag_transcription.py mon_audio.mp3

# 2. Tous les résumés
python audio_summarizer.py mon_audio_advanced_rag_*.json --type all

# 3. Questions spécifiques
python simple_audio_analyzer.py mon_audio_advanced_rag_*.json --question "Quelles actions ?"
```

## 📁 Structure des fichiers

### **Fichiers d'entrée (Audio)**
```
votre_audio.mp3          # Fichier audio original
mon_meeting.wav          # Autre format audio
```

### **Fichiers intermédiaires (JSON)**
```
votre_audio_advanced_rag_20251003_214507.json    # Généré par le RAG
mon_meeting_advanced_rag_20251003_214507.json    # Autre transcription
```

### **Fichiers de sortie (Résumés)**
```
resume_executif.md                    # Résumé exécutif
resume_business.md                    # Résumé business
resume_detaille.md                    # Résumé détaillé
resumes_complets/                     # Dossier avec tous les résumés
  ├── resume_executive.md
  ├── resume_business.md
  └── resume_detailed.md
```

## 🔍 Vérification des fichiers

### **Vérifier les fichiers JSON disponibles**
```bash
ls -la *advanced_rag*.json
```

### **Vérifier le contenu d'un fichier JSON**
```bash
# Afficher les métadonnées
cat fichier.json | jq '.metadata'

# Afficher le texte transcrit
cat fichier.json | jq '.transcription.text'
```

## ⚠️ Erreurs courantes

### **Erreur : "Aucun fichier JSON trouvé"**
```bash
❌ Aucun fichier JSON de transcription trouvé.
💡 Utilisez d'abord : python advanced_rag_transcription.py votre_audio.mp3
```

**Solution** : Générer d'abord le fichier JSON avec le script RAG

### **Erreur : "Fichier JSON non trouvé"**
```bash
❌ Le fichier fichier.json n'existe pas
```

**Solution** : Vérifier le nom exact du fichier JSON généré

### **Erreur : "Fichier audio non trouvé"**
```bash
❌ Le fichier votre_audio.mp3 n'existe pas
```

**Solution** : Vérifier que le fichier audio existe dans le répertoire

## 🎯 Scripts par étape

### **Étape 1 : Traitement audio (OBLIGATOIRE)**
```bash
# Script principal de transcription RAG
python advanced_rag_transcription.py audio.mp3

# Avec paramètres spécifiques
python advanced_rag_transcription.py audio.mp3 --transcription-model whisper
```

### **Étape 2 : Analyse et résumés (OPTIONNEL)**
```bash
# Questions spécifiques
python simple_audio_analyzer.py fichier.json --question "Votre question"

# Résumés complets
python audio_summarizer.py fichier.json --type executive

# Interface interactive
python resume_audio.py

# Affichage simple
python show_summary.py

# Démonstration complète
python demo_questions.py
```

## 🚀 Exemples pratiques

### **Exemple 1 : Traitement d'une réunion**
```bash
# 1. Traiter la réunion
python advanced_rag_transcription.py reunion_equipe.mp3

# 2. Générer le résumé exécutif
python audio_summarizer.py reunion_equipe_advanced_rag_*.json --type executive

# 3. Analyser les risques
python simple_audio_analyzer.py reunion_equipe_advanced_rag_*.json --question "Quels risques ?"
```

### **Exemple 2 : Analyse complète**
```bash
# 1. Traiter l'audio
python advanced_rag_transcription.py presentation.mp3

# 2. Tous les résumés
python audio_summarizer.py presentation_advanced_rag_*.json --type all

# 3. Questions spécifiques
python simple_audio_analyzer.py presentation_advanced_rag_*.json --question "Quelles actions ?"
python simple_audio_analyzer.py presentation_advanced_rag_*.json --question "Qui fait partie de l'équipe ?"
```

### **Exemple 3 : Workflow interactif**
```bash
# 1. Traiter l'audio
python advanced_rag_transcription.py mon_audio.mp3

# 2. Interface guidée pour les résumés
python resume_audio.py

# 3. Interface guidée pour les questions
python ask_audio.py
```

## 📊 Ordre des opérations

### **✅ Ordre correct**
1. **Audio** → **JSON** (avec `advanced_rag_transcription.py`)
2. **JSON** → **Résumés** (avec `audio_summarizer.py`)
3. **JSON** → **Questions** (avec `simple_audio_analyzer.py`)

### **❌ Ordre incorrect**
1. ~~**Audio** → **Résumés**~~ (impossible sans JSON)
2. ~~**JSON** → **Audio**~~ (inutile)

## 🎯 Résumé du workflow

### **🔴 Étape obligatoire**
```bash
python advanced_rag_transcription.py votre_audio.mp3
```
→ Génère le fichier JSON de transcription

### **🟡 Étapes optionnelles**
```bash
# Résumés
python audio_summarizer.py fichier.json --type executive

# Questions
python simple_audio_analyzer.py fichier.json --question "Quels risques ?"

# Interface interactive
python resume_audio.py
```

## 💡 Conseil

**Commencez toujours par** :
```bash
python advanced_rag_transcription.py votre_audio.mp3
```

**Puis utilisez** :
```bash
python resume_audio.py
```

Pour une expérience guidée et complète !
