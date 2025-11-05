#!/usr/bin/env python3
"""
Script pour générer un compte rendu de réunion formaté pour email
en utilisant cursor-agent à partir d'un fichier de transcription.

PRÉREQUIS:
- cursor-agent doit être installé et authentifié
- Pour s'authentifier: cursor-agent login
- Ou utiliser une clé API: export CURSOR_API_KEY=votre_cle_api
"""

import sys
from pathlib import Path
from typing import Optional
import argparse

# Import du module commun
from meeting_report_generator import generate_meeting_report_email


def main():
    parser = argparse.ArgumentParser(
        description="Génère un compte rendu de réunion formaté pour email via cursor-agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  %(prog)s transcription.json
  %(prog)s transcription.json --output compte_rendu.html
  %(prog)s transcription.json --title "Réunion Architecture Azure"
  %(prog)s transcription.txt --output output/meeting_reports/custom/compte_rendu.html

Note: Par défaut, les fichiers sont sauvegardés dans:
  output/meeting_reports/{nom_transcription}/compte_rendu_YYYYMMDD_HHMMSS.html
        """
    )
    
    parser.add_argument(
        'transcription_file',
        type=str,
        help='Fichier de transcription (JSON ou TXT)'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Fichier de sortie (défaut: compte_rendu_YYYYMMDD_HHMMSS.html)'
    )
    
    parser.add_argument(
        '-t', '--title',
        type=str,
        help='Titre de la réunion (pour l\'objet de l\'email)'
    )
    
    parser.add_argument(
        '--cursor-agent-path',
        type=str,
        help='Chemin complet vers cursor-agent (si non dans PATH)'
    )
    
    args = parser.parse_args()
    
    # Vérifier le fichier d'entrée
    transcription_file = Path(args.transcription_file)
    if not transcription_file.exists():
        print(f"❌ Fichier introuvable: {transcription_file}")
        return 1
    
    # Déterminer le fichier de sortie si fourni
    output_file = None
    if args.output:
        output_file = Path(args.output)
    
    # Générer le compte rendu
    result_file = generate_meeting_report_email(
        transcription_file=transcription_file,
        meeting_title=args.title,
        output_file=output_file,
        cursor_agent_path=args.cursor_agent_path
    )
    
    if result_file:
        # Lire le contenu pour les statistiques
        with open(result_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"\n📊 Statistiques:")
        print(f"   - Longueur du compte rendu: {len(content):,} caractères")
        print(f"   - Répertoire: {result_file.parent}")
        print(f"   - Fichier: {result_file.name}")
        print(f"   - Chemin complet: {result_file}")
        return 0
    else:
        print("\n❌ Échec de la génération du compte rendu")
        print("\n💡 Suggestions:")
        print("   1. Vérifiez que cursor-agent est installé et accessible")
        print("   2. Vérifiez la syntaxe de la commande cursor-agent")
        print("   3. Consultez la documentation de cursor-agent")
        return 1


if __name__ == "__main__":
    sys.exit(main())

