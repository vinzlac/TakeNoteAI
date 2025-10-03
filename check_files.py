#!/usr/bin/env python3
"""
Script de vérification des fichiers JSON de transcription
"""

import sys
from pathlib import Path

def check_json_files():
    """Vérifie les fichiers JSON disponibles."""
    print("🔍 Vérification des fichiers de transcription")
    print("=" * 50)
    
    # Chercher les fichiers JSON
    json_files = list(Path(".").glob("*advanced_rag*.json"))
    
    if not json_files:
        print("❌ Aucun fichier JSON de transcription trouvé.")
        print("\n💡 Pour créer un fichier JSON :")
        print("   python advanced_rag_transcription.py votre_audio.mp3")
        return False
    
    print(f"✅ {len(json_files)} fichier(s) JSON trouvé(s) :")
    print()
    
    for i, file in enumerate(json_files, 1):
        print(f"{i:2d}. {file.name}")
        
        # Vérifier la taille du fichier
        size_mb = file.stat().st_size / 1024 / 1024
        print(f"    📁 Taille : {size_mb:.2f} MB")
        
        # Vérifier le contenu basique
        try:
            import json
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Informations de base
            if 'transcription' in data:
                text_length = len(data['transcription'].get('text', ''))
                segments_count = len(data['transcription'].get('segments', []))
                print(f"    📝 Texte : {text_length} caractères")
                print(f"    🎵 Segments : {segments_count}")
            
            if 'metadata' in data:
                metadata = data['metadata']
                print(f"    📅 Date : {metadata.get('timestamp', 'Non spécifiée')}")
                print(f"    🎤 Méthode : {metadata.get('transcription_method', 'Non spécifiée')}")
            
        except Exception as e:
            print(f"    ⚠️  Erreur lecture : {e}")
        
        print()
    
    return True

def show_usage_examples():
    """Affiche des exemples d'utilisation."""
    print("🚀 Exemples d'utilisation avec vos fichiers :")
    print("-" * 50)
    
    json_files = list(Path(".").glob("*advanced_rag*.json"))
    
    if json_files:
        # Prendre le premier fichier comme exemple
        example_file = json_files[0]
        
        print(f"📊 Résumés :")
        print(f"   python audio_summarizer.py {example_file.name} --type executive")
        print(f"   python resume_audio.py")
        
        print(f"\n❓ Questions :")
        print(f"   python simple_audio_analyzer.py {example_file.name} --question \"Quels risques ?\"")
        print(f"   python ask_audio.py")
        
        print(f"\n📺 Affichage :")
        print(f"   python show_summary.py")
        print(f"   python demo_questions.py")

def main():
    """Fonction principale."""
    try:
        # Vérifier les fichiers JSON
        has_files = check_json_files()
        
        if has_files:
            show_usage_examples()
            
            print("\n" + "=" * 50)
            print("🎯 Prêt pour l'analyse !")
            print("💡 Utilisez : python resume_audio.py")
        else:
            print("\n" + "=" * 50)
            print("🔴 Action requise : Traiter un fichier audio")
            print("💡 Commande : python advanced_rag_transcription.py votre_audio.mp3")
        
        return 0
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return 1

if __name__ == "__main__":
    exit(main())
