#!/usr/bin/env python3
"""
Script simplifié pour analyser un fichier JSON de transcription et répondre à des questions
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
import re

class SimpleAudioAnalyzer:
    """Analyseur simplifié pour les transcriptions audio."""
    
    def __init__(self, json_file: str):
        """Initialise l'analyseur avec un fichier JSON."""
        self.json_file = Path(json_file)
        if not self.json_file.exists():
            raise FileNotFoundError(f"Le fichier {json_file} n'existe pas")
        
        with open(self.json_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        # Extraire le texte complet et les segments
        self.full_text = self.data["transcription"]["text"]
        self.segments = self.data["transcription"].get("segments", [])
        
        print(f"✅ Fichier chargé: {len(self.full_text)} caractères, {len(self.segments)} segments")
    
    def find_risks(self):
        """Trouve les risques mentionnés dans l'audio."""
        risk_keywords = [
            "risque", "danger", "problème", "difficulté", "challenge", 
            "attention", "précaution", "vigilance", "alerte",
            "changement", "modification", "impact", "conséquence",
            "standard", "conformité", "respecter", "go-live", "production"
        ]
        
        risks = []
        
        # Analyser chaque segment
        for segment in self.segments:
            text = segment.get("text", "").lower()
            start = segment.get("start", 0)
            end = segment.get("end", 0)
            
            # Vérifier si le segment contient des mots-clés de risque
            found_keywords = [kw for kw in risk_keywords if kw in text]
            
            if found_keywords:
                # Déterminer le type de risque
                risk_type = "Risque général"
                severity = "Moyen"
                
                if any(kw in text for kw in ["changement", "modification"]):
                    risk_type = "Risque de changement"
                    severity = "Moyen"
                elif any(kw in text for kw in ["standard", "conformité", "respecter"]):
                    risk_type = "Risque de non-conformité"
                    severity = "Élevé"
                elif any(kw in text for kw in ["go-live", "production", "déploiement"]):
                    risk_type = "Risque de déploiement"
                    severity = "Élevé"
                elif any(kw in text for kw in ["problème", "difficulté"]):
                    risk_type = "Risque opérationnel"
                    severity = "Élevé"
                
                risks.append({
                    "type": risk_type,
                    "description": segment.get("text", ""),
                    "timestamp": f"{start:.1f}s - {end:.1f}s",
                    "severity": severity,
                    "keywords_found": found_keywords
                })
        
        return risks
    
    def find_actions(self):
        """Trouve les actions mentionnées dans l'audio."""
        action_keywords = [
            "action", "faire", "développer", "créer", "mettre", "implémenter",
            "déployer", "installer", "configurer", "tester", "valider",
            "commencer", "terminer", "finaliser", "livrer", "review", "vérifier"
        ]
        
        actions = []
        
        for segment in self.segments:
            text = segment.get("text", "").lower()
            start = segment.get("start", 0)
            end = segment.get("end", 0)
            
            found_keywords = [kw for kw in action_keywords if kw in text]
            
            if found_keywords:
                action_type = "Action générale"
                priority = "Moyenne"
                
                if any(kw in text for kw in ["développer", "créer", "faire"]):
                    action_type = "Développement"
                    priority = "Haute"
                elif any(kw in text for kw in ["valider", "review", "vérifier"]):
                    action_type = "Validation"
                    priority = "Critique"
                elif any(kw in text for kw in ["tester", "installer", "configurer"]):
                    action_type = "Mise en œuvre"
                    priority = "Haute"
                
                actions.append({
                    "type": action_type,
                    "description": segment.get("text", ""),
                    "timestamp": f"{start:.1f}s - {end:.1f}s",
                    "priority": priority,
                    "keywords_found": found_keywords
                })
        
        return actions
    
    def find_team_info(self):
        """Trouve les informations sur l'équipe."""
        team_info = []
        
        for segment in self.segments:
            text = segment.get("text", "")
            start = segment.get("start", 0)
            end = segment.get("end", 0)
            
            # Rechercher des informations spécifiques sur l'équipe
            if "150 applications" in text:
                team_info.append({
                    "type": "Portée du projet",
                    "description": text,
                    "timestamp": f"{start:.1f}s - {end:.1f}s"
                })
            
            if "70 personnes" in text:
                team_info.append({
                    "type": "Taille de l'équipe",
                    "description": text,
                    "timestamp": f"{start:.1f}s - {end:.1f}s"
                })
            
            if any(word in text.lower() for word in ["développeur", "architecte", "responsable"]):
                team_info.append({
                    "type": "Composition de l'équipe",
                    "description": text,
                    "timestamp": f"{start:.1f}s - {end:.1f}s"
                })
        
        return team_info
    
    def find_timeline(self):
        """Trouve les informations temporelles."""
        timeline = []
        
        for segment in self.segments:
            text = segment.get("text", "").lower()
            start = segment.get("start", 0)
            end = segment.get("end", 0)
            
            if "go-live" in text:
                timeline.append({
                    "type": "Échéance critique",
                    "description": segment.get("text", ""),
                    "timestamp": f"{start:.1f}s - {end:.1f}s",
                    "importance": "Critique"
                })
            
            if any(word in text for word in ["avant", "après", "maintenant", "pendant"]):
                timeline.append({
                    "type": "Information temporelle",
                    "description": segment.get("text", ""),
                    "timestamp": f"{start:.1f}s - {end:.1f}s",
                    "importance": "Moyenne"
                })
        
        return timeline
    
    def answer_question(self, question: str):
        """Répond à une question basée sur le contenu."""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ["risque", "danger", "problème"]):
            return self.find_risks()
        elif any(word in question_lower for word in ["action", "faire", "développer"]):
            return self.find_actions()
        elif any(word in question_lower for word in ["équipe", "personne", "développeur"]):
            return self.find_team_info()
        elif any(word in question_lower for word in ["délai", "date", "timing", "go-live"]):
            return self.find_timeline()
        else:
            # Recherche générale
            return self.general_search(question)
    
    def general_search(self, question: str):
        """Recherche générale basée sur les mots de la question."""
        question_words = [word.lower() for word in question.split() if len(word) > 3]
        results = []
        
        for segment in self.segments:
            text = segment.get("text", "").lower()
            start = segment.get("start", 0)
            end = segment.get("end", 0)
            
            # Compter les mots de la question trouvés dans le segment
            matches = sum(1 for word in question_words if word in text)
            
            if matches > 0:
                results.append({
                    "text": segment.get("text", ""),
                    "timestamp": f"{start:.1f}s - {end:.1f}s",
                    "relevance": matches,
                    "matches": [word for word in question_words if word in text]
                })
        
        # Trier par pertinence
        results.sort(key=lambda x: x["relevance"], reverse=True)
        return results[:5]  # Top 5
    
    def format_answer(self, results, question: str):
        """Formate la réponse pour l'affichage."""
        if not results:
            return f"❌ Aucune information pertinente trouvée pour : '{question}'"
        
        if isinstance(results, list) and len(results) > 0:
            # Vérifier le type de résultat
            if "type" in results[0]:
                return self._format_structured_answer(results, question)
            else:
                return self._format_search_results(results, question)
        
        return "❌ Aucune information trouvée"
    
    def _format_structured_answer(self, results, question: str):
        """Formate une réponse structurée (risques, actions, etc.)."""
        if "risque" in question.lower():
            output = f"🔍 **Réponse à : \"{question}\"**\n\n"
            output += "Voici les **risques identifiés** dans cette discussion :\n\n"
            
            for i, result in enumerate(results, 1):
                output += f"### **{i}. {result['type']}**\n"
                output += f"- **Description** : {result['description']}\n"
                output += f"- **Timestamp** : {result['timestamp']}\n"
                output += f"- **Sévérité** : {result['severity']}\n"
                if 'keywords_found' in result:
                    output += f"- **Mots-clés détectés** : {', '.join(result['keywords_found'])}\n"
                output += "\n"
            
            return output
        
        elif "action" in question.lower():
            output = f"🎯 **Réponse à : \"{question}\"**\n\n"
            output += "Voici les **actions identifiées** dans cette discussion :\n\n"
            
            for i, result in enumerate(results, 1):
                output += f"### **{i}. {result['type']}**\n"
                output += f"- **Description** : {result['description']}\n"
                output += f"- **Timestamp** : {result['timestamp']}\n"
                output += f"- **Priorité** : {result['priority']}\n"
                if 'keywords_found' in result:
                    output += f"- **Mots-clés détectés** : {', '.join(result['keywords_found'])}\n"
                output += "\n"
            
            return output
        
        else:
            output = f"📋 **Réponse à : \"{question}\"**\n\n"
            output += "Voici les **informations pertinentes** trouvées :\n\n"
            
            for i, result in enumerate(results, 1):
                output += f"**{i}.** {result['description']}\n"
                output += f"   *({result['timestamp']})*\n\n"
            
            return output
    
    def _format_search_results(self, results, question: str):
        """Formate les résultats de recherche générale."""
        output = f"🔍 **Réponse à : \"{question}\"**\n\n"
        output += "Voici les **segments les plus pertinents** trouvés :\n\n"
        
        for i, result in enumerate(results, 1):
            output += f"**{i}.** {result['text']}\n"
            output += f"   *({result['timestamp']}) - Pertinence: {result['relevance']}*\n"
            if 'matches' in result:
                output += f"   *Mots correspondants: {', '.join(result['matches'])}*\n"
            output += "\n"
        
        return output


def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(
        description="Analyseur simplifié pour les transcriptions audio",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  %(prog)s transcription.json --question "Quels risques sont identifiés ?"
  %(prog)s transcription.json --question "Quelles actions doivent être prises ?"
  %(prog)s transcription.json --question "Qui fait partie de l'équipe ?"
  %(prog)s transcription.json --question "Quels sont les délais ?"
        """
    )
    
    parser.add_argument("json_file", help="Fichier JSON de transcription")
    parser.add_argument("--question", "-q", required=True, help="Question à poser")
    parser.add_argument("--output", "-o", help="Fichier de sortie (optionnel)")
    
    args = parser.parse_args()
    
    try:
        # Initialiser l'analyseur
        analyzer = SimpleAudioAnalyzer(args.json_file)
        
        # Analyser la question
        results = analyzer.answer_question(args.question)
        
        # Formater la réponse
        formatted_answer = analyzer.format_answer(results, args.question)
        
        # Afficher ou sauvegarder
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(formatted_answer)
            print(f"✅ Réponse sauvegardée dans : {args.output}")
        else:
            print(formatted_answer)
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
