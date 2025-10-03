#!/usr/bin/env python3
"""
Script de démonstration pour tester différentes questions sur l'audio
"""

import subprocess
import sys
from pathlib import Path

def run_question(json_file: str, question: str, title: str = None):
    """Lance une question et affiche le résultat."""
    if title:
        print(f"\n{'='*60}")
        print(f"🎯 {title}")
        print(f"{'='*60}")
    
    try:
        result = subprocess.run([
            sys.executable, "simple_audio_analyzer.py", 
            json_file, "--question", question
        ], capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"❌ Erreur: {result.stderr}")
    
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution: {e}")

def main():
    """Fonction principale de démonstration."""
    # Fichier JSON à analyser
    json_file = "test_output_1_advanced_rag_20251003_214507.json"
    
    if not Path(json_file).exists():
        print(f"❌ Le fichier {json_file} n'existe pas")
        print("💡 Assurez-vous d'avoir traité l'audio avec le script RAG avancé")
        return 1
    
    print("🚀 Démonstration de l'analyseur de questions audio")
    print(f"📁 Fichier analysé: {json_file}")
    
    # Questions de démonstration
    questions = [
        ("Quels risques sont identifiés ?", "ANALYSE DES RISQUES"),
        ("Quelles actions doivent être prises ?", "ANALYSE DES ACTIONS"),
        ("Qui fait partie de l'équipe ?", "INFORMATIONS SUR L'ÉQUIPE"),
        ("Quels sont les délais et échéances ?", "ANALYSE TEMPORELLE"),
        ("Quel est l'état de l'architecture ?", "ANALYSE DE L'ARCHITECTURE"),
        ("Quels sont les standards mentionnés ?", "ANALYSE DES STANDARDS")
    ]
    
    for question, title in questions:
        run_question(json_file, question, title)
    
    print(f"\n{'='*60}")
    print("✅ Démonstration terminée!")
    print("💡 Vous pouvez utiliser le script simple_audio_analyzer.py avec vos propres questions")
    print(f"{'='*60}")
    
    return 0

if __name__ == "__main__":
    exit(main())
