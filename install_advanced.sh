#!/bin/bash

# Script d'installation pour les fonctionnalités avancées RAG
# TakeNote AI - Installation des dépendances avancées

set -e

echo "🚀 Installation des fonctionnalités avancées TakeNote AI"
echo "=================================================="

# Vérifier que l'environnement virtuel est activé
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Environnement virtuel non détecté"
    echo "💡 Activez votre environnement virtuel avec: source venv/bin/activate"
    exit 1
fi

echo "✅ Environnement virtuel détecté: $VIRTUAL_ENV"

# Mettre à jour pip
echo "🔄 Mise à jour de pip..."
pip install --upgrade pip

# Installation des dépendances de base
echo "🔄 Installation des dépendances de base..."
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

# Installation de SpeechBrain
echo "🔄 Installation de SpeechBrain..."
pip install speechbrain

# Installation des composants RAG
echo "🔄 Installation des composants RAG..."
pip install sentence-transformers
pip install keybert
pip install chromadb

# Installation de spaCy et modèle français
echo "🔄 Installation de spaCy..."
pip install spacy
python -m spacy download fr_core_news_sm

# Installation des dépendances supplémentaires
echo "🔄 Installation des dépendances supplémentaires..."
pip install transformers
pip install datasets
pip install scikit-learn
pip install numpy
pip install pandas

# Vérification de l'installation
echo "🧪 Vérification de l'installation..."

python -c "
import torch
import torchaudio
import speechbrain
import sentence_transformers
import keybert
import chromadb
import spacy
print('✅ Toutes les dépendances sont installées correctement!')
print(f'   - PyTorch: {torch.__version__}')
print(f'   - TorchAudio: {torchaudio.__version__}')
print(f'   - SpeechBrain: {speechbrain.__version__}')
print(f'   - Sentence Transformers: {sentence_transformers.__version__}')
print(f'   - KeyBERT: {keybert.__version__}')
print(f'   - ChromaDB: {chromadb.__version__}')
"

echo ""
echo "🎉 Installation terminée avec succès!"
echo ""
echo "📋 Fonctionnalités disponibles:"
echo "   ✅ Transcription avancée avec SpeechBrain"
echo "   ✅ Extraction de mots-clés métiers avec KeyBERT"
echo "   ✅ Embeddings sémantiques avec Sentence Transformers"
echo "   ✅ Base de données vectorielle avec ChromaDB"
echo "   ✅ Traitement de texte avec spaCy"
echo ""
echo "🚀 Utilisation:"
echo "   python advanced_rag_transcription.py audio.mp3"
echo ""
echo "💡 Pour plus d'options:"
echo "   python advanced_rag_transcription.py --help"
