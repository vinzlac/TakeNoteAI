#!/usr/bin/env python3
"""
Script pour extraire et analyser les mots-clés du JSON de sortie
"""

import json
import sys
from pathlib import Path

def extract_keywords_from_json(json_file):
    """Extrait et analyse les mots-clés du JSON."""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extraire les mots-clés
    keywords = data.get('business_keywords', [])
    metadata = data.get('metadata', {})
    
    return keywords, metadata

def main():
    if len(sys.argv) != 2:
        print("Usage: python extract_keywords_from_json.py <fichier.json>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    
    if not Path(json_file).exists():
        print(f"❌ Fichier {json_file} non trouvé")
        sys.exit(1)
    
    try:
        keywords, metadata = extract_keywords_from_json(json_file)
        
        print("🔑 Mots-clés métiers extraits:")
        print("=" * 50)
        
        if not keywords:
            print("❌ Aucun mot-clé trouvé")
            return
        
        # Afficher les mots-clés par score
        for i, (keyword, score) in enumerate(keywords, 1):
            print(f"{i:2d}. {keyword:<30} (score: {score:.3f})")
        
        print("=" * 50)
        print(f"📊 Statistiques:")
        print(f"   - Nombre de mots-clés: {len(keywords)}")
        print(f"   - Fichier source: {metadata.get('filename', 'N/A')}")
        print(f"   - Durée: {metadata.get('duration', 0):.1f} secondes")
        print(f"   - Langue: {metadata.get('language', 'N/A')}")
        
        # Sauvegarder en CSV
        output_file = Path(json_file).stem + "_mots_cles.csv"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("Mots-clés,Score\n")
            for keyword, score in keywords:
                f.write(f'"{keyword}",{score:.3f}\n')
        
        print(f"✅ Mots-clés sauvegardés: {output_file}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
