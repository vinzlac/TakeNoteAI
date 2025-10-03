# 🎯 Guide des Mots-Clés Personnalisés

## 🎯 **Problème résolu : "Forvia" transcrit en "Fortville"**

**OUI, c'est possible de donner au RAG une liste de mots-clés pour améliorer la transcription !**

## 🔧 **Solution : Script avec mots-clés personnalisés**

### **Script principal :**
```bash
python advanced_rag_transcription_with_keywords.py audio.mp3 --keywords "Forvia,Microsoft,Azure"
```

### **Script interactif :**
```bash
python transcribe_with_keywords.py
```

## 🚀 **Utilisation simple**

### **1. Avec mots-clés en ligne de commande**
```bash
# Mots-clés spécifiques
python advanced_rag_transcription_with_keywords.py audio.mp3 --keywords "Forvia,Microsoft,Azure"

# Plus de mots-clés
python advanced_rag_transcription_with_keywords.py audio.mp3 --keywords "Forvia,Microsoft,Azure,PowerBI,SAP,Oracle"
```

### **2. Avec fichier de mots-clés**
```bash
# Utiliser le fichier keywords_forvia.txt
python advanced_rag_transcription_with_keywords.py audio.mp3 --keywords-file keywords_forvia.txt
```

### **3. Interface interactive**
```bash
python transcribe_with_keywords.py
# Sélection guidée des fichiers et mots-clés
```

## 📊 **Comparaison des résultats**

### **❌ Sans mots-clés :**
```
"standards de Fortville"  # Incorrect
```

### **✅ Avec mots-clés :**
```bash
python advanced_rag_transcription_with_keywords.py audio.mp3 --keywords "Forvia"
```
```
"standards de Forvia"  # Correct !
```

## 🎯 **Fonctionnalités du script avec mots-clés**

### **✅ Amélioration de la transcription**
- **Prompt initial** : Whisper reçoit les mots-clés dans le contexte
- **Post-traitement** : Correction automatique des erreurs de transcription
- **Variations** : Gère les variations communes (espaces, tirets, etc.)

### **✅ Support complet**
- **Whisper** : Support natif des mots-clés via `initial_prompt`
- **SpeechBrain** : Post-traitement pour corriger les erreurs
- **Fallback** : Basculement automatique si erreur

### **✅ Intégration RAG**
- **Mots-clés enrichis** : Ajoutés aux métadonnées et embeddings
- **Extraction améliorée** : KeyBERT utilise les mots-clés pour de meilleurs résultats
- **Base vectorielle** : Stockage avec contexte des mots-clés

## 📁 **Fichiers créés**

### **Scripts principaux :**
1. **`advanced_rag_transcription_with_keywords.py`** - Script principal avec mots-clés
2. **`transcribe_with_keywords.py`** - Interface interactive simple

### **Fichiers d'exemple :**
3. **`keywords_forvia.txt`** - Liste d'exemple de mots-clés
4. **`keywords_example.txt`** - Liste étendue de mots-clés techniques

### **Guides :**
5. **`GUIDE_MOTS_CLES.md`** - Ce guide d'utilisation

## 🎯 **Types de mots-clés supportés**

### **🏢 Noms d'entreprises**
```
Forvia
Microsoft
Google
Amazon
Apple
Meta
```

### **💻 Technologies**
```
Azure
AWS
Docker
Kubernetes
Python
JavaScript
React
Angular
```

### **🛠️ Outils**
```
PowerBI
SAP
Oracle
Salesforce
Jira
Confluence
```

### **👥 Personnes/Noms**
```
Edouard
Marie
Jean-Pierre
```

### **📍 Lieux**
```
Paris
Lyon
Marseille
```

## 📊 **Exemple concret**

### **Transcription originale :**
```
"On a des questions avec les standards de Fortville"
```

### **Avec mots-clés :**
```bash
python advanced_rag_transcription_with_keywords.py audio.mp3 --keywords "Forvia"
```

### **Résultat corrigé :**
```
"On a des questions avec les standards de Forvia"
```

## 🔧 **Comment ça marche**

### **1. Prompt initial**
```python
prompt = "Transcription en français avec les mots-clés suivants : Forvia, Microsoft, Azure. Utilisez ces termes exactement comme spécifiés."
```

### **2. Post-traitement**
```python
corrections = {
    "fortville": "Forvia",
    "forville": "Forvia",
    "forvia": "Forvia"
}
```

### **3. Remplacement intelligent**
```python
# Remplace toutes les variations insensibles à la casse
pattern = re.compile(re.escape(incorrect), re.IGNORECASE)
corrected_text = pattern.sub(correct, corrected_text)
```

## 🚀 **Workflow complet**

### **1. Préparation des mots-clés**
```bash
# Créer un fichier de mots-clés
echo "Forvia" > mes_keywords.txt
echo "Microsoft" >> mes_keywords.txt
echo "Azure" >> mes_keywords.txt
```

### **2. Transcription avec mots-clés**
```bash
python advanced_rag_transcription_with_keywords.py audio.mp3 --keywords-file mes_keywords.txt
```

### **3. Analyse des résultats**
```bash
# Vérifier les corrections
python simple_audio_analyzer.py fichier.json --question "Quels mots-clés sont mentionnés ?"

# Générer des résumés
python resume_audio.py
```

## 📈 **Avantages**

### **✅ Précision améliorée**
- Transcription correcte des noms propres
- Réduction des erreurs de reconnaissance
- Contexte enrichi pour Whisper

### **✅ Flexibilité**
- Mots-clés en ligne de commande ou fichier
- Interface interactive simple
- Support de nombreux domaines

### **✅ Intégration complète**
- Compatible avec tous les scripts d'analyse
- Métadonnées enrichies
- Base vectorielle améliorée

## 🎯 **Cas d'usage**

### **1. Réunions d'entreprise**
```bash
python advanced_rag_transcription_with_keywords.py reunion.mp3 --keywords "Forvia,Microsoft,Azure,PowerBI"
```

### **2. Formations techniques**
```bash
python advanced_rag_transcription_with_keywords.py formation.mp3 --keywords "Python,Docker,Kubernetes,React"
```

### **3. Projets spécifiques**
```bash
python advanced_rag_transcription_with_keywords.py projet.mp3 --keywords "SAP,Oracle,Salesforce,Jira"
```

## 🔍 **Vérification des résultats**

### **Comparer les transcriptions :**
```bash
# Sans mots-clés
grep -i "forvia\|fortville" fichier_original.json

# Avec mots-clés
grep -i "forvia\|fortville" fichier_avec_keywords.json
```

### **Analyser les corrections :**
```bash
python simple_audio_analyzer.py fichier_avec_keywords.json --question "Quels mots-clés sont mentionnés ?"
```

## 💡 **Conseils d'utilisation**

### **✅ Bonnes pratiques**
1. **Liste complète** : Inclure toutes les variations possibles
2. **Noms propres** : Toujours inclure les noms d'entreprises/personnes
3. **Technologies** : Ajouter les acronymes et noms complets
4. **Test** : Vérifier les résultats sur un échantillon

### **❌ À éviter**
1. **Trop de mots-clés** : Peut ralentir la transcription
2. **Mots génériques** : Éviter les mots trop communs
3. **Variations incorrectes** : Vérifier l'orthographe

## 🎉 **Résultat**

**Vous pouvez maintenant :**
1. ✅ **Transcrire correctement** "Forvia" au lieu de "Fortville"
2. ✅ **Personnaliser** la transcription avec vos mots-clés
3. ✅ **Améliorer la précision** de tous vos contenus audio
4. ✅ **Intégrer** les mots-clés dans l'analyse RAG

**🚀 Commencez par :**
```bash
python transcribe_with_keywords.py
```

Et découvrez la puissance de la transcription personnalisée !
