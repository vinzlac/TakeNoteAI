#!/usr/bin/env python3
"""
Script interactif pour préparer un nouveau RAG
Nettoie les données et guide l'utilisateur
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Exécute une commande et affiche le résultat."""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} terminé")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ Erreur lors de {description}")
            if result.stderr:
                print(result.stderr)
            return False
        return True
    except Exception as e:
        print(f"❌ Exception lors de {description}: {e}")
        return False

def main():
    """Fonction principale."""
    print("🚀 Préparation d'un nouveau RAG")
    print("=" * 50)
    
    # 1. Vérifier l'état actuel
    print("\n📊 1. Vérification de l'état actuel...")
    if not run_command("python clean_rag_data.py --status", "Vérification de l'état"):
        print("❌ Impossible de vérifier l'état")
        return 1
    
    # 2. Demander confirmation pour le nettoyage
    print("\n🧹 2. Nettoyage des données existantes")
    response = input("❓ Voulez-vous nettoyer les données existantes ? (oui/non): ")
    
    if response.lower() in ["oui", "o", "yes", "y"]:
        print("\n⚠️  ATTENTION: Cela va supprimer:")
        print("   - ChromaDB (base de données vectorielle)")
        print("   - Fichiers JSON de transcription")
        print("   - Fichiers de résumé")
        print("   - Fichiers de mots-clés générés")
        
        confirm = input("\n❓ Confirmez-vous le nettoyage ? (oui/non): ")
        if confirm.lower() in ["oui", "o", "yes", "y"]:
            if not run_command("python clean_rag_data.py --all --force", "Nettoyage complet"):
                print("❌ Erreur lors du nettoyage")
                return 1
            print("✅ Données nettoyées avec succès")
        else:
            print("❌ Nettoyage annulé")
            return 1
    else:
        print("⏭️  Nettoyage ignoré")
    
    # 3. Vérifier l'état après nettoyage
    print("\n📊 3. Vérification après nettoyage...")
    run_command("python clean_rag_data.py --status", "Vérification après nettoyage")
    
    # 4. Proposer les options suivantes
    print("\n🎯 4. Options suivantes:")
    print("   a) Lancer une nouvelle transcription RAG")
    print("   b) Générer des mots-clés à partir d'un fichier existant")
    print("   c) Utiliser des mots-clés personnalisés")
    print("   d) Quitter")
    
    choice = input("\n❓ Que voulez-vous faire ? (a/b/c/d): ").lower()
    
    if choice == "a":
        print("\n🎤 Lancement d'une nouvelle transcription RAG...")
        audio_file = input("📁 Nom du fichier audio (ex: audio.mp3): ")
        if not Path(audio_file).exists():
            print(f"❌ Fichier {audio_file} introuvable")
            return 1
        
        keywords_file = input("📝 Fichier de mots-clés (optionnel, ex: keywords.txt): ")
        if keywords_file and Path(keywords_file).exists():
            cmd = f"python advanced_rag_transcription_with_keywords.py {audio_file} --keywords-file {keywords_file}"
        else:
            keywords = input("🔤 Mots-clés personnalisés (optionnel, séparés par des virgules): ")
            if keywords:
                cmd = f"python advanced_rag_transcription_with_keywords.py {audio_file} --keywords \"{keywords}\""
            else:
                cmd = f"python advanced_rag_transcription.py {audio_file}"
        
        print(f"\n🚀 Commande à exécuter: {cmd}")
        confirm = input("❓ Exécuter maintenant ? (oui/non): ")
        if confirm.lower() in ["oui", "o", "yes", "y"]:
            run_command(cmd, "Transcription RAG")
        else:
            print("💡 Vous pouvez exécuter la commande plus tard")
    
    elif choice == "b":
        print("\n🔍 Génération de mots-clés...")
        json_file = input("📁 Nom du fichier JSON de transcription: ")
        if not Path(json_file).exists():
            print(f"❌ Fichier {json_file} introuvable")
            return 1
        
        top_n = input("🔢 Nombre de mots-clés à extraire (défaut: 25): ") or "25"
        cmd = f"python generate_keywords_from_transcription.py {json_file} --top {top_n}"
        
        print(f"\n🚀 Commande à exécuter: {cmd}")
        confirm = input("❓ Exécuter maintenant ? (oui/non): ")
        if confirm.lower() in ["oui", "o", "yes", "y"]:
            run_command(cmd, "Génération de mots-clés")
        else:
            print("💡 Vous pouvez exécuter la commande plus tard")
    
    elif choice == "c":
        print("\n🔤 Utilisation de mots-clés personnalisés...")
        audio_file = input("📁 Nom du fichier audio (ex: audio.mp3): ")
        if not Path(audio_file).exists():
            print(f"❌ Fichier {audio_file} introuvable")
            return 1
        
        keywords = input("🔤 Mots-clés (séparés par des virgules, ex: Azure, Microsoft): ")
        if not keywords:
            print("❌ Aucun mot-clé fourni")
            return 1
        
        cmd = f"python advanced_rag_transcription_with_keywords.py {audio_file} --keywords \"{keywords}\""
        print(f"\n🚀 Commande à exécuter: {cmd}")
        confirm = input("❓ Exécuter maintenant ? (oui/non): ")
        if confirm.lower() in ["oui", "o", "yes", "y"]:
            run_command(cmd, "Transcription RAG avec mots-clés personnalisés")
        else:
            print("💡 Vous pouvez exécuter la commande plus tard")
    
    elif choice == "d":
        print("👋 Au revoir !")
        return 0
    
    else:
        print("❌ Choix invalide")
        return 1
    
    # 5. Proposer les analyses
    print("\n📊 5. Analyses disponibles après transcription:")
    print("   - ask_audio.py : Poser des questions sur l'audio")
    print("   - show_summary.py : Afficher des résumés")
    print("   - start_analysis.py : Menu interactif d'analyse")
    
    print("\n🎉 Préparation terminée !")
    print("💡 Vous pouvez maintenant utiliser les scripts d'analyse")
    
    return 0

if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n⏹️  Préparation interrompue par l'utilisateur")
        exit(1)
    except Exception as e:
        print(f"❌ Erreur: {e}")
        exit(1)
