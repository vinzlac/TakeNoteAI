#!/usr/bin/env python3
"""
Script pour afficher un résumé directement dans le terminal (sans sauvegarder)
"""

import sys
import subprocess
from pathlib import Path

def find_json_files():
    """Trouve les fichiers JSON disponibles."""
    json_files = list(Path(".").glob("*advanced_rag*.json"))
    return json_files

def main():
    """Fonction principale."""
    print("📊 Affichage de Résumé Audio")
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
        ("executive", "📊 Résumé Exécutif"),
        ("business", "💼 Résumé Business"),
        ("detailed", "📋 Résumé Détaillé")
    ]
    
    print(f"\n📋 Types de résumés disponibles :")
    for i, (type_id, name) in enumerate(summary_types, 1):
        print(f"   {i}. {name}")
    
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
    
    # Affichage du résumé (sans sauvegarder)
    print(f"\n🔄 Génération du {summary_types[choice - 1][1]}...")
    print("=" * 80)
    
    try:
        # Utiliser le script audio_summarizer sans --output pour afficher seulement
        cmd = [sys.executable, "audio_summarizer.py", str(selected_file), "--type", selected_type]
        
        result = subprocess.run(cmd, capture_output=False, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("\n🎉 Résumé affiché avec succès !")
        else:
            print("❌ Erreur lors de la génération du résumé")
            return 1
    
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n\n👋 Interruption par l'utilisateur. Au revoir !")
        exit(0)
