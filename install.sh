#!/bin/bash

# TakeNote AI - Script d'installation automatique

set -e  # Arrêter en cas d'erreur

echo "🚀 Installation de TakeNote AI"
echo "================================"

# Vérification de Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $PYTHON_VERSION détecté"

# Vérification de FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg n'est pas installé."
    echo "📦 Installation de FFmpeg..."
    
    # Détection du système
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install ffmpeg
        else
            echo "❌ Homebrew n'est pas installé. Installez FFmpeg manuellement:"
            echo "   brew install ffmpeg"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y ffmpeg
        elif command -v yum &> /dev/null; then
            sudo yum install -y ffmpeg
        else
            echo "❌ Gestionnaire de paquets non supporté. Installez FFmpeg manuellement."
            exit 1
        fi
    else
        echo "❌ Système non supporté. Installez FFmpeg manuellement."
        exit 1
    fi
else
    echo "✅ FFmpeg est déjà installé"
fi

# Création de l'environnement virtuel
echo "📦 Création de l'environnement virtuel..."
python3 -m venv venv

# Activation de l'environnement virtuel
echo "🔄 Activation de l'environnement virtuel..."
source venv/bin/activate

# Mise à jour de pip
echo "⬆️  Mise à jour de pip..."
pip install --upgrade pip

# Installation des dépendances
echo "📚 Installation des dépendances Python..."
pip install -r requirements.txt

# Test d'installation
echo "🧪 Test d'installation..."
python3 -c "import whisper, ffmpeg; print('✅ Toutes les dépendances sont installées')"

echo ""
echo "🎉 Installation terminée avec succès!"
echo ""
echo "📖 Pour utiliser TakeNote AI:"
echo "   1. Activez l'environnement virtuel: source venv/bin/activate"
echo "   2. Lancez l'application: python takenote.py votre_fichier.mp3"
echo ""
echo "📚 Consultez le README.md pour plus d'informations."

