# 🚀 TakeNote AI - Fonctionnalités Avancées RAG

Extension de TakeNote AI avec transcription avancée, extraction de mots-clés métiers et RAG (Retrieval-Augmented Generation).

## 🎯 Fonctionnalités Avancées

### 🎤 **Transcription Avancée**
- **SpeechBrain** : Alternative à Whisper, plus précise pour certains domaines
- **Modèles spécialisés** : Support des modèles fine-tunés pour domaines métiers
- **Multilingue** : Support natif du français et autres langues

### 🔍 **Extraction de Mots-Clés Métiers**
- **KeyBERT** : Extraction intelligente de mots-clés avec scores
- **Filtrage métier** : Détection automatique des termes techniques
- **N-grammes** : Extraction de phrases-clés (1-3 mots)
- **Diversité** : Évite la redondance avec MMR (Maximal Marginal Relevance)

### 🧠 **Embeddings Sémantiques**
- **Sentence Transformers** : Modèles multilingues optimisés
- **Similarité sémantique** : Recherche par sens, pas par mots exacts
- **Multilingue** : Support français/anglais natif

### 💾 **Base de Données Vectorielle**
- **ChromaDB** : Stockage et recherche vectorielle performante
- **Persistance** : Données sauvegardées entre les sessions
- **Métadonnées** : Enrichissement des documents avec tags

## 🛠️ Installation

### Installation Automatique (Recommandée)
```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Installer les fonctionnalités avancées
./install_advanced.sh
```

### Installation Manuelle
```bash
# Dépendances de base
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

# Transcription avancée
pip install speechbrain

# RAG et embeddings
pip install sentence-transformers keybert chromadb

# Traitement de texte
pip install spacy
python -m spacy download fr_core_news_sm

# Dépendances supplémentaires
pip install transformers datasets scikit-learn
```

## 🚀 Utilisation

### Script Principal
```bash
# Traitement complet avec RAG
python advanced_rag_transcription.py audio.mp3

# Avec options avancées
python advanced_rag_transcription.py audio.mp3 \
  --transcription-model "speechbrain/asr-wav2vec2-commonvoice-fr" \
  --embedding-model "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2" \
  --output results.json
```

### Démonstration
```bash
# Tester les fonctionnalités sans fichier audio
python demo_rag.py
```

### Recherche dans la Base
```bash
# Rechercher des documents similaires
python advanced_rag_transcription.py audio.mp3 --search "architecture système"
```

## 📊 Exemple de Sortie

```json
{
  "transcription": {
    "text": "Nous discutons de l'architecture du projet...",
    "method": "speechbrain",
    "language": "fr"
  },
  "business_keywords": [
    ["architecture projet", 0.85],
    ["développement équipe", 0.78],
    ["code review", 0.72],
    ["déploiement production", 0.68]
  ],
  "metadata": {
    "filename": "reunion.mp3",
    "business_keywords": ["architecture projet", "développement équipe"],
    "embeddings_available": true
  },
  "embeddings_available": true,
  "vector_db_stored": true
}
```

## 🔧 Configuration Avancée

### Modèles de Transcription
- `speechbrain/asr-wav2vec2-commonvoice-fr` : Français (recommandé)
- `speechbrain/asr-wav2vec2-commonvoice-en` : Anglais
- `speechbrain/asr-crdnn-commonvoice-fr` : Modèle plus léger

### Modèles d'Embeddings
- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` : Multilingue (recommandé)
- `sentence-transformers/all-MiniLM-L6-v2` : Plus rapide
- `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` : Plus précis

### Mots-Clés Métiers Détectés
Le système détecte automatiquement les termes liés à :
- **Développement** : code, architecture, tests, déploiement
- **Projet** : équipe, planning, méthodologie, livrables
- **Technique** : système, intégration, performance, sécurité
- **Métier** : processus, qualité, maintenance, support

## 🎯 Cas d'Usage

### 1. **Réunions Techniques**
```bash
python advanced_rag_transcription.py reunion_tech.mp3
```
- Extraction des décisions techniques
- Identification des responsables
- Mots-clés : architecture, déploiement, tests

### 2. **Formations**
```bash
python advanced_rag_transcription.py formation.mp3 --search "concepts clés"
```
- Indexation du contenu pédagogique
- Recherche par concepts
- Mots-clés : méthodologie, bonnes pratiques

### 3. **Interviews**
```bash
python advanced_rag_transcription.py interview.mp3
```
- Extraction des compétences mentionnées
- Identification des projets
- Mots-clés : technologies, expérience, équipe

## 🔍 Recherche Avancée

### Recherche Sémantique
```python
# Rechercher des documents similaires
results = processor.search_similar_documents("architecture microservices", top_k=5)

for doc in results:
    print(f"Texte: {doc['text']}")
    print(f"Score: {doc['distance']}")
    print(f"Métadonnées: {doc['metadata']}")
```

### Filtrage par Métadonnées
```python
# Recherche avec filtres
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=10,
    where={"type": "architecture"}  # Filtrer par type
)
```

## 📈 Performance

### Comparaison des Modèles
| Modèle | Précision | Vitesse | Taille | Usage |
|--------|-----------|---------|--------|-------|
| SpeechBrain | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | Recommandé |
| Whisper Base | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Rapide |
| Whisper Large | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | Précision max |

### Optimisations
- **GPU** : Accélération automatique si disponible
- **Batch Processing** : Traitement par lots pour plusieurs fichiers
- **Cache** : Modèles mis en cache pour réutilisation

## 🔧 Dépannage

### Erreur SpeechBrain
```
ModuleNotFoundError: No module named 'speechbrain'
```
**Solution** : `pip install speechbrain`

### Erreur KeyBERT
```
ImportError: cannot import name 'KeyBERT'
```
**Solution** : `pip install keybert`

### Erreur ChromaDB
```
chromadb.errors.InvalidCollectionException
```
**Solution** : Supprimer le dossier `chroma_db` et relancer

### Mémoire insuffisante
```
CUDA out of memory
```
**Solutions** :
- Utiliser `--device cpu`
- Réduire la taille du batch
- Utiliser un modèle plus petit

## 📚 Ressources

### Documentation
- [SpeechBrain](https://speechbrain.github.io/)
- [KeyBERT](https://maartengr.github.io/KeyBERT/)
- [Sentence Transformers](https://www.sbert.net/)
- [ChromaDB](https://docs.trychroma.com/)

### Modèles Disponibles
- [Hugging Face SpeechBrain](https://huggingface.co/speechbrain)
- [Sentence Transformers Models](https://www.sbert.net/docs/pretrained_models.html)

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Ajouter de nouveaux modèles de transcription
- Améliorer l'extraction de mots-clés métiers
- Optimiser les performances
- Ajouter de nouveaux cas d'usage

---

**TakeNote AI Advanced** - Transcription intelligente avec RAG et mots-clés métiers 🚀
