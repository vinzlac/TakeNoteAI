#!/usr/bin/env python3
"""
Script principal pour poser des questions sur un fichier audio
Usage simple et intuitif
"""

import sys
import os
from pathlib import Path

def find_json_files():
    """Trouve les fichiers JSON de transcription disponibles."""
    json_files = list(Path(".").glob("*advanced_rag*.json"))
    return json_files

def main():
    """Fonction principale interactive."""
    print("🎤 Analyseur de Questions Audio")
    print("=" * 50)
    
    # Trouver les fichiers JSON disponibles
    json_files = find_json_files()
    
    if not json_files:
        print("❌ Aucun fichier JSON de transcription trouvé.")
        print("💡 Utilisez d'abord : python advanced_rag_transcription.py votre_audio.mp3")
        return 1
    
    # Afficher les fichiers disponibles
    print("📁 Fichiers de transcription disponibles :")
    for i, file in enumerate(json_files, 1):
        print(f"   {i}. {file.name}")
    
    # Sélection du fichier
    if len(json_files) == 1:
        selected_file = json_files[0]
        print(f"\n✅ Fichier sélectionné automatiquement : {selected_file.name}")
    else:
        try:
            choice = int(input(f"\n🔢 Choisissez un fichier (1-{len(json_files)}) : "))
            if 1 <= choice <= len(json_files):
                selected_file = json_files[choice - 1]
            else:
                print("❌ Choix invalide")
                return 1
        except ValueError:
            print("❌ Veuillez entrer un nombre valide")
            return 1
    
    print(f"\n📋 Fichier analysé : {selected_file.name}")
    
    # Questions prédéfinies
    predefined_questions = [
        "Quels risques sont identifiés ?",
        "Quelles actions doivent être prises ?",
        "Qui fait partie de l'équipe ?",
        "Quels sont les délais et échéances ?",
        "Quel est l'état de l'architecture ?",
        "Quels standards sont mentionnés ?"
    ]
    
    print("\n🎯 Questions prédéfinies disponibles :")
    for i, question in enumerate(predefined_questions, 1):
        print(f"   {i}. {question}")
    
    print("\n💡 Ou tapez votre propre question")
    
    while True:
        print("\n" + "="*50)
        choice = input("🔢 Choisissez une question (1-6) ou tapez votre question : ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= len(predefined_questions):
            question = predefined_questions[int(choice) - 1]
        elif choice.lower() in ['quit', 'exit', 'q', '']:
            print("👋 Au revoir !")
            break
        else:
            question = choice
        
        # Exécuter l'analyse
        print(f"\n🔍 Analyse de : \"{question}\"")
        print("-" * 50)
        
        try:
            import subprocess
            result = subprocess.run([
                sys.executable, "simple_audio_analyzer.py", 
                str(selected_file), "--question", question
            ], capture_output=False, text=True, encoding='utf-8')
            
            if result.returncode != 0:
                print("❌ Erreur lors de l'analyse")
        
        except Exception as e:
            print(f"❌ Erreur : {e}")
        
        # Proposer de continuer
        continue_choice = input("\n❓ Voulez-vous poser une autre question ? (o/n) : ").strip().lower()
        if continue_choice not in ['o', 'oui', 'y', 'yes']:
            print("👋 Au revoir !")
            break
    
    return 0

if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n\n👋 Interruption par l'utilisateur. Au revoir !")
        exit(0)
