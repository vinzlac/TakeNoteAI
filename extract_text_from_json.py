#!/usr/bin/env python3
"""
Script pour extraire le texte simple du JSON de sortie
"""

import json
import sys
from pathlib import Path

def extract_text_from_json(json_file):
    """Extrait le texte simple du JSON."""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extraire le texte complet
    text = data.get('transcription', {}).get('text', '')
    
    # Nettoyer le texte
    text = text.strip()
    
    return text

def main():
    if len(sys.argv) != 2:
        print("Usage: python extract_text_from_json.py <fichier.json>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    
    if not Path(json_file).exists():
        print(f"❌ Fichier {json_file} non trouvé")
        sys.exit(1)
    
    try:
        text = extract_text_from_json(json_file)
        
        # Afficher le texte
        print("📝 Texte extrait:")
        print("=" * 50)
        print(text)
        print("=" * 50)
        
        # Sauvegarder en fichier texte
        output_file = Path(json_file).stem + "_texte.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"✅ Texte sauvegardé: {output_file}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
