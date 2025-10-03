#!/usr/bin/env python3
"""
Script de démarrage pour l'analyse audio
Guide l'utilisateur à travers le workflow complet
"""

import sys
import subprocess
from pathlib import Path

def check_json_files():
    """Vérifie si des fichiers JSON existent."""
    return list(Path(".").glob("*advanced_rag*.json"))

def check_audio_files():
    """Vérifie si des fichiers audio existent."""
    audio_extensions = ['.mp3', '.wav', '.m4a', '.flac', '.ogg']
    audio_files = []
    
    for ext in audio_extensions:
        audio_files.extend(Path(".").glob(f"*{ext}"))
    
    return audio_files

def main():
    """Fonction principale."""
    print("🎤 Analyseur Audio - Démarrage")
    print("=" * 50)
    
    # Vérifier les fichiers existants
    json_files = check_json_files()
    audio_files = check_audio_files()
    
    print(f"📁 Fichiers audio trouvés : {len(audio_files)}")
    print(f"📄 Fichiers JSON trouvés : {len(json_files)}")
    print()
    
    # Décider du workflow
    if json_files:
        print("✅ Fichiers JSON disponibles !")
        print("🎯 Vous pouvez directement analyser vos transcriptions.")
        print()
        
        # Afficher les fichiers disponibles
        print("📋 Fichiers de transcription disponibles :")
        for i, file in enumerate(json_files, 1):
            print(f"   {i}. {file.name}")
        
        print()
        print("🚀 Options disponibles :")
        print("   1. 📊 Générer des résumés")
        print("   2. ❓ Poser des questions")
        print("   3. 📺 Afficher dans le terminal")
        print("   4. 🔍 Vérifier les fichiers")
        
        try:
            choice = int(input("\n🔢 Que voulez-vous faire ? (1-4) : "))
            
            if choice == 1:
                print("\n🔄 Lancement du générateur de résumés...")
                subprocess.run([sys.executable, "resume_audio.py"])
            elif choice == 2:
                print("\n🔄 Lancement de l'interface de questions...")
                subprocess.run([sys.executable, "ask_audio.py"])
            elif choice == 3:
                print("\n🔄 Lancement de l'affichage simple...")
                subprocess.run([sys.executable, "show_summary.py"])
            elif choice == 4:
                print("\n🔄 Vérification des fichiers...")
                subprocess.run([sys.executable, "check_files.py"])
            else:
                print("❌ Choix invalide")
                return 1
                
        except ValueError:
            print("❌ Veuillez entrer un nombre valide")
            return 1
        except KeyboardInterrupt:
            print("\n👋 Au revoir !")
            return 0
    
    elif audio_files:
        print("🎵 Fichiers audio trouvés !")
        print("📝 Vous devez d'abord créer les transcriptions JSON.")
        print()
        
        # Afficher les fichiers audio
        print("📋 Fichiers audio disponibles :")
        for i, file in enumerate(audio_files, 1):
            print(f"   {i}. {file.name}")
        
        print()
        print("🚀 Options disponibles :")
        print("   1. 🎤 Traiter un fichier audio (créer JSON)")
        print("   2. 📖 Voir le guide complet")
        print("   3. ❌ Annuler")
        
        try:
            choice = int(input("\n🔢 Que voulez-vous faire ? (1-3) : "))
            
            if choice == 1:
                if len(audio_files) == 1:
                    selected_file = audio_files[0]
                    print(f"\n✅ Fichier sélectionné : {selected_file.name}")
                else:
                    try:
                        file_choice = int(input(f"\n🔢 Choisissez un fichier audio (1-{len(audio_files)}) : "))
                        if 1 <= file_choice <= len(audio_files):
                            selected_file = audio_files[file_choice - 1]
                        else:
                            print("❌ Choix invalide")
                            return 1
                    except ValueError:
                        print("❌ Veuillez entrer un nombre valide")
                        return 1
                
                print(f"\n🔄 Traitement de {selected_file.name}...")
                print("⏳ Cela peut prendre quelques minutes...")
                print()
                
                # Lancer le traitement RAG
                result = subprocess.run([
                    sys.executable, "advanced_rag_transcription.py", 
                    str(selected_file)
                ])
                
                if result.returncode == 0:
                    print("\n✅ Traitement terminé !")
                    print("🎯 Vous pouvez maintenant analyser vos transcriptions.")
                    print("\n🔄 Lancement de l'interface d'analyse...")
                    subprocess.run([sys.executable, "resume_audio.py"])
                else:
                    print("\n❌ Erreur lors du traitement")
                    return 1
                    
            elif choice == 2:
                print("\n📖 Guide complet disponible dans :")
                print("   - WORKFLOW_COMPLET.md")
                print("   - GUIDE_RESUMES.md")
                print("   - GUIDE_AFFICHAGE.md")
            elif choice == 3:
                print("👋 Au revoir !")
                return 0
            else:
                print("❌ Choix invalide")
                return 1
                
        except ValueError:
            print("❌ Veuillez entrer un nombre valide")
            return 1
        except KeyboardInterrupt:
            print("\n👋 Au revoir !")
            return 0
    
    else:
        print("❌ Aucun fichier audio ou JSON trouvé.")
        print()
        print("💡 Pour commencer :")
        print("   1. Placez vos fichiers audio (.mp3, .wav, etc.) dans ce dossier")
        print("   2. Relancez ce script")
        print("   3. Ou utilisez directement : python advanced_rag_transcription.py votre_audio.mp3")
        
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n\n👋 Interruption par l'utilisateur. Au revoir !")
        exit(0)
