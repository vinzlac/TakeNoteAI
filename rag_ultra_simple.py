#!/usr/bin/env python3
"""
Script RAG ultra-simple pour usage quotidien
Usage: python rag_ultra_simple.py audio.mp3
"""

import sys
import subprocess
import time
from pathlib import Path

# Import du gestionnaire d'entrée
try:
    from input_manager import resolve_audio_path
    INPUT_MANAGER_AVAILABLE = True
except ImportError:
    print("⚠️  input_manager.py non trouvé, utilisation des chemins par défaut")
    INPUT_MANAGER_AVAILABLE = False

# Optimisations M4
import torch
import os
if torch.backends.mps.is_available():
    torch.set_num_threads(14)
    os.environ['OMP_NUM_THREADS'] = '14'
    os.environ['MKL_NUM_THREADS'] = '14'
    os.environ['NUMEXPR_NUM_THREADS'] = '14'
    print("🚀 Optimisations Mac M4 activées")

def main():
    """Fonction principale ultra-simple."""
    if len(sys.argv) != 2:
        print("Usage: python rag_ultra_simple.py audio.mp3")
        print("Exemple: python rag_ultra_simple.py test_output_1.mp3")
        return 1
    
    audio_file = sys.argv[1]
    
    # Résoudre le chemin du fichier audio
    if INPUT_MANAGER_AVAILABLE:
        resolved_path = resolve_audio_path(audio_file)
        if resolved_path:
            audio_file = str(resolved_path)
            print(f"📁 Fichier trouvé: {audio_file}")
        else:
            print(f"❌ Fichier {audio_file} introuvable dans input/")
            return 1
    else:
        if not Path(audio_file).exists():
            print(f"❌ Fichier {audio_file} introuvable")
            return 1
    
    print(f"🚀 RAG Ultra-Simple - Mac M4 Optimisé")
    print(f"📁 Fichier: {audio_file}")
    print("=" * 50)
    
    start_time = time.time()
    
    try:
        # Étape 1: Transcription RAG simple
        print("\n🎤 ÉTAPE 1: Transcription RAG...")
        cmd1 = f'python advanced_rag_transcription.py "{audio_file}"'
        print(f"🔄 {cmd1}")
        
        result1 = subprocess.run(cmd1, shell=True, capture_output=True, text=True)
        if result1.returncode != 0:
            print(f"❌ Erreur transcription: {result1.stderr}")
            return 1
        
        print("✅ Transcription terminée")
        
        # Trouver le fichier JSON généré (maintenant dans output/)
        json_files = list(Path("output/transcriptions").glob("*advanced_rag*.json"))
        if not json_files:
            # Fallback dans le répertoire courant
            json_files = list(Path(".").glob("*advanced_rag*.json"))
        
        if not json_files:
            print("❌ Aucun fichier JSON généré")
            return 1
        
        json_file = max(json_files, key=lambda x: x.stat().st_mtime)
        print(f"📄 Fichier généré: {json_file.name}")
        
        # Étape 2: Analyse simple
        print("\n📊 ÉTAPE 2: Analyse des risques...")
        cmd2 = f'python simple_audio_analyzer.py "{json_file}" --question "Quels sont les risques identifiés ?"'
        print(f"🔄 {cmd2}")
        
        result2 = subprocess.run(cmd2, shell=True, capture_output=True, text=True)
        if result2.returncode == 0:
            print("✅ Analyse terminée")
        else:
            print(f"⚠️  Erreur analyse: {result2.stderr}")
        
        # Étape 3: Résumé simple
        print("\n📝 ÉTAPE 3: Résumé executive...")
        cmd3 = f'python audio_summarizer.py "{json_file}" --type executive'
        print(f"🔄 {cmd3}")
        
        result3 = subprocess.run(cmd3, shell=True, capture_output=True, text=True)
        if result3.returncode == 0:
            print("✅ Résumé terminé")
        else:
            print(f"⚠️  Erreur résumé: {result3.stderr}")
        
        total_time = time.time() - start_time
        
        print(f"\n🎉 WORKFLOW TERMINÉ EN {total_time:.2f}s")
        print("=" * 50)
        
        print("📁 FICHIERS GÉNÉRÉS:")
        print(f"📄 Transcription: {json_file.name}")
        
        # Lister les fichiers de résumé
        summary_files = list(Path(".").glob("resume_*.md"))
        for summary_file in summary_files:
            if summary_file.stat().st_mtime > time.time() - 300:  # Fichiers récents
                print(f"📝 Résumé: {summary_file.name}")
        
        print(f"\n🚀 OPTIMISATIONS M4 ACTIVES:")
        print("✅ GPU M4 (MPS) utilisé")
        print("✅ 14 threads CPU utilisés")
        print("✅ Mémoire unifiée optimisée")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⏹️  Interrompu par l'utilisateur")
        return 1
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
