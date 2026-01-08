#!/usr/bin/env python3
"""
Script pour générer un résumé (compte rendu des risques et actions) 
à partir d'un fichier de transcription texte (.txt)
"""

import argparse
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# Import du gestionnaire de sortie
try:
    from output_manager import OutputManager
    OUTPUT_MANAGER = OutputManager()
except ImportError:
    print("⚠️  output_manager.py non trouvé, utilisation des chemins par défaut")
    OUTPUT_MANAGER = None


def parse_transcript_file(transcript_file: Path) -> Dict:
    """
    Parse un fichier de transcription texte et extrait les informations.
    
    Args:
        transcript_file: Chemin vers le fichier de transcription .txt
    
    Returns:
        Dict avec 'text', 'segments', 'metadata'
    """
    with open(transcript_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extraire les métadonnées du header
    metadata = {}
    lines = content.split('\n')
    
    # Parser le header (lignes commençant par #)
    header_lines = []
    text_lines = []
    in_header = True
    
    for line in lines:
        if line.startswith('#'):
            header_lines.append(line)
            # Extraire la durée
            if 'Durée:' in line:
                duration_match = re.search(r'Durée:\s*(\d{2}):(\d{2}):(\d{2})', line)
                if duration_match:
                    hours, minutes, secs = map(int, duration_match.groups())
                    metadata['duration'] = hours * 3600 + minutes * 60 + secs
            # Extraire le nom du fichier
            if 'Transcription:' in line:
                filename_match = re.search(r'Transcription:\s*(.+)', line)
                if filename_match:
                    metadata['filename'] = filename_match.group(1).strip()
        elif line.startswith('='):
            in_header = False
            continue
        elif not in_header and line.strip():
            text_lines.append(line)
    
    # Extraire le texte complet (sans les timestamps)
    full_text = ""
    segments = []
    max_timestamp = 0
    
    for line in text_lines:
        # Format: [HH:MM:SS] [Personne:] Texte
        timestamp_match = re.match(r'\[(\d{2}):(\d{2}):(\d{2})\]\s*(?:(\w+):\s*)?(.+)', line)
        if timestamp_match:
            hours, minutes, secs = map(int, timestamp_match.groups()[:3])
            timestamp_seconds = hours * 3600 + minutes * 60 + secs
            speaker = timestamp_match.group(4) if timestamp_match.group(4) else None
            text = timestamp_match.group(5).strip()
            
            # Mettre à jour le timestamp maximum
            max_timestamp = max(max_timestamp, timestamp_seconds)
            
            full_text += text + " "
            segments.append({
                'start': timestamp_seconds,
                'end': timestamp_seconds + 5,  # Estimation
                'text': text,
                'speaker': speaker
            })
        else:
            # Ligne sans timestamp, ajouter au texte
            if line.strip():
                full_text += line.strip() + " "
    
    # Si la durée n'a pas été trouvée dans le header, la calculer depuis le dernier segment
    if metadata.get('duration', 0) == 0 and max_timestamp > 0:
        metadata['duration'] = max_timestamp
    
    return {
        'text': full_text.strip(),
        'segments': segments,
        'metadata': metadata
    }


def extract_risks(text: str, segments: List[Dict]) -> List[Dict]:
    """Extrait les risques identifiés dans le texte."""
    risks = []
    
    # Mots-clés indiquant des risques
    risk_keywords = [
        'risque', 'problème', 'difficulté', 'challenge', 'défi',
        'danger', 'menace', 'alerte', 'attention', 'précaution',
        'bloqué', 'retard', 'échec', 'erreur', 'bug'
    ]
    
    text_lower = text.lower()
    
    for segment in segments:
        seg_text = segment.get('text', '').lower()
        if any(keyword in seg_text for keyword in risk_keywords):
            risks.append({
                'type': 'Risque identifié',
                'description': segment.get('text', '').strip(),
                'severity': 'Moyen',
                'timestamp': segment.get('start', 0)
            })
    
    return risks[:10]  # Limiter à 10 risques


def extract_actions(text: str, segments: List[Dict]) -> List[Dict]:
    """Extrait les actions à prendre dans le texte."""
    actions = []
    
    # Mots-clés indiquant des actions
    action_keywords = [
        'faire', 'développer', 'créer', 'mettre en place', 'implémenter',
        'valider', 'vérifier', 'corriger', 'améliorer', 'optimiser',
        'déployer', 'migrer', 'refactoriser', 'tester', 'documenter',
        'doit', 'faut', 'nécessaire', 'important', 'prioritaire'
    ]
    
    text_lower = text.lower()
    
    for segment in segments:
        seg_text = segment.get('text', '').lower()
        if any(keyword in seg_text for keyword in action_keywords):
            # Déterminer la priorité
            priority = 'Moyenne'
            if any(word in seg_text for word in ['urgent', 'critique', 'prioritaire', 'important']):
                priority = 'Haute'
            elif any(word in seg_text for word in ['peut', 'optionnel', 'si possible']):
                priority = 'Basse'
            
            actions.append({
                'type': 'Action',
                'description': segment.get('text', '').strip(),
                'priority': priority,
                'timestamp': segment.get('start', 0)
            })
    
    return actions[:30]  # Limiter à 30 actions


def generate_action_report(transcript_data: Dict) -> str:
    """
    Génère un compte rendu des risques et actions à partir des données de transcription.
    
    Args:
        transcript_data: Dict avec 'text', 'segments', 'metadata'
    
    Returns:
        Contenu du rapport en Markdown
    """
    text = transcript_data['text']
    segments = transcript_data['segments']
    metadata = transcript_data['metadata']
    
    filename = metadata.get('filename', 'Transcription')
    duration = metadata.get('duration', 0)
    
    # Extraire les informations
    risks = extract_risks(text, segments)
    actions = extract_actions(text, segments)
    
    # Calculer la durée formatée
    hours = duration // 3600
    minutes = (duration % 3600) // 60
    seconds = duration % 60
    duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    # Générer le rapport
    report = f"""# 📋 COMPTE RENDU - {filename}

## 🎯 Contexte général
- **Durée** : {duration_str} ({duration} secondes)
- **Segments** : {len(segments)} segments transcrits
- **Date de génération** : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## ⚠️ Risques identifiés ({len(risks)})

"""
    
    if risks:
        for i, risk in enumerate(risks, 1):
            timestamp_str = f"{int(risk['timestamp'])//3600:02d}:{(int(risk['timestamp'])%3600)//60:02d}:{int(risk['timestamp'])%60:02d}"
            report += f"{i}. **{risk['type']}** - {risk['severity']} (à {timestamp_str})\n"
            report += f"   *{risk['description'][:150]}...*\n\n"
    else:
        report += "Aucun risque spécifique identifié dans la transcription.\n\n"
    
    report += f"""
## 🎯 Actions à prendre ({len(actions)})

"""
    
    if actions:
        # Trier par priorité
        actions_sorted = sorted(actions, key=lambda x: {'Haute': 0, 'Moyenne': 1, 'Basse': 2}.get(x['priority'], 3))
        
        for i, action in enumerate(actions_sorted, 1):
            timestamp_str = f"{int(action['timestamp'])//3600:02d}:{(int(action['timestamp'])%3600)//60:02d}:{int(action['timestamp'])%60:02d}"
            report += f"{i}. **{action['type']}** - Priorité: {action['priority']} (à {timestamp_str})\n"
            report += f"   *{action['description'][:150]}...*\n\n"
    else:
        report += "Aucune action spécifique identifiée dans la transcription.\n\n"
    
    report += f"""
## 📊 Statistiques
- **Durée totale** : {duration_str}
- **Nombre de segments** : {len(segments)}
- **Risques identifiés** : {len(risks)}
- **Actions identifiées** : {len(actions)}

---
*Rapport généré automatiquement le {datetime.now().strftime('%d/%m/%Y à %H:%M')}*
"""
    
    return report


def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(
        description="Génère un compte rendu (risques et actions) depuis un fichier de transcription texte",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  %(prog)s output/readable_transcripts/transcript.txt
  %(prog)s output/readable_transcripts/transcript.txt -o custom_report.md
        """
    )
    
    parser.add_argument("transcript_file", help="Fichier de transcription texte (.txt)")
    parser.add_argument("-o", "--output", help="Fichier de sortie (optionnel, défaut: output/reports/action.md)")
    
    args = parser.parse_args()
    
    try:
        transcript_path = Path(args.transcript_file)
        
        if not transcript_path.exists():
            print(f"❌ Le fichier {transcript_path} n'existe pas")
            return 1
        
        print(f"📄 Lecture de la transcription: {transcript_path.name}")
        
        # Parser le fichier de transcription
        transcript_data = parse_transcript_file(transcript_path)
        
        print(f"✅ Transcription parsée: {len(transcript_data['segments'])} segments")
        
        # Générer le rapport
        print("📝 Génération du compte rendu...")
        report = generate_action_report(transcript_data)
        
        # Déterminer le fichier de sortie
        if args.output:
            output_file = Path(args.output)
        else:
            # Générer dans output/reports/action.md
            reports_dir = Path("output/reports")
            reports_dir.mkdir(parents=True, exist_ok=True)
            output_file = reports_dir / "action.md"
        
        # Sauvegarder
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ Compte rendu généré: {output_file}")
        print(f"📊 Statistiques:")
        print(f"   - Risques identifiés: {len(extract_risks(transcript_data['text'], transcript_data['segments']))}")
        print(f"   - Actions identifiées: {len(extract_actions(transcript_data['text'], transcript_data['segments']))}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
