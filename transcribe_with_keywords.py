#!/usr/bin/env python3
"""
Script simple pour transcrire avec des mots-clés personnalisés
"""

import sys
import subprocess
from pathlib import Path

def find_audio_files():
    """Trouve les fichiers audio disponibles."""
    audio_extensions = ['.mp3', '.wav', '.m4a', '.flac', '.ogg']
    audio_files = []
    
    for ext in audio_extensions:
        audio_files.extend(Path(".").glob(f"*{ext}"))
    
    return audio_files

def main():
    """Fonction principale."""
    print("🎤 Transcription avec Mots-Clés Personnalisés")
    print("=" * 50)
    
    # Trouver les fichiers audio
    audio_files = find_audio_files()
    
    if not audio_files:
        print("❌ Aucun fichier audio trouvé.")
        print("💡 Placez vos fichiers audio (.mp3, .wav, etc.) dans ce dossier")
        return 1
    
    # Afficher les fichiers disponibles
    print("📁 Fichiers audio disponibles :")
    for i, file in enumerate(audio_files, 1):
        print(f"   {i}. {file.name}")
    
    # Sélection du fichier
    if len(audio_files) == 1:
        selected_file = audio_files[0]
        print(f"\n✅ Fichier sélectionné : {selected_file.name}")
    else:
        try:
            choice = int(input(f"\n🔢 Choisissez un fichier (1-{len(audio_files)}) : "))
            if 1 <= choice <= len(audio_files):
                selected_file = audio_files[choice - 1]
            else:
                print("❌ Choix invalide")
                return 1
        except ValueError:
            print("❌ Veuillez entrer un nombre valide")
            return 1
    
    # Options de mots-clés
    print(f"\n🎯 Options de mots-clés :")
    print("   1. 📝 Saisir des mots-clés manuellement")
    print("   2. 📄 Utiliser le fichier keywords.txt")
    print("   3. 🚫 Pas de mots-clés")
    
    try:
        choice = int(input(f"\n🔢 Choisissez une option (1-3) : "))
        
        keywords = []
        
        if choice == 1:
            keywords_input = input("\n📝 Entrez vos mots-clés (séparés par des virgules) : ")
            keywords = [kw.strip() for kw in keywords_input.split(",") if kw.strip()]
        
        elif choice == 2:
            keywords_file = Path("keywords.txt")
            if keywords_file.exists():
                with open(keywords_file, 'r', encoding='utf-8') as f:
                    keywords = [line.strip() for line in f if line.strip()]
                print(f"✅ {len(keywords)} mots-clés chargés depuis {keywords_file.name}")
            else:
                print(f"❌ Fichier {keywords_file.name} non trouvé")
                return 1
        
        elif choice == 3:
            keywords = []
        
        else:
            print("❌ Choix invalide")
            return 1
    
    except ValueError:
        print("❌ Veuillez entrer un nombre valide")
        return 1
    
    # Construire la commande
    cmd = [sys.executable, "advanced_rag_transcription_with_keywords.py", str(selected_file)]
    
    if keywords:
        keywords_str = ",".join(keywords)
        cmd.extend(["--keywords", keywords_str])
        print(f"\n🎯 Mots-clés appliqués : {', '.join(keywords)}")
    else:
        print(f"\n🚫 Aucun mot-clé appliqué")
    
    # Lancer la transcription
    print(f"\n🔄 Lancement de la transcription...")
    print(f"⏳ Cela peut prendre quelques minutes...")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, capture_output=False, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("\n🎉 Transcription terminée avec succès !")
            
            if keywords:
                print(f"\n✅ Mots-clés appliqués : {', '.join(keywords)}")
                print("💡 Vérifiez le fichier JSON généré pour voir les corrections")
            
            print(f"\n📄 Fichier JSON généré avec la transcription")
            print(f"🚀 Vous pouvez maintenant utiliser :")
            print(f"   - python resume_audio.py")
            print(f"   - python simple_audio_analyzer.py fichier.json --question \"Votre question\"")
        else:
            print("\n❌ Erreur lors de la transcription")
            return 1
    
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n\n👋 Interruption par l'utilisateur. Au revoir !")
        exit(0)
