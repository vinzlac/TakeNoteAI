#!/usr/bin/env python3
"""
Script RAG simple pour usage quotidien
Usage: python rag_simple.py audio.mp3
"""

import sys
import subprocess
from pathlib import Path

# Optimisations M4
import torch
import os
if torch.backends.mps.is_available():
    torch.set_num_threads(14)
    os.environ['OMP_NUM_THREADS'] = '14'
    os.environ['MKL_NUM_THREADS'] = '14'
    os.environ['NUMEXPR_NUM_THREADS'] = '14'

def main():
    """Fonction principale simplifiée."""
    if len(sys.argv) != 2:
        print("Usage: python rag_simple.py audio.mp3")
        print("Exemple: python rag_simple.py test_output_1.mp3")
        return 1
    
    audio_file = sys.argv[1]
    
    if not Path(audio_file).exists():
        print(f"❌ Fichier {audio_file} introuvable")
        return 1
    
    print(f"🚀 RAG Simple - Mac M4 Optimisé")
    print(f"📁 Fichier: {audio_file}")
    print("=" * 50)
    
    # Exécuter le workflow complet avec paramètres par défaut
    cmd = f'python rag_complete_workflow.py "{audio_file}"'
    
    print(f"🔄 Exécution du workflow complet...")
    print(f"⏱️  Temps estimé: 15-30 secondes")
    
    try:
        result = subprocess.run(cmd, shell=True)
        return result.returncode
    except KeyboardInterrupt:
        print("\n⏹️  Interrompu par l'utilisateur")
        return 1
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
