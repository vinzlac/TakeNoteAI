#!/bin/bash

# TakeNote AI - Script de lancement rapide

# Vérifier si l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo "❌ Environnement virtuel non trouvé."
    echo "📦 Lancement de l'installation..."
    ./install.sh
    if [ $? -ne 0 ]; then
        echo "❌ Installation échouée. Veuillez installer manuellement."
        exit 1
    fi
fi

# Activer l'environnement virtuel
source venv/bin/activate

# Vérifier si des arguments sont fournis
if [ $# -eq 0 ]; then
    echo "🎤 TakeNote AI - Transcription audio"
    echo "===================================="
    echo ""
    echo "Usage: ./run.sh <fichier_audio> [options]"
    echo ""
    echo "Exemples:"
    echo "  ./run.sh audio.mp3"
    echo "  ./run.sh audio.m4a -m large -l fr"
    echo "  ./run.sh audio.wav -f json"
    echo ""
    echo "Options disponibles:"
    echo "  -m, --model     Modèle Whisper (tiny, base, small, medium, large)"
    echo "  -l, --language  Langue (fr, en, es, etc.)"
    echo "  -f, --format    Format de sortie (txt, json, srt, vtt)"
    echo "  -o, --output    Fichier de sortie"
    echo "  --no-clean      Désactiver le nettoyage audio"
    echo "  --analyze-only  Analyser le fichier sans le traiter"
    echo ""
    echo "Pour plus d'informations: python takenote.py --help"
    exit 1
fi

# Lancer TakeNote AI
echo "🚀 Lancement de TakeNote AI..."
python takenote.py "$@"

