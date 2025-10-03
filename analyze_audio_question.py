#!/usr/bin/env python3
"""
Script pour analyser un fichier JSON de transcription et répondre à des questions
Basé sur l'analyse sémantique du contenu transcrit
"""

import json
import argparse
import re
from typing import Dict, List, Tuple
from pathlib import Path

class AudioQuestionAnalyzer:
    """Analyseur de questions sur les transcriptions audio."""
    
    def __init__(self, json_file: str):
        """
        Initialise l'analyseur avec un fichier JSON de transcription.
        
        Args:
            json_file (str): Chemin vers le fichier JSON de transcription
        """
        self.json_file = Path(json_file)
        if not self.json_file.exists():
            raise FileNotFoundError(f"Le fichier {json_file} n'existe pas")
        
        self.data = self._load_data()
        self.full_text = self.data["transcription"]["text"]
        self.segments = self.data["transcription"].get("segments", [])
        
        # Mots-clés pour différents types de questions
        self.question_keywords = {
            "risques": [
                "risque", "danger", "problème", "difficulté", "challenge", "issue", 
                "attention", "attention", "précaution", "vigilance", "alerte",
                "changement", "modification", "impact", "conséquence", "effet"
            ],
            "actions": [
                "action", "faire", "développer", "créer", "mettre", "implémenter",
                "déployer", "installer", "configurer", "tester", "valider",
                "commencer", "terminer", "finaliser", "livrer", "délivrer"
            ],
            "délais": [
                "délai", "date", "timing", "calendrier", "planning", "échéance",
                "avant", "après", "jusqu'à", "pendant", "durant", "maintenant",
                "go-live", "mise en production", "lancement", "déploiement"
            ],
            "équipe": [
                "équipe", "personne", "développeur", "architecte", "responsable",
                "gérer", "diriger", "coordonner", "collaborer", "travailler",
                "membre", "participant", "intervenant", "acteur"
            ],
            "architecture": [
                "architecture", "structure", "design", "modèle", "framework",
                "système", "application", "plateforme", "infrastructure",
                "code review", "validation", "standards", "conformité"
            ],
            "problèmes": [
                "problème", "erreur", "bug", "défaut", "anomalie", "incident",
                "panne", "dysfonctionnement", "échec", "raté", "échoué",
                "question", "interrogation", "doute", "incertitude"
            ]
        }
    
    def _load_data(self) -> Dict:
        """Charge les données JSON."""
        with open(self.json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _extract_segments_with_keywords(self, keywords: List[str]) -> List[Dict]:
        """
        Extrait les segments contenant des mots-clés spécifiques.
        
        Args:
            keywords (List[str]): Mots-clés à rechercher
            
        Returns:
            List[Dict]: Segments contenant les mots-clés
        """
        relevant_segments = []
        
        for segment in self.segments:
            text = segment.get("text", "").lower()
            
            # Vérifier si le segment contient des mots-clés
            for keyword in keywords:
                if keyword.lower() in text:
                    relevant_segments.append({
                        "text": segment.get("text", ""),
                        "start": segment.get("start", 0),
                        "end": segment.get("end", 0),
                        "keyword_found": keyword,
                        "relevance_score": self._calculate_relevance(text, keywords)
                    })
                    break
        
        # Trier par score de pertinence
        relevant_segments.sort(key=lambda x: x["relevance_score"], reverse=True)
        return relevant_segments
    
    def _calculate_relevance(self, text: str, keywords: List[str]) -> float:
        """
        Calcule un score de pertinence basé sur les mots-clés.
        
        Args:
            text (str): Texte à analyser
            keywords (List[str]): Mots-clés recherchés
            
        Returns:
            float: Score de pertinence
        """
        text_lower = text.lower()
        score = 0
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            # Score basé sur la fréquence et la position du mot-clé
            count = text_lower.count(keyword_lower)
            if count > 0:
                score += count * 0.5
                # Bonus si le mot-clé est en début de phrase
                if text_lower.startswith(keyword_lower):
                    score += 1.0
        
        return score
    
    def _analyze_risks(self) -> List[Dict]:
        """Analyse les risques mentionnés dans l'audio."""
        risk_segments = self._extract_segments_with_keywords(
            self.question_keywords["risques"]
        )
        
        risks = []
        for segment in risk_segments:
            text = segment.get("text", "")
            
            # Détecter différents types de risques
            if any(word in text.lower() for word in ["changement", "modification"]):
                risks.append({
                    "type": "Risque de changement",
                    "description": text,
                    "timestamp": f"{segment.get('start', 0):.1f}s - {segment.get('end', 0):.1f}s",
                    "severity": "Moyen"
                })
            
            if any(word in text.lower() for word in ["standard", "conformité", "respecter"]):
                risks.append({
                    "type": "Risque de non-conformité",
                    "description": text,
                    "timestamp": f"{segment.get('start', 0):.1f}s - {segment.get('end', 0):.1f}s",
                    "severity": "Élevé"
                })
            
            if any(word in text.lower() for word in ["go-live", "production", "déploiement"]):
                risks.append({
                    "type": "Risque de déploiement",
                    "description": text,
                    "timestamp": f"{segment.get('start', 0):.1f}s - {segment.get('end', 0):.1f}s",
                    "severity": "Élevé"
                })
        
        return risks
    
    def _analyze_actions(self) -> List[Dict]:
        """Analyse les actions mentionnées dans l'audio."""
        action_segments = self._extract_segments_with_keywords(
            self.question_keywords["actions"]
        )
        
        actions = []
        for segment in action_segments:
            text = segment.get("text", "")
            
            # Détecter différents types d'actions
            if any(word in text.lower() for word in ["développer", "créer", "faire"]):
                actions.append({
                    "type": "Développement",
                    "description": text,
                    "timestamp": f"{segment.get('start', 0):.1f}s - {segment.get('end', 0):.1f}s",
                    "priority": "Haute"
                })
            
            if any(word in text.lower() for word in ["valider", "review", "vérifier"]):
                actions.append({
                    "type": "Validation",
                    "description": text,
                    "timestamp": f"{segment.get('start', 0):.1f}s - {segment.get('end', 0):.1f}s",
                    "priority": "Critique"
                })
        
        return actions
    
    def _analyze_team(self) -> List[Dict]:
        """Analyse les informations sur l'équipe."""
        team_segments = self._extract_segments_with_keywords(
            self.question_keywords["équipe"]
        )
        
        team_info = []
        for segment in team_segments:
            text = segment["text"]
            
            # Extraire les informations sur l'équipe
            if "150 applications" in text:
                team_info.append({
                    "type": "Portée",
                    "description": "Gestion de 150 applications",
                    "timestamp": f"{segment['start']:.1f}s - {segment['end']:.1f}s"
                })
            
            if "70 personnes" in text:
                team_info.append({
                    "type": "Taille équipe",
                    "description": "70 personnes dans l'équipe",
                    "timestamp": f"{segment['start']:.1f}s - {segment['end']:.1f}s"
                })
            
            if any(word in text.lower() for word in ["développeur", "architecte"]):
                team_info.append({
                    "type": "Composition",
                    "description": text,
                    "timestamp": f"{segment['start']:.1f}s - {segment['end']:.1f}s"
                })
        
        return team_info
    
    def answer_question(self, question: str) -> Dict:
        """
        Répond à une question basée sur l'analyse du contenu audio.
        
        Args:
            question (str): Question posée
            
        Returns:
            Dict: Réponse structurée
        """
        question_lower = question.lower()
        
        # Déterminer le type de question
        if any(word in question_lower for word in ["risque", "danger", "problème"]):
            return self._analyze_risks()
        elif any(word in question_lower for word in ["action", "faire", "développer"]):
            return self._analyze_actions()
        elif any(word in question_lower for word in ["équipe", "personne", "développeur"]):
            return self._analyze_team()
        elif any(word in question_lower for word in ["délai", "date", "timing"]):
            return self._analyze_timeline()
        else:
            # Analyse générale
            return self._general_analysis(question)
    
    def _analyze_timeline(self) -> List[Dict]:
        """Analyse les informations temporelles."""
        timeline_segments = self._extract_segments_with_keywords(
            self.question_keywords["délais"]
        )
        
        timeline = []
        for segment in timeline_segments:
            text = segment["text"]
            
            if "go-live" in text.lower():
                timeline.append({
                    "type": "Échéance critique",
                    "description": text,
                    "timestamp": f"{segment['start']:.1f}s - {segment['end']:.1f}s",
                    "importance": "Critique"
                })
        
        return timeline
    
    def _general_analysis(self, question: str) -> Dict:
        """Analyse générale basée sur la question."""
        # Recherche de mots-clés dans la question
        question_words = question.lower().split()
        
        # Trouver les segments les plus pertinents
        relevant_segments = []
        for segment in self.segments:
            text = segment.get("text", "").lower()
            relevance = 0
            
            for word in question_words:
                if len(word) > 3 and word in text:  # Éviter les mots trop courts
                    relevance += 1
            
            if relevance > 0:
                relevant_segments.append({
                    "text": segment.get("text", ""),
                    "start": segment.get("start", 0),
                    "end": segment.get("end", 0),
                    "relevance": relevance
                })
        
        # Trier par pertinence
        relevant_segments.sort(key=lambda x: x["relevance"], reverse=True)
        
        return {
            "type": "Analyse générale",
            "segments_pertinents": relevant_segments[:5],  # Top 5
            "question_originale": question
        }
    
    def format_answer(self, answer: Dict, question: str) -> str:
        """
        Formate la réponse pour l'affichage.
        
        Args:
            answer (Dict): Réponse structurée
            question (str): Question originale
            
        Returns:
            str: Réponse formatée
        """
        if isinstance(answer, list) and len(answer) > 0:
            if "type" in answer[0] and "risque" in answer[0]["type"].lower():
                return self._format_risks_answer(answer, question)
            elif "type" in answer[0] and "action" in answer[0]["type"].lower():
                return self._format_actions_answer(answer, question)
            else:
                return self._format_general_answer(answer, question)
        else:
            return f"❌ Aucune information pertinente trouvée pour la question : '{question}'"
    
    def _format_risks_answer(self, risks: List[Dict], question: str) -> str:
        """Formate la réponse sur les risques."""
        output = f"🔍 **Réponse à : \"{question}\"**\n\n"
        output += "En analysant le contenu de l'audio, voici les **risques identifiés** dans cette discussion :\n\n"
        
        for i, risk in enumerate(risks, 1):
            output += f"### **{i}. {risk.get('type', 'Risque non catégorisé')}**\n"
            output += f"- **Description** : {risk.get('description', 'Non disponible')}\n"
            output += f"- **Timestamp** : {risk.get('timestamp', 'Non disponible')}\n"
            if 'severity' in risk:
                output += f"- **Sévérité** : {risk['severity']}\n"
            output += "\n"
        
        return output
    
    def _format_actions_answer(self, actions: List[Dict], question: str) -> str:
        """Formate la réponse sur les actions."""
        output = f"🎯 **Réponse à : \"{question}\"**\n\n"
        output += "Voici les **actions identifiées** dans cette discussion :\n\n"
        
        for i, action in enumerate(actions, 1):
            output += f"### **{i}. {action.get('type', 'Action non catégorisée')}**\n"
            output += f"- **Description** : {action.get('description', 'Non disponible')}\n"
            output += f"- **Timestamp** : {action.get('timestamp', 'Non disponible')}\n"
            if 'priority' in action:
                output += f"- **Priorité** : {action['priority']}\n"
            output += "\n"
        
        return output
    
    def _format_general_answer(self, data: List[Dict], question: str) -> str:
        """Formate une réponse générale."""
        output = f"📋 **Réponse à : \"{question}\"**\n\n"
        output += "Voici les **informations pertinentes** trouvées :\n\n"
        
        for i, item in enumerate(data[:5], 1):  # Limiter à 5 résultats
            output += f"**{i}.** {item.get('text', 'Non disponible')}\n"
            output += f"   *({item.get('timestamp', 'Non disponible')})*\n\n"
        
        return output


def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(
        description="Analyseur de questions sur les transcriptions audio",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  %(prog)s transcription.json --question "Quels risques sont identifiés ?"
  %(prog)s transcription.json --question "Quelles actions doivent être prises ?"
  %(prog)s transcription.json --question "Qui fait partie de l'équipe ?"
        """
    )
    
    parser.add_argument("json_file", help="Fichier JSON de transcription")
    parser.add_argument("--question", "-q", required=True, help="Question à poser")
    parser.add_argument("--output", "-o", help="Fichier de sortie (optionnel)")
    
    args = parser.parse_args()
    
    try:
        # Initialiser l'analyseur
        analyzer = AudioQuestionAnalyzer(args.json_file)
        
        # Analyser la question
        answer = analyzer.answer_question(args.question)
        
        # Formater la réponse
        formatted_answer = analyzer.format_answer(answer, args.question)
        
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
