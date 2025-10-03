# 🧹 Guide : Nettoyage des Données RAG

## ❓ **Question : "Faut-il nettoyer avant de relancer le RAG ?"**

**Réponse : OUI, c'est recommandé !** Voici pourquoi et comment.

## 🎯 **Pourquoi nettoyer ?**

### **1. Éviter les conflits de données**
- **ChromaDB** peut contenir des embeddings obsolètes
- **Fichiers JSON** anciens peuvent créer de la confusion
- **Mots-clés** générés précédemment peuvent être périmés

### **2. Partir d'une base propre**
- **Nouvelle transcription** avec des mots-clés mis à jour
- **Embeddings frais** dans ChromaDB
- **Résultats cohérents** et fiables

### **3. Éviter l'accumulation**
- **Fichiers volumineux** qui s'accumulent
- **Données incohérentes** entre les versions
- **Confusion** entre anciens et nouveaux résultats

## 📊 **État actuel de vos données**

D'après le scan, vous avez :
```
🗄️  ChromaDB: ✅ Présent (0.74 MB, 6 fichiers)
📄 Fichiers JSON: 7 fichier(s) (0.53 MB total)
📝 Fichiers de résumé: 3 fichier(s)
💡 Recommandation: Nettoyage recommandé avant un nouveau RAG
```

## 🧹 **Options de nettoyage**

### **1. Nettoyage complet (recommandé)**
```bash
# Avec confirmation
python clean_rag_data.py --all

# Sans confirmation (attention !)
python clean_rag_data.py --all --force
```

### **2. Nettoyage sélectif**
```bash
# Seulement ChromaDB
python clean_rag_data.py --chromadb

# Seulement les fichiers JSON
python clean_rag_data.py --json

# Seulement les résumés
python clean_rag_data.py --summaries

# Seulement les mots-clés
python clean_rag_data.py --keywords
```

### **3. Vérifier l'état**
```bash
# Voir ce qui peut être nettoyé
python clean_rag_data.py --status
```

## 🚀 **Workflow recommandé**

### **Avant un nouveau RAG :**
```bash
# 1. Vérifier l'état
python clean_rag_data.py --status

# 2. Nettoyer tout
python clean_rag_data.py --all

# 3. Relancer le RAG avec de nouveaux mots-clés
python advanced_rag_transcription_with_keywords.py audio.mp3 --keywords-file nouveaux_mots_cles.txt
```

### **Après le RAG :**
```bash
# 4. Générer de nouveaux mots-clés si nécessaire
python generate_keywords_from_transcription.py nouveau_fichier.json --top 25

# 5. Utiliser les scripts d'analyse
python ask_audio.py
python show_summary.py
```

## ⚠️ **Attention !**

### **Données supprimées :**
- **ChromaDB** : Base de données vectorielle (embeddings)
- **Fichiers JSON** : Transcriptions RAG
- **Résumés** : Fichiers .md générés
- **Mots-clés** : Fichiers .txt générés

### **Données conservées :**
- **Scripts Python** : Tous les scripts restent
- **Audio original** : Fichiers .mp3 conservés
- **Documentation** : Guides .md conservés

## 🔄 **Scénarios d'utilisation**

### **Scénario 1 : Nouveau fichier audio**
```bash
python clean_rag_data.py --all
python advanced_rag_transcription_with_keywords.py nouveau_audio.mp3
```

### **Scénario 2 : Améliorer la transcription existante**
```bash
python clean_rag_data.py --all
python generate_keywords_from_transcription.py ancien_fichier.json --top 30
python advanced_rag_transcription_with_keywords.py audio.mp3 --keywords-file mots_cles_ameliores.txt
```

### **Scénario 3 : Tester différents mots-clés**
```bash
# Premier test
python clean_rag_data.py --all
python advanced_rag_transcription_with_keywords.py audio.mp3 --keywords "Azure, Microsoft"

# Deuxième test avec d'autres mots-clés
python clean_rag_data.py --all
python advanced_rag_transcription_with_keywords.py audio.mp3 --keywords "JIT, Zven, Mako"
```

## 🎯 **Recommandations**

### **✅ Faire avant chaque nouveau RAG :**
1. **Nettoyer ChromaDB** (évite les embeddings obsolètes)
2. **Supprimer les anciens JSON** (évite la confusion)
3. **Générer de nouveaux mots-clés** (améliore la transcription)

### **❌ Ne pas faire :**
- Nettoyer sans sauvegarder les résultats importants
- Utiliser `--force` sans vérifier d'abord
- Nettoyer pendant qu'un RAG est en cours

## 🛡️ **Sécurité**

Le script demande **toujours confirmation** sauf avec `--force` :
```bash
❓ Voulez-vous supprimer TOUTES ces données ? (oui/non):
```

**Répondez "oui"** pour confirmer ou **"non"** pour annuler.

## 🎉 **Résultat**

Après le nettoyage, vous aurez :
- ✅ **Base ChromaDB propre**
- ✅ **Aucun fichier JSON obsolète**
- ✅ **Aucun résumé périmé**
- ✅ **Prêt pour un nouveau RAG**

**🚀 Votre prochaine transcription sera plus précise et cohérente !**
