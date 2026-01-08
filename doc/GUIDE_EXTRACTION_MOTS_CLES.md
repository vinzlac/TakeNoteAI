# 🔍 Guide d'Extraction des Mots-Clés Inconnus

## 🎯 **Problème résolu : Extraire automatiquement les mots-clés techniques**

**OUI, c'est possible d'extraire automatiquement tous les mots-clés inconnus comme "JIT" de vos transcriptions !**

## 🔧 **Scripts disponibles**

### **1. Script principal - Générateur automatique :**
```bash
python generate_keywords_from_transcription.py fichier.json --top 30
```

### **2. Script spécialisé - Extraction technique :**
```bash
python extract_technical_keywords.py fichier.json --top 25
```

### **3. Script général - Extraction inconnue :**
```bash
python extract_unknown_keywords.py fichier.json --top 20
```

## 🚀 **Utilisation recommandée**

### **Étape 1 : Générer automatiquement les mots-clés**
```bash
python generate_keywords_from_transcription.py votre_transcription.json --top 30
```

**Résultat** : Fichier `keywords_generated_votre_transcription.txt` avec tous les mots-clés détectés

### **Étape 2 : Utiliser les mots-clés générés**
```bash
python advanced_rag_transcription_with_keywords.py audio.mp3 --keywords-file keywords_generated_votre_transcription.txt
```

## 📊 **Exemple concret avec votre fichier**

### **Mots-clés détectés automatiquement :**
```
Zven, Mako, Vincent, Mellex, Forvia, Edward, Malek, GIT, ETI, V1, V2, go-live, Hip-Hamp, Rusem, MacO, Simon, Arne, Diati, Wiss, Ong, Cote, Hip, Maco, Vue, Merci, Enfin, Parce, est-ce, Moi, go-life
```

### **Utilisation :**
```bash
# Générer les mots-clés
python generate_keywords_from_transcription.py test_output_advanced_rag_keywords_111_20251003_221142.json --top 30

# Utiliser avec la transcription
python advanced_rag_transcription_with_keywords.py test_output_1.mp3 --keywords-file keywords_generated_test_output_advanced_rag_keywords_111_20251003_221142.txt
```

## 🎯 **Types de mots-clés détectés**

### **✅ Acronymes techniques**
- **JIT** (Just-In-Time)
- **GIT** (Git)
- **ETI** (Entreprise)
- **API** (Application Programming Interface)

### **✅ Noms propres**
- **Zven** (Nom de personne)
- **Mako** (Nom de personne)
- **Vincent** (Nom de personne)
- **Mellex** (Nom de personne)
- **Forvia** (Nom d'entreprise)
- **Edward** (Nom de personne)
- **Malek** (Nom de personne)

### **✅ Versions et numéros**
- **V1** (Version 1)
- **V2** (Version 2)
- **V3** (Version 3)

### **✅ Mots composés techniques**
- **go-live** (Mise en production)
- **go-life** (Phase de vie)
- **code-review** (Révision de code)
- **hip-hamp** (Nom technique)

### **✅ CamelCase**
- **MacO** (Nom technique)
- **Rusem** (Nom technique)

## 📁 **Fichiers créés**

### **Scripts d'extraction :**
1. **`generate_keywords_from_transcription.py`** - Générateur automatique principal
2. **`extract_technical_keywords.py`** - Extraction technique spécialisée
3. **`extract_unknown_keywords.py`** - Extraction générale

### **Fichiers de sortie :**
4. **`keywords_generated_*.txt`** - Fichier de mots-clés généré automatiquement
5. **`mots_cles_techniques_*.json`** - Résultats détaillés de l'extraction technique
6. **`mots_cles_inconnus_*.json`** - Résultats de l'extraction générale

## 🔍 **Comment ça marche**

### **1. Analyse du texte**
- Recherche des patterns techniques (acronymes, CamelCase, etc.)
- Détection des noms propres
- Identification des mots composés
- Extraction des versions et numéros

### **2. Filtrage intelligent**
- Exclusion des mots français courants
- Validation des mots-clés techniques
- Déduplication automatique
- Tri par fréquence d'apparition

### **3. Génération du fichier**
- Création d'un fichier de mots-clés prêt à utiliser
- Format compatible avec le script de transcription
- Documentation automatique

## 🎯 **Workflow complet**

### **1. Transcrir avec mots-clés de base**
```bash
python advanced_rag_transcription_with_keywords.py audio.mp3 --keywords "Forvia,Microsoft,Azure"
```

### **2. Extraire les mots-clés manqués**
```bash
python generate_keywords_from_transcription.py transcription.json --top 30
```

### **3. Re-transcrir avec tous les mots-clés**
```bash
python advanced_rag_transcription_with_transcription.py audio.mp3 --keywords-file keywords_generated.txt
```

### **4. Vérifier les améliorations**
```bash
python simple_audio_analyzer.py nouvelle_transcription.json --question "Quels mots-clés sont mentionnés ?"
```

## 📈 **Avantages**

### **✅ Détection automatique**
- Plus besoin de deviner les mots-clés
- Détection de tous les termes techniques
- Identification des noms propres
- Extraction des acronymes

### **✅ Amélioration continue**
- Analyse des transcriptions existantes
- Mise à jour automatique des mots-clés
- Apprentissage des patterns techniques
- Optimisation des performances

### **✅ Intégration complète**
- Compatible avec tous les scripts existants
- Format standardisé
- Documentation automatique
- Workflow optimisé

## 🎉 **Résultat final**

**Vous pouvez maintenant :**
1. ✅ **Extraire automatiquement** tous les mots-clés techniques de vos transcriptions
2. ✅ **Détecter les noms propres** et acronymes manqués
3. ✅ **Générer des fichiers de mots-clés** prêts à utiliser
4. ✅ **Améliorer continuellement** la précision de transcription

**🚀 Commencez par :**
```bash
python generate_keywords_from_transcription.py votre_transcription.json --top 30
```

Et découvrez tous les mots-clés techniques cachés dans vos transcriptions !
