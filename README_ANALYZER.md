# 📊 Analyseur de Questions Audio

Ce projet contient des scripts Python pour analyser des transcriptions audio et répondre à des questions en langage naturel.

## 🎯 Fonctionnalités

- **Analyse sémantique** des transcriptions audio
- **Réponses intelligentes** aux questions posées
- **Extraction automatique** de risques, actions, délais, etc.
- **Timestamps précis** pour chaque information trouvée
- **Classification automatique** par type et priorité

## 📁 Fichiers du projet

### Scripts principaux

1. **`simple_audio_analyzer.py`** - Script principal d'analyse
2. **`demo_questions.py`** - Démonstration complète
3. **`advanced_rag_transcription.py`** - Script RAG original

### Scripts utilitaires

4. **`analyze_audio_question.py`** - Version avancée (en développement)
5. **`GUIDE_SPEECHBRAIN.md`** - Guide d'utilisation SpeechBrain

## 🚀 Utilisation rapide

### 1. Prérequis

```bash
# Activer l'environnement virtuel
source venv/bin/activate

# S'assurer d'avoir un fichier JSON de transcription
ls *.json
```

### 2. Analyse simple

```bash
# Question sur les risques
python simple_audio_analyzer.py fichier.json --question "Quels risques sont identifiés ?"

# Question sur les actions
python simple_audio_analyzer.py fichier.json --question "Quelles actions doivent être prises ?"

# Question sur l'équipe
python simple_audio_analyzer.py fichier.json --question "Qui fait partie de l'équipe ?"
```

### 3. Démonstration complète

```bash
# Lancer toutes les analyses d'exemple
python demo_questions.py
```

### 4. Sauvegarder les résultats

```bash
# Sauvegarder dans un fichier
python simple_audio_analyzer.py fichier.json --question "Quels risques ?" --output resultats.md
```

## 📋 Types de questions supportées

### 🔍 **Analyse des risques**
- "Quels risques sont identifiés ?"
- "Quels dangers sont mentionnés ?"
- "Quels problèmes sont évoqués ?"

**Résultat** : Liste des risques avec type, description, timestamp et sévérité

### 🎯 **Analyse des actions**
- "Quelles actions doivent être prises ?"
- "Que faut-il faire ?"
- "Quelles tâches sont à réaliser ?"

**Résultat** : Liste des actions avec type, description, timestamp et priorité

### 👥 **Informations sur l'équipe**
- "Qui fait partie de l'équipe ?"
- "Combien de personnes travaillent sur le projet ?"
- "Quel est le rôle de chacun ?"

**Résultat** : Informations sur la composition et la taille de l'équipe

### ⏰ **Analyse temporelle**
- "Quels sont les délais ?"
- "Quelles sont les échéances ?"
- "Quand doit être livré le projet ?"

**Résultat** : Informations temporelles et échéances critiques

### 🏗️ **Analyse technique**
- "Quel est l'état de l'architecture ?"
- "Quels standards sont utilisés ?"
- "Quelles technologies sont mentionnées ?"

**Résultat** : Segments pertinents avec scores de pertinence

## 🔧 Fonctionnement technique

### 1. **Chargement des données**
```python
# Le script charge le fichier JSON de transcription
data = json.load(file)
full_text = data["transcription"]["text"]
segments = data["transcription"]["segments"]
```

### 2. **Analyse sémantique**
```python
# Recherche de mots-clés dans chaque segment
for segment in segments:
    text = segment["text"].lower()
    if keyword in text:
        # Ajouter à la liste des résultats
```

### 3. **Classification automatique**
- **Risques** : changement, modification, standard, go-live, etc.
- **Actions** : développer, valider, tester, implémenter, etc.
- **Équipe** : développeur, architecte, responsable, etc.
- **Temps** : avant, après, go-live, délai, etc.

### 4. **Formatage des résultats**
- Structure claire avec émojis
- Timestamps précis
- Classification par type et priorité
- Mots-clés détectés

## 📊 Exemple de sortie

```
🔍 **Réponse à : "Quels risques sont identifiés ?"**

Voici les **risques identifiés** dans cette discussion :

### **1. Risque de changement**
- **Description** : Donc, ça va être plus si il y a des changements
- **Timestamp** : 38.8s - 41.8s
- **Sévérité** : Moyen
- **Mots-clés détectés** : changement

### **2. Risque de non-conformité**
- **Description** : On va dire, on a des questions avec les standards de Fortville.
- **Timestamp** : 54.6s - 57.6s
- **Sévérité** : Élevé
- **Mots-clés détectés** : standard
```

## 🛠️ Personnalisation

### Ajouter de nouveaux types de questions

Modifiez la classe `SimpleAudioAnalyzer` :

```python
def find_custom_info(self):
    """Trouve des informations personnalisées."""
    custom_keywords = ["votre", "mots", "clés"]
    # ... logique d'analyse
    return results

def answer_question(self, question: str):
    """Ajoutez votre condition :"""
    if "votre_question" in question.lower():
        return self.find_custom_info()
    # ... autres conditions
```

### Modifier les mots-clés

```python
self.question_keywords = {
    "risques": ["votre", "nouveau", "mot-clé"],
    "actions": ["autre", "action", "personnalisée"],
    # ... autres catégories
}
```

## 🎯 Cas d'usage

### 1. **Analyse de réunions projet**
- Identifier les risques et actions
- Suivre les décisions prises
- Analyser la répartition des responsabilités

### 2. **Audit de conformité**
- Vérifier les standards mentionnés
- Identifier les écarts de processus
- Suivre les recommandations

### 3. **Suivi de projet**
- Analyser les délais et échéances
- Identifier les dépendances
- Suivre l'avancement

### 4. **Formation et documentation**
- Extraire les bonnes pratiques
- Identifier les points d'attention
- Créer des guides de référence

## 🔍 Dépannage

### Erreur : "Fichier JSON non trouvé"
```bash
# Vérifier que le fichier existe
ls -la *.json

# Générer un fichier JSON avec le script RAG
python advanced_rag_transcription.py audio.mp3
```

### Erreur : "Aucune information trouvée"
```bash
# Vérifier le contenu du fichier JSON
cat fichier.json | jq '.transcription.text'

# Essayer une question plus générale
python simple_audio_analyzer.py fichier.json --question "Que dit l'audio ?"
```

### Erreur : "Module non trouvé"
```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Vérifier l'installation
pip list | grep -E "(json|pathlib|argparse)"
```

## 📈 Améliorations futures

- [ ] Support de plusieurs langues
- [ ] Interface web simple
- [ ] Export en différents formats (PDF, Excel)
- [ ] Intégration avec des bases de données
- [ ] API REST pour l'intégration
- [ ] Analyse de sentiment
- [ ] Extraction d'entités nommées
- [ ] Génération automatique de rapports

## 🤝 Contribution

Pour contribuer au projet :

1. Fork le repository
2. Créer une branche feature
3. Ajouter vos améliorations
4. Tester avec différents fichiers audio
5. Soumettre une pull request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

---

**💡 Conseil** : Commencez par tester avec `demo_questions.py` pour comprendre les capacités du système, puis utilisez `simple_audio_analyzer.py` pour vos propres questions.
