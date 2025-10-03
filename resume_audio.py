#!/usr/bin/env python3
"""
Script simple pour générer des résumés d'audio
Usage : python resume_audio.py
"""

import sys
import subprocess
from pathlib import Path

def find_json_files():
    """Trouve les fichiers JSON disponibles."""
    json_files = list(Path(".").glob("*advanced_rag*.json"))
    return json_files

def main():
    """Fonction principale interactive."""
    print("📊 Générateur de Résumés Audio")
    print("=" * 50)
    
    # Trouver les fichiers JSON
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
        print(f"\n✅ Fichier sélectionné : {selected_file.name}")
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
    
    # Types de résumés disponibles
    summary_types = [
        ("executive", "📊 Résumé Exécutif", "Résumé court pour les dirigeants"),
        ("business", "💼 Résumé Business", "Analyse orientée business"),
        ("detailed", "📋 Résumé Détaillé", "Analyse complète avec transcription"),
        ("all", "🎯 Tous les Résumés", "Génère les 3 types de résumés")
    ]
    
    print(f"\n📋 Types de résumés disponibles :")
    for i, (type_id, name, description) in enumerate(summary_types, 1):
        print(f"   {i}. {name}")
        print(f"      {description}")
    
    # Sélection du type
    try:
        choice = int(input(f"\n🔢 Choisissez un type de résumé (1-{len(summary_types)}) : "))
        if 1 <= choice <= len(summary_types):
            selected_type = summary_types[choice - 1][0]
        else:
            print("❌ Choix invalide")
            return 1
    except ValueError:
        print("❌ Veuillez entrer un nombre valide")
        return 1
    
    # Génération du résumé
    print(f"\n🔄 Génération du résumé {summary_types[choice - 1][1]}...")
    print("-" * 50)
    
    try:
        if selected_type == "all":
            # Générer tous les résumés
            output_dir = f"resumes_{selected_file.stem}"
            cmd = [sys.executable, "audio_summarizer.py", str(selected_file), 
                   "--type", "all", "--output", output_dir]
        else:
            # Générer un seul résumé
            output_file = f"resume_{selected_type}_{selected_file.stem}.md"
            cmd = [sys.executable, "audio_summarizer.py", str(selected_file), 
                   "--type", selected_type, "--output", output_file]
        
        result = subprocess.run(cmd, capture_output=False, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("🎉 Résumé généré avec succès !")
            
            if selected_type == "all":
                print(f"📁 Dossier de sortie : {output_dir}/")
                print("📄 Fichiers générés :")
                output_path = Path(output_dir)
                if output_path.exists():
                    for file in output_path.glob("*.md"):
                        print(f"   - {file.name}")
            else:
                print(f"📄 Fichier généré : resume_{selected_type}_{selected_file.stem}.md")
        else:
            print(f"❌ Erreur lors de la génération : {result.stderr}")
            return 1
    
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return 1
    
    # Proposer de continuer
    print("\n" + "=" * 50)
    continue_choice = input("❓ Voulez-vous générer un autre résumé ? (o/n) : ").strip().lower()
    if continue_choice in ['o', 'oui', 'y', 'yes']:
        return main()  # Récursion pour continuer
    else:
        print("👋 Au revoir !")
        return 0

if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n\n👋 Interruption par l'utilisateur. Au revoir !")
        exit(0)
