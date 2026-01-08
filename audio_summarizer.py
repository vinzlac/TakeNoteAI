#!/usr/bin/env python3
"""
Script pour générer des résumés complets de fichiers audio transcrits
"""

import warnings
import torch
import os

# Optimisations M4 pour l'analyse
if torch.backends.mps.is_available():
    torch.set_num_threads(14)
    os.environ['OMP_NUM_THREADS'] = '14'
    os.environ['MKL_NUM_THREADS'] = '14'
    os.environ['NUMEXPR_NUM_THREADS'] = '14'
import json
import argparse
from pathlib import Path
from datetime import datetime
import re

# Import du gestionnaire de sortie
try:
    from output_manager import OutputManager
    OUTPUT_MANAGER = OutputManager()
except ImportError:
    print("⚠️  output_manager.py non trouvé, utilisation des chemins par défaut")
    OUTPUT_MANAGER = None

class AudioSummarizer:
    """Générateur de résumés pour les transcriptions audio."""
    
    def __init__(self, json_file: str):
        """Initialise le résumeur avec un fichier JSON."""
        self.json_file = Path(json_file)
        if not self.json_file.exists():
            raise FileNotFoundError(f"Le fichier {json_file} n'existe pas")
        
        with open(self.json_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        self.full_text = self.data["transcription"]["text"]
        self.segments = self.data["transcription"].get("segments", [])
        self.metadata = self.data.get("metadata", {})
        
        print(f"✅ Fichier chargé: {len(self.full_text)} caractères, {len(self.segments)} segments")
    
    def extract_key_information(self):
        """Extrait les informations clés de l'audio."""
        info = {
            "duration": self._calculate_duration(),
            "speaker_role": self._identify_speaker_role(),
            "project_scope": self._extract_project_scope(),
            "team_size": self._extract_team_info(),
            "main_topics": self._extract_main_topics(),
            "timeline": self._extract_timeline(),
            "risks": self._extract_risks(),
            "actions": self._extract_actions(),
            "decisions": self._extract_decisions()
        }
        return info
    
    def _calculate_duration(self):
        """Calcule la durée totale de l'audio."""
        if self.segments:
            last_segment = max(self.segments, key=lambda x: x.get("end", 0))
            return round(last_segment.get("end", 0), 1)
        return 0
    
    def _identify_speaker_role(self):
        """Identifie le rôle du locuteur principal."""
        text_lower = self.full_text.lower()
        
        if "responsable" in text_lower and "développer" in text_lower:
            return "Responsable de développement"
        elif "gérer" in text_lower and "applications" in text_lower:
            return "Manager de projet"
        elif "architecture" in text_lower:
            return "Architecte technique"
        else:
            return "Participant à la réunion"
    
    def _extract_project_scope(self):
        """Extrait la portée du projet."""
        scope_info = {}
        
        for segment in self.segments:
            text = segment.get("text", "")
            
            if "150 applications" in text:
                scope_info["applications_count"] = 150
            if "70 personnes" in text:
                scope_info["team_size"] = 70
            if "go-live" in text.lower():
                scope_info["has_go_live"] = True
            if "architecture" in text.lower():
                scope_info["involves_architecture"] = True
        
        return scope_info
    
    def _extract_team_info(self):
        """Extrait les informations sur l'équipe."""
        team_info = {}
        
        for segment in self.segments:
            text = segment.get("text", "")
            text_lower = text.lower()
            
            if "développeurs" in text_lower:
                team_info["has_developers"] = True
            if "architectes" in text_lower:
                team_info["has_architects"] = True
            if "services de projets" in text_lower:
                team_info["has_project_services"] = True
            if "70 personnes" in text:
                team_info["total_team_size"] = 70
        
        return team_info
    
    def _extract_main_topics(self):
        """Extrait les sujets principaux discutés."""
        topics = []
        
        # Sujets identifiés par mots-clés
        topic_keywords = {
            "Architecture": ["architecture", "design", "structure"],
            "Code Review": ["code review", "review", "validation"],
            "Standards": ["standards", "conformité", "respecter"],
            "Go-live": ["go-live", "production", "déploiement"],
            "Maintenance": ["maintenance", "support", "entretien"],
            "Développement": ["développer", "développement", "applications"],
            "Équipe": ["équipe", "personnes", "responsable"]
        }
        
        for topic, keywords in topic_keywords.items():
            for segment in self.segments:
                text_lower = segment.get("text", "").lower()
                if any(keyword in text_lower for keyword in keywords):
                    if topic not in topics:
                        topics.append(topic)
                    break
        
        return topics
    
    def _extract_timeline(self):
        """Extrait les informations temporelles."""
        timeline = []
        
        for segment in self.segments:
            text = segment.get("text", "")
            text_lower = text.lower()
            timestamp = segment.get("start", 0)
            
            if "go-live" in text_lower:
                timeline.append({
                    "event": "Go-live mentionné",
                    "description": text.strip(),
                    "timestamp": f"{timestamp:.1f}s"
                })
            elif "maintenant" in text_lower:
                timeline.append({
                    "event": "Situation actuelle",
                    "description": text.strip(),
                    "timestamp": f"{timestamp:.1f}s"
                })
            elif "après" in text_lower and "go-live" in text_lower:
                timeline.append({
                    "event": "Post go-live",
                    "description": text.strip(),
                    "timestamp": f"{timestamp:.1f}s"
                })
        
        return timeline
    
    def _extract_risks(self):
        """Extrait les risques identifiés."""
        risks = []
        
        for segment in self.segments:
            text = segment.get("text", "")
            text_lower = text.lower()
            
            if any(word in text_lower for word in ["changement", "modification"]):
                risks.append({
                    "type": "Risque de changement",
                    "description": text.strip(),
                    "severity": "Moyen"
                })
            elif any(word in text_lower for word in ["standard", "conformité"]):
                risks.append({
                    "type": "Risque de non-conformité",
                    "description": text.strip(),
                    "severity": "Élevé"
                })
            elif "go-live" in text_lower:
                risks.append({
                    "type": "Risque de déploiement",
                    "description": text.strip(),
                    "severity": "Élevé"
                })
        
        return risks
    
    def _extract_actions(self):
        """Extrait les actions identifiées."""
        actions = []
        
        for segment in self.segments:
            text = segment.get("text", "")
            text_lower = text.lower()
            
            if any(word in text_lower for word in ["développer", "créer", "faire"]):
                actions.append({
                    "type": "Développement",
                    "description": text.strip(),
                    "priority": "Haute"
                })
            elif any(word in text_lower for word in ["valider", "review", "vérifier"]):
                actions.append({
                    "type": "Validation",
                    "description": text.strip(),
                    "priority": "Critique"
                })
        
        return actions
    
    def _extract_decisions(self):
        """Extrait les décisions prises."""
        decisions = []
        
        for segment in self.segments:
            text = segment.get("text", "")
            text_lower = text.lower()
            
            # Mots-clés indiquant une décision
            decision_indicators = ["doit passer", "nécessaire", "important", "critique"]
            
            if any(indicator in text_lower for indicator in decision_indicators):
                decisions.append({
                    "description": text.strip(),
                    "type": "Décision technique"
                })
        
        return decisions
    
    def generate_executive_summary(self):
        """Génère un résumé exécutif."""
        info = self.extract_key_information()
        
        summary = f"""# 📊 RÉSUMÉ EXÉCUTIF - {self.metadata.get('filename', 'Audio')}

## 🎯 Contexte général
- **Durée** : {info['duration']} secondes
- **Rôle du locuteur** : {info['speaker_role']}
- **Sujets principaux** : {', '.join(info['main_topics'])}

## 📈 Portée du projet
"""
        
        if info['project_scope']:
            if 'applications_count' in info['project_scope']:
                summary += f"- **Applications** : {info['project_scope']['applications_count']}\n"
            if 'team_size' in info['project_scope']:
                summary += f"- **Équipe** : {info['project_scope']['team_size']} personnes\n"
            if info['project_scope'].get('has_go_live'):
                summary += "- **Go-live prévu** : Oui\n"
        
        summary += f"""
## ⚠️ Risques identifiés ({len(info['risks'])})
"""
        
        for i, risk in enumerate(info['risks'][:5], 1):
            summary += f"{i}. **{risk['type']}** - {risk['severity']}\n"
            summary += f"   *{risk['description'][:80]}...*\n\n"
        
        summary += f"""
## 🎯 Actions prioritaires ({len(info['actions'])})
"""
        
        for i, action in enumerate(info['actions'][:5], 1):
            summary += f"{i}. **{action['type']}** - {action['priority']}\n"
            summary += f"   *{action['description'][:80]}...*\n\n"
        
        summary += f"""
## 📅 Échéances clés
"""
        
        for event in info['timeline'][:3]:
            summary += f"- **{event['event']}** : {event['timestamp']}\n"
            summary += f"  *{event['description'][:60]}...*\n\n"
        
        summary += f"""
## 🏆 Points clés à retenir
1. **Projet d'envergure** : Gestion de {info['project_scope'].get('applications_count', 'plusieurs')} applications
2. **Équipe importante** : {info['project_scope'].get('team_size', 'plusieurs')} personnes impliquées
3. **Go-live critique** : Point focal de toutes les activités
4. **Standards à respecter** : Conformité et validation essentielles
5. **Architecture stabilisée** : Phase de finalisation en cours
"""
        
        return summary
    
    def generate_detailed_summary(self):
        """Génère un résumé détaillé."""
        info = self.extract_key_information()
        
        summary = f"""# 📋 RÉSUMÉ DÉTAILLÉ - {self.metadata.get('filename', 'Audio')}

## 📊 Métadonnées
- **Fichier** : {self.metadata.get('filename', 'Non spécifié')}
- **Durée** : {info['duration']} secondes
- **Méthode de transcription** : {self.metadata.get('transcription_method', 'Non spécifiée')}
- **Langue** : {self.metadata.get('language', 'Non spécifiée')}
- **Date de traitement** : {self.metadata.get('timestamp', 'Non spécifiée')}

## 👤 Profil du locuteur
- **Rôle** : {info['speaker_role']}
- **Responsabilités** : Gestion d'équipe et de projets de développement

## 🎯 Sujets abordés
"""
        
        for i, topic in enumerate(info['main_topics'], 1):
            summary += f"{i}. **{topic}**\n"
        
        summary += f"""

## 📈 Portée et contexte du projet
"""
        
        if info['project_scope']:
            summary += "### Détails du projet :\n"
            for key, value in info['project_scope'].items():
                summary += f"- **{key.replace('_', ' ').title()}** : {value}\n"
        
        summary += f"""

### Composition de l'équipe :
"""
        
        if info['team_size']:
            for key, value in info['team_size'].items():
                summary += f"- **{key.replace('_', ' ').title()}** : {value}\n"
        
        summary += f"""

## ⚠️ Analyse des risques
**Total identifié** : {len(info['risks'])} risques

"""
        
        for i, risk in enumerate(info['risks'], 1):
            summary += f"### {i}. {risk['type']} (Sévérité: {risk['severity']})\n"
            summary += f"**Description** : {risk['description']}\n\n"
        
        summary += f"""
## 🎯 Actions et responsabilités
**Total identifié** : {len(info['actions'])} actions

"""
        
        for i, action in enumerate(info['actions'], 1):
            summary += f"### {i}. {action['type']} (Priorité: {action['priority']})\n"
            summary += f"**Description** : {action['description']}\n\n"
        
        summary += f"""
## 📅 Chronologie des événements
"""
        
        for i, event in enumerate(info['timeline'], 1):
            summary += f"### {i}. {event['event']} ({event['timestamp']})\n"
            summary += f"**Description** : {event['description']}\n\n"
        
        summary += f"""
## 🏆 Décisions importantes
**Total identifié** : {len(info['decisions'])} décisions

"""
        
        for i, decision in enumerate(info['decisions'], 1):
            summary += f"### {i}. {decision['type']}\n"
            summary += f"**Description** : {decision['description']}\n\n"
        
        summary += f"""
## 📝 Transcription complète
*Durée totale : {info['duration']} secondes*

```
{self.full_text}
```

## 🔍 Segments détaillés
"""
        
        for i, segment in enumerate(self.segments[:10], 1):  # Limiter à 10 segments
            start = segment.get('start', 0)
            end = segment.get('end', 0)
            text = segment.get('text', '').strip()
            summary += f"{i:2d}. [{start:6.1f}s - {end:6.1f}s] {text}\n"
        
        if len(self.segments) > 10:
            summary += f"\n... et {len(self.segments) - 10} segments supplémentaires\n"
        
        summary += f"""

---
*Résumé généré automatiquement le {datetime.now().strftime('%d/%m/%Y à %H:%M')}*
"""
        
        return summary
    
    def generate_business_summary(self):
        """Génère un résumé orienté business."""
        info = self.extract_key_information()
        
        summary = f"""# 💼 RÉSUMÉ BUSINESS - {self.metadata.get('filename', 'Audio')}

## 🎯 Vue d'ensemble
Cette réunion porte sur un **projet de grande envergure** impliquant :
- {info['project_scope'].get('applications_count', 'Plusieurs')} applications
- {info['project_scope'].get('team_size', 'Une équipe importante')} de personnes
- Un **go-live critique** à venir

## 💰 Impact business
- **Scope** : Projet majeur touchant de nombreux systèmes
- **Ressources** : Équipe importante mobilisée
- **Timeline** : Go-live imminent avec pression temporelle
- **Risques** : Enjeux élevés de conformité et de déploiement

## ⚡ Actions prioritaires
"""
        
        high_priority_actions = [a for a in info['actions'] if a['priority'] in ['Haute', 'Critique']]
        
        for i, action in enumerate(high_priority_actions[:5], 1):
            summary += f"{i}. **{action['type']}** - {action['description'][:60]}...\n"
        
        summary += f"""

## 🚨 Risques critiques
"""
        
        high_risk = [r for r in info['risks'] if r['severity'] == 'Élevé']
        
        for i, risk in enumerate(high_risk[:5], 1):
            summary += f"{i}. **{risk['type']}** - {risk['description'][:60]}...\n"
        
        summary += f"""

## 📊 Métriques clés
- **Durée de la réunion** : {info['duration']} secondes
- **Sujets abordés** : {len(info['main_topics'])}
- **Risques identifiés** : {len(info['risks'])}
- **Actions définies** : {len(info['actions'])}
- **Décisions prises** : {len(info['decisions'])}

## 🎯 Recommandations
1. **Suivi rapproché** du go-live
2. **Validation stricte** des standards
3. **Coordination renforcée** entre les équipes
4. **Monitoring** des risques de changement
5. **Communication** sur les échéances

---
*Analyse business générée le {datetime.now().strftime('%d/%m/%Y à %H:%M')}*
"""
        
        return summary


def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(
        description="Générateur de résumés pour les transcriptions audio",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  %(prog)s fichier.json --type executive
  %(prog)s fichier.json --type detailed --output resume_detaille.md
  %(prog)s fichier.json --type business --output analyse_business.md
  %(prog)s fichier.json --type all --output dossier_resumes/
        """
    )
    
    parser.add_argument("json_file", help="Fichier JSON de transcription")
    parser.add_argument("--type", "-t", 
                       choices=["executive", "detailed", "business", "all"],
                       default="executive",
                       help="Type de résumé à générer")
    parser.add_argument("--output", "-o", help="Fichier ou dossier de sortie")
    
    args = parser.parse_args()
    
    try:
        # Initialiser le résumeur
        summarizer = AudioSummarizer(args.json_file)
        
        # Générer le(s) résumé(s)
        if args.type == "executive":
            summary = summarizer.generate_executive_summary()
            if args.output:
                output_file = args.output
            else:
                # Générer dans output/reports/action.md au lieu de summaries/
                filename = "action.md"
                reports_dir = Path("output/reports")
                reports_dir.mkdir(parents=True, exist_ok=True)
                output_file = str(reports_dir / filename)
        elif args.type == "detailed":
            summary = summarizer.generate_detailed_summary()
            if args.output:
                output_file = args.output
            else:
                filename = "resume_detaille.md"
                if OUTPUT_MANAGER:
                    output_file = str(OUTPUT_MANAGER.get_summary_path(filename))
                else:
                    output_file = filename
        elif args.type == "business":
            summary = summarizer.generate_business_summary()
            if args.output:
                output_file = args.output
            else:
                filename = "resume_business.md"
                if OUTPUT_MANAGER:
                    output_file = str(OUTPUT_MANAGER.get_summary_path(filename))
                else:
                    output_file = filename
        elif args.type == "all":
            # Générer tous les types
            if args.output:
                output_dir = Path(args.output)
            else:
                output_dir = OUTPUT_MANAGER.base_output_dir / "summaries" if OUTPUT_MANAGER else Path("resumes")
            output_dir.mkdir(exist_ok=True)
            
            summaries = {
                "executive": summarizer.generate_executive_summary(),
                "detailed": summarizer.generate_detailed_summary(),
                "business": summarizer.generate_business_summary()
            }
            
            for summary_type, content in summaries.items():
                output_file = output_dir / f"resume_{summary_type}.md"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Résumé {summary_type} sauvegardé : {output_file}")
                
                # Afficher aussi dans la sortie standard
                print("\n" + "="*80)
                print(f"📊 RÉSUMÉ {summary_type.upper()} - AFFICHAGE")
                print("="*80)
                print(content)
            
            print(f"\n🎉 Tous les résumés générés dans : {output_dir}")
            return 0
        
        # Sauvegarder ou afficher
        if args.output or args.type != "all":
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(summary)
            print(f"✅ Résumé {args.type} sauvegardé : {output_file}")
            
            # Afficher aussi dans la sortie standard
            print("\n" + "="*80)
            print(f"📊 RÉSUMÉ {args.type.upper()} - AFFICHAGE")
            print("="*80)
            print(summary)
        else:
            print(summary)
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
