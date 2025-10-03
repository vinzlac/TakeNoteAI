#!/usr/bin/env python3
"""
Script pour générer automatiquement un fichier de mots-clés
à partir d'une transcription audio
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
import re
import argparse
from pathlib import Path
from collections import Counter
from typing import List, Dict, Set

# Import du gestionnaire de sortie
try:
    from output_manager import OutputManager
    OUTPUT_MANAGER = OutputManager()
except ImportError:
    print("⚠️  output_manager.py non trouvé, utilisation des chemins par défaut")
    OUTPUT_MANAGER = None

class KeywordGenerator:
    """Générateur de mots-clés à partir de transcriptions."""
    
    def __init__(self):
        """Initialise le générateur."""
        print("🔧 Initialisation du générateur de mots-clés...")
        
        # Mots français courants à exclure (avec variantes majuscules)
        self.common_french_words = {
            # Articles et déterminants
            "le", "la", "les", "de", "du", "des", "un", "une", "et", "ou", "mais", "donc", "car",
            "Le", "La", "Les", "De", "Du", "Des", "Un", "Une", "Et", "Ou", "Mais", "Donc", "Car",
            
            # Pronoms
            "je", "tu", "il", "elle", "nous", "vous", "ils", "elles", "ce", "cette", "ces",
            "Je", "Tu", "Il", "Elle", "Nous", "Vous", "Ils", "Elles", "Ce", "Cette", "Ces",
            
            # Mots interrogatifs
            "qui", "que", "quoi", "où", "quand", "comment", "pourquoi", "est-ce", "qu'est-ce",
            "Qui", "Que", "Quoi", "Où", "Quand", "Comment", "Pourquoi", "Est-ce", "Qu'est-ce",
            
            # Verbes courants
            "est", "sont", "être", "avoir", "faire", "aller", "venir", "voir", "dire", "savoir", "pouvoir", "vouloir",
            "Est", "Sont", "Être", "Avoir", "Faire", "Aller", "Venir", "Voir", "Dire", "Savoir", "Pouvoir", "Vouloir",
            
            # Prépositions et conjonctions
            "avec", "sans", "pour", "dans", "sur", "sous", "par", "vers", "entre", "chez", "après", "avant", "pendant",
            "Avec", "Sans", "Pour", "Dans", "Sur", "Sous", "Par", "Vers", "Entre", "Chez", "Après", "Avant", "Pendant",
            
            # Adverbes
            "très", "plus", "moins", "bien", "mal", "bon", "mauvais", "grand", "petit", "maintenant", "toujours", "jamais",
            "Très", "Plus", "Moins", "Bien", "Mal", "Bon", "Mauvais", "Grand", "Petit", "Maintenant", "Toujours", "Jamais",
            
            # Mots de liaison
            "donc", "alors", "puis", "ensuite", "enfin", "parce", "parce que", "puisque", "comme", "si", "quand",
            "Donc", "Alors", "Puis", "Ensuite", "Enfin", "Parce", "Parce que", "Puisque", "Comme", "Si", "Quand",
            
            # Mots de politesse
            "merci", "pardon", "excuse", "bonjour", "bonsoir", "salut", "au revoir",
            "Merci", "Pardon", "Excuse", "Bonjour", "Bonsoir", "Salut", "Au revoir",
            
            # Mots courants
            "oui", "non", "ok", "pas", "que", "qui", "comme", "si", "alors", "donc", "peut", "être",
            "Oui", "Non", "Ok", "Pas", "Que", "Qui", "Comme", "Si", "Alors", "Donc", "Peut", "Être",
            
            # Expressions courantes
            "voilà", "voici", "c'est", "il y a", "ça va", "c'est ça", "c'est bon", "c'est bien",
            "Voilà", "Voici", "C'est", "Il y a", "Ça va", "C'est ça", "C'est bon", "C'est bien",
            
            # Mots techniques génériques (à exclure car trop généraux)
            "système", "application", "projet", "équipe", "travail", "fonction", "rôle", "mission",
            "Système", "Application", "Projet", "Équipe", "Travail", "Fonction", "Rôle", "Mission"
        }
        
        print("✅ Générateur initialisé")
    
    def extract_keywords_from_transcription(self, text: str) -> List[str]:
        """
        Extrait les mots-clés d'une transcription.
        
        Args:
            text (str): Texte de la transcription
            
        Returns:
            List[str]: Liste des mots-clés extraits
        """
        print("🔍 Extraction des mots-clés de la transcription...")
        
        # Nettoyer le texte
        cleaned_text = self._clean_text(text)
        
        # Extraire les mots-clés potentiels
        keywords = []
        
        # 1. Acronymes (2-6 caractères en majuscules)
        acronyms = re.findall(r'\b[A-Z]{2,6}\b', cleaned_text)
        keywords.extend(acronyms)
        
        # 2. Noms propres (commençant par majuscule, 3+ caractères)
        proper_nouns = re.findall(r'\b[A-Z][a-z]{2,}\b', cleaned_text)
        # Filtrer les mots français courants
        proper_nouns = [noun for noun in proper_nouns if noun not in {
            "Le", "La", "Les", "De", "Du", "Des", "Un", "Une", "Et", "Ou", "Mais", 
            "Donc", "Car", "Pour", "Dans", "Sur", "Sous", "Par", "Vers", "Entre",
            "Avec", "Sans", "Avec", "Dans", "Pour", "Sur", "Sous", "Par", "Vers",
            "Très", "Plus", "Moins", "Bien", "Mal", "Bon", "Mauvais", "Grand", "Petit",
            "Nouveau", "Ancien", "Premier", "Dernier", "Autre", "Même", "Tout", "Tous",
            "Maintenant", "Toujours", "Jamais", "Souvent", "Parfois", "Rarement",
            "Beaucoup", "Peu", "Assez", "Trop", "Autant", "Tant", "Ici", "Là", "Partout",
            "Ailleurs", "Dedans", "Dehors", "Dessus", "Dessous", "Devant", "Derrière",
            "Haut", "Bas", "Droite", "Gauche", "Milieu", "Centre", "Bord", "Côté",
            "Partie", "Endroit", "Lieu", "Place", "Position", "Situation", "État",
            "Condition", "Manière", "Façon", "Moyen", "Méthode", "Technique", "Système",
            "Procédé", "Processus", "Opération", "Action", "Activité", "Travail",
            "Fonction", "Rôle", "Mission", "Tâche", "Objectif", "But", "Résultat",
            "Effet", "Conséquence", "Impact", "Influence", "Importance", "Valeur",
            "Prix", "Coût", "Budget", "Finance", "Argent", "Monnaie", "Temps",
            "Moment", "Instant", "Période", "Durée", "Longueur", "Largeur", "Hauteur",
            "Profondeur", "Taille", "Dimension", "Mesure", "Quantité", "Nombre",
            "Chiffre", "Pourcentage", "Ratio", "Proportion", "Fraction", "Total",
            "Somme", "Moyenne", "Maximum", "Minimum", "Limite", "Après", "Avant",
            "Pendant", "Depuis", "Jusque", "Vers", "Contre", "Selon", "Malgré",
            "Grâce", "Faute", "Cause", "Suite", "Résultat", "Conséquence", "Effet",
            "Impact", "Influence", "Changement", "Modification", "Amélioration",
            "Dégradation", "Évolution", "Progrès", "Régression", "Augmentation",
            "Diminution", "Croissance", "Décroissance", "Stabilité", "Variation",
            "Fluctuation", "Oscillation", "Tendance", "Orientation", "Direction",
            "Sens", "Côté", "Partie", "Section", "Zone", "Région", "Territoire",
            "Domaine", "Secteur", "Branche", "Spécialité", "Compétence", "Connaissance",
            "Savoir", "Expérience", "Pratique", "Théorie", "Concept", "Idée", "Notion",
            "Principe", "Règle", "Loi", "Norme", "Standard", "Critère", "Condition",
            "Exigence", "Besoin", "Demande", "Requête", "Proposition", "Suggestion",
            "Recommandation", "Conseil", "Avis", "Opinion", "Jugement", "Évaluation",
            "Appréciation", "Estimation", "Calcul", "Comptage", "Dénombrement",
            "Inventaire", "Liste", "Catalogue", "Répertoire", "Annuaire", "Index",
            "Table", "Tableau", "Graphique", "Diagramme", "Schéma", "Plan", "Carte",
            "Croquis", "Dessin", "Image", "Photo", "Illustration", "Figure", "Exemple",
            "Cas", "Situation", "Contexte", "Environnement", "Cadre", "Structure",
            "Organisation", "Arrangement", "Disposition", "Configuration", "Paramètre",
            "Réglage", "Ajustement", "Adaptation", "Modification", "Transformation",
            "Changement", "Évolution", "Développement", "Croissance", "Expansion",
            "Extension", "Augmentation", "Agrandissement", "Élargissement",
            "Approfondissement", "Enrichissement", "Amélioration", "Perfectionnement",
            "Optimisation", "Maximisation", "Minimisation", "Réduction", "Diminution",
            "Compression", "Condensation", "Concentration", "Centralisation",
            "Décentralisation", "Distribution", "Répartition", "Partage", "Division",
            "Séparation", "Découpage", "Fragmentation", "Décomposition", "Analyse",
            "Synthèse", "Combinaison", "Association", "Liaison", "Connexion", "Relation",
            "Lien", "Rapport", "Correspondance", "Équivalence", "Similarité",
            "Ressemblance", "Différence", "Distinction", "Opposition", "Contraste",
            "Comparaison", "Conflit", "Tension", "Harmonie", "Équilibre", "Stabilité",
            "Instabilité", "Variabilité", "Prévisibilité", "Imprévisibilité",
            "Certitude", "Incertitude", "Doute", "Confiance", "Méfiance", "Sécurité",
            "Insécurité", "Protection", "Vulnérabilité", "Risque", "Danger", "Menace",
            "Opportunité", "Chance"
        }]
        keywords.extend(proper_nouns)
        
        # 3. Versions (v1, v2, etc.)
        versions = re.findall(r'\bv\d+\b', cleaned_text.lower())
        keywords.extend([v.upper() for v in versions])
        
        # 4. Mots avec chiffres
        words_with_numbers = re.findall(r'\b[a-zA-Z]+\d+[a-zA-Z]*\b', cleaned_text)
        keywords.extend(words_with_numbers)
        
        # 5. Mots composés avec tirets (go-live, code-review, etc.)
        compound_words = re.findall(r'\b[a-zA-Z]+-[a-zA-Z]+\b', cleaned_text)
        keywords.extend(compound_words)
        
        # 6. CamelCase
        camel_case = re.findall(r'\b[A-Z][a-z]+[A-Z][a-z]*\b', cleaned_text)
        keywords.extend(camel_case)
        
        # Dédupliquer et filtrer
        unique_keywords = list(set(keywords))
        filtered_keywords = [kw for kw in unique_keywords if self._is_valid_keyword(kw)]
        
        # Trier par fréquence d'apparition
        keyword_counts = Counter([kw for kw in keywords if kw in filtered_keywords])
        sorted_keywords = sorted(filtered_keywords, key=lambda x: keyword_counts[x], reverse=True)
        
        print(f"✅ {len(sorted_keywords)} mots-clés extraits")
        return sorted_keywords
    
    def _clean_text(self, text: str) -> str:
        """Nettoie le texte pour l'analyse."""
        # Garder la casse originale
        text = re.sub(r'[^\w\s\-\.]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _is_valid_keyword(self, word: str) -> bool:
        """Vérifie si un mot est un mot-clé valide."""
        # Exclure les mots français courants (avec casse originale)
        if word in self.common_french_words:
            return False
        
        # Exclure les mots français courants (en minuscules)
        word_lower = word.lower()
        if word_lower in self.common_french_words:
            return False
        
        # Exclure les mots trop courts (sauf acronymes)
        if len(word) < 2:
            return False
        
        # Exclure les mots trop longs
        if len(word) > 20:
            return False
        
        # Exclure les mots avec trop de caractères spéciaux
        if len(re.findall(r'[^a-zA-Z0-9\-]', word)) > len(word) / 2:
            return False
        
        # Exclure les mots qui sont probablement des erreurs de transcription
        # (mots très courts qui ne sont pas des acronymes)
        if len(word) <= 3 and not re.match(r'^[A-Z]{2,3}$', word):
            # Exclure les pronoms et mots courants courts
            short_common_words = {"moi", "toi", "lui", "elle", "nous", "vous", "eux", "soi"}
            if word_lower in short_common_words:
                return False
        
        # Exclure les mots qui ressemblent à des erreurs de transcription
        # (mots avec des patterns étranges)
        if re.search(r'[aeiou]{3,}', word_lower):  # Trop de voyelles consécutives
            return False
        
        if re.search(r'[bcdfghjklmnpqrstvwxyz]{4,}', word_lower):  # Trop de consonnes consécutives
            return False
        
        return True
    
    def generate_keywords_file(self, keywords: List[str], output_file: str):
        """Génère un fichier de mots-clés."""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Mots-clés générés automatiquement à partir de la transcription\n")
            f.write("# Utilisez ce fichier avec: --keywords-file\n\n")
            
            for keyword in keywords:
                f.write(f"{keyword}\n")
        
        print(f"✅ Fichier de mots-clés généré: {output_file}")
    
    def print_summary(self, keywords: List[str]):
        """Affiche un résumé des mots-clés générés."""
        print(f"\n📊 Résumé des mots-clés générés:")
        print(f"   Total: {len(keywords)}")
        
        # Par catégorie
        acronyms = [kw for kw in keywords if re.match(r'^[A-Z]{2,6}$', kw)]
        proper_nouns = [kw for kw in keywords if kw[0].isupper() and len(kw) > 3]
        versions = [kw for kw in keywords if re.match(r'^V\d+$', kw)]
        compound_words = [kw for kw in keywords if '-' in kw]
        camel_case = [kw for kw in keywords if re.search(r'[A-Z][a-z]+[A-Z]', kw)]
        
        print(f"\n📋 Par catégorie:")
        print(f"   - Acronymes: {len(acronyms)}")
        print(f"   - Noms propres: {len(proper_nouns)}")
        print(f"   - Versions: {len(versions)}")
        print(f"   - Mots composés: {len(compound_words)}")
        print(f"   - CamelCase: {len(camel_case)}")
        
        # Top 20
        print(f"\n🏆 Top 20 des mots-clés générés:")
        for i, keyword in enumerate(keywords[:20], 1):
            print(f"   {i:2d}. {keyword}")


def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(
        description="Génère automatiquement un fichier de mots-clés à partir d'une transcription",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  %(prog)s fichier.json                           # Générer des mots-clés
  %(prog)s fichier.json --output mes_keywords.txt # Sortie personnalisée
  %(prog)s fichier.json --top 50                  # Limiter à 50 mots-clés
        """
    )
    
    parser.add_argument("input", help="Fichier JSON de transcription à analyser")
    parser.add_argument("--output", "-o", help="Fichier de sortie (défaut: keywords_generated.txt)")
    parser.add_argument("--top", type=int, help="Limiter à N mots-clés")
    
    args = parser.parse_args()
    
    try:
        # Vérifier le fichier d'entrée
        input_file = Path(args.input)
        if not input_file.exists():
            print(f"❌ Fichier non trouvé: {input_file}")
            return 1
        
        # Déterminer le fichier de sortie
        if args.output:
            output_file = args.output
        else:
            filename = f"keywords_generated_{input_file.stem}.txt"
            if OUTPUT_MANAGER:
                output_file = str(OUTPUT_MANAGER.get_keywords_path(filename))
            else:
                output_file = filename
        
        print(f"🔍 Analyse du fichier: {input_file}")
        print(f"📄 Sortie: {output_file}")
        
        # Charger le fichier JSON
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extraire le texte
        if 'transcription' in data:
            if isinstance(data['transcription'], dict):
                text = data['transcription'].get('text', '')
            else:
                text = str(data['transcription'])
        else:
            print("❌ Aucune transcription trouvée dans le fichier")
            return 1
        
        if not text:
            print("❌ Texte de transcription vide")
            return 1
        
        print(f"📝 Texte analysé: {len(text)} caractères")
        
        # Initialiser le générateur
        generator = KeywordGenerator()
        
        # Extraire les mots-clés
        keywords = generator.extract_keywords_from_transcription(text)
        
        if not keywords:
            print("✅ Aucun mot-clé détecté")
            return 0
        
        # Limiter les résultats si demandé
        if args.top:
            keywords = keywords[:args.top]
        
        # Afficher le résumé
        generator.print_summary(keywords)
        
        # Générer le fichier de mots-clés
        generator.generate_keywords_file(keywords, output_file)
        
        print(f"\n🎯 Utilisation:")
        print(f"   1. Vérifiez le fichier généré: {output_file}")
        print(f"   2. Utilisez avec: python advanced_rag_transcription_with_keywords.py audio.mp3 --keywords-file {output_file}")
        print(f"   3. Ou copiez les mots-clés: --keywords \"{', '.join(keywords[:10])}\"")
        
        return 0
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
